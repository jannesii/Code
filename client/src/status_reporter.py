#!/usr/bin/env python3
import os
import sys
import json
import base64
import logging
import threading
import signal
from typing import Optional

import requests
import re
import socketio

from .dht import DHT22Sensor
from .timelapse_session import TimelapseSession
from .bambu_handler import BambuHandler

logger = logging.getLogger(__name__)

class StatusReporter:
    """
    Handles HTTP login, Socket.IO connection, and periodic updates:
    sends status, temperature/humidity, and preview images when idle.
    """

    def __init__(
        self,
        session: TimelapseSession,
        dht: DHT22Sensor,
        logger: logging.Logger
    ) -> None:
        """
        session: TimelapseSession instance
        dht: DHT22Sensor instance for readings
        """
        self.session = session
        self.dht = dht
        self.printer = BambuHandler()

        self.rest = requests.Session()
        self._login()

        self.sio = socketio.Client(logger=True)
        self.sio.on('connect',    self.on_connect)
        self.sio.on('disconnect', self.on_disconnect)
        self.sio.on('error',      self.on_error)
        self.sio.on('timelapse_conf', self.on_config)
        self.sio.on('printerActionRedirect', self.on_printer_action)
        self.status_interval = None
        self.temphum_interval = None
        self.image_interval = None

        # events to interrupt waits
        self._status_event = threading.Event()
        self._temphum_event = threading.Event()
        self._image_event = threading.Event()

        conf = self.get_config()
        if conf:
            self.on_config(conf)

        pid_file = '/tmp/server.pid'
        try:
            with open(pid_file) as f:
                self.pid = int(f.read().strip())
        except Exception as e:
            logging.error(f"Could not read PID file {pid_file}: {e}")

    def _login(self) -> None:
        """Authenticate via HTTP to obtain session cookies (with CSRF)."""
        login_url = f"{os.getenv('SERVER')}/login"

        # 1) GET login page to set cookie and grab CSRF token
        resp_get = self.rest.get(login_url)
        logger.info("Fetched login page (%s) for CSRF token", login_url)
        if resp_get.status_code != 200:
            logger.error("Failed to GET login page: %s",
                              resp_get.status_code)
            sys.exit(1)

        # 2) Extract CSRF token from hidden input
        m = re.search(r'name="csrf_token" value="([^"]+)"', resp_get.text)
        if not m:
            logger.error("CSRF token not found on login page")
            sys.exit(1)
        token = m.group(1)
        logger.debug("Using CSRF token: %s", token)

        # 3) POST credentials + CSRF
        payload = {
            "username": os.getenv("RASPI_USERNAME"),
            "password": os.getenv("RASPI_PASSWORD"),
            "csrf_token": token,
        }
        headers = {"Referer": login_url}
        logger.debug("Posting to %s with Referer header", login_url)
        resp_post = self.rest.post(
            login_url,
            data=payload,
            headers=headers
        )
        if resp_post.status_code != 200 or "Invalid credentials" in resp_post.text:
            logger.error(
                "StatusReporter: login failed: %s", resp_post.text)
            sys.exit(1)

        logger.info("StatusReporter: logged in")

    def connect(self) -> None:
        """
        Establish Socket.IO connection and start background loops
        for status, temphum, and preview image streaming.
        """
        cookies = "; ".join(
            f"{k}={v}" for k, v in self.rest.cookies.get_dict().items())
        self.sio.connect(
            os.getenv("SERVER"),
            headers={"Cookie": cookies},
            transports=["websocket", "polling"]
        )
        threading.Thread(target=self._status_loop, daemon=True).start()
        threading.Thread(target=self._temphum_loop, daemon=True).start()
        threading.Thread(target=self._image_loop, daemon=True).start()

        # hook timelapse capture to immediate send
        self.session.image_callback = self.send_image

    def _status_loop(self) -> None:
        """Periodically emit the current timelapse status."""
        while True:
            try:
                self.sio.emit('status', self.printer.to_dict())
            except Exception:
                logger.exception("StatusReporter: error sending status")

            woke = self._status_event.wait(timeout=self.status_interval)
            if woke:
                logger.info(
                    "StatusReporter: status interval updated, resetting wait")
            self._status_event.clear()

    def _temphum_loop(self) -> None:
        """Periodically read DHT22 and emit temperature/humidity."""
        while True:
            try:
                data = self.dht.read()
                self.sio.emit('temphum', data)
            except Exception:
                logger.exception("StatusReporter: error sending temphum")

            woke = self._temphum_event.wait(timeout=self.temphum_interval)
            if woke:
                logger.info(
                    "StatusReporter: temphum interval updated, resetting wait")
            self._temphum_event.clear()

    def _image_loop(self) -> None:
        """
        Stream preview images only when timelapse is not active.
        """
        while True:
            try:
                if not self.session.active:
                    threading.Thread(
                        target=self.session._blink_red_led, args=(True, 0.2)).start()
                    jpeg = self.session.camera.capture_frame()
                    if jpeg:
                        with open("/tmp/preview.jpg", "wb") as f:
                            f.write(jpeg)
                        self.send_signal()
                        # self.send_image(jpeg)
            except Exception:
                logger.exception("StatusReporter: error in image loop")

            woke = self._image_event.wait(timeout=self.image_interval)
            if woke:
                logger.info(
                    "StatusReporter: image interval updated, resetting wait")
            self._image_event.clear()

    def send_image(self, jpeg_bytes: bytes) -> None:
        """
        Emit a base64-encoded image over Socket.IO.
        """
        try:
            payload = base64.b64encode(jpeg_bytes).decode('utf-8')
            self.sio.emit('image', {'image': payload})
        except Exception:
            logger.exception("StatusReporter: error sending image")

    def send_signal(self) -> None:
        try:
            os.kill(self.pid, signal.SIGUSR1)
            logging.info(f"Sent SIGUSR1 to server process {self.pid}")
        except Exception as e:
            logging.error(f"Error sending SIGUSR1: {e}")

    def on_connect(self) -> None:
        """Socket.IO connect handler."""
        logger.info("StatusReporter: connected to server")

    def on_disconnect(self) -> None:
        """Socket.IO disconnect handler."""
        logger.info("StatusReporter: disconnected from server")

    def on_error(self, data: dict) -> None:
        """Socket.IO error handler."""
        logger.error("StatusReporter: server error: %s", data)

    def on_printer_action(self, data: dict) -> None:
        action = data.get("action")
        if action not in ['pause', 'resume', 'stop', 'home']:
            logger.error("StatusReporter: invalid printer action: %s", action)
            return
        if action == 'pause':
            result = self.printer.pause_print()
        elif action == 'resume':
            result = self.printer.resume_print()
        elif action == 'stop':
            result = self.printer.stop_print()
        elif action == 'home':
            result = self.printer.home_printer()
        
        logger.info("Printer action %s result: %s", action, result)
        self.sio.emit('printerAction', {'action': action, 'result': result})

    def on_config(self, data: dict) -> None:
        """
        Handle configuration updates.
        Updates intervals and wakes sleeping loops.
        """
        changed = []
        try:
            # collect which intervals actually changed
            if self.image_interval != data['image_delay']:
                self.image_interval = data['image_delay']
                changed.append("_image_event")
            if self.status_interval != data['status_delay']:
                self.status_interval = data['status_delay']
                changed.append("_status_event")
            if self.temphum_interval != data['temphum_delay']:
                self.temphum_interval = data['temphum_delay']
                changed.append("_temphum_event")

            logger.info("StatusReporter: config updated %r, changed: %s",
                             data, changed)
            # wake up any sleeping loops so they pick up the new value immediately
            if "_status_event" in changed:
                self._status_event.set()
            if "_temphum_event" in changed:
                self._temphum_event.set()
            if "_image_event" in changed:
                self._image_event.set()

        except KeyError as e:
            logger.warning("StatusReporter: invalid config key %s", e)

    def get_config(self) -> Optional[dict]:
        """
        Return the current configuration settings.
        """
        url = f"{os.getenv('SERVER')}/api/timelapse_config"

        resp = self.rest.get(url)
        if resp.status_code == 200:
            try:
                data = resp.json()
                logger.info("StatusReporter: config retrieved %r", data)
                return data
            except json.JSONDecodeError:
                logger.error(
                    "StatusReporter: error decoding JSON response")
        else:
            logger.error(
                "StatusReporter: failed to retrieve config, status code: %d", resp.status_code)
            return None
        return None
