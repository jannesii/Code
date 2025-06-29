#!/usr/bin/env python3
import os
import sys
import json
import base64
import logging
import threading
import signal
from time import sleep
from typing import Optional

import requests
import re
import socketio


logger = logging.getLogger(__name__)

class StatusReporter:
    """
    Handles HTTP login, Socket.IO connection, and periodic updates:
    sends status, temperature/humidity, and preview images when idle.
    """

    def __init__(
        self
    ) -> None:
        """
        session: TimelapseSession instance
        dht: DHT22Sensor instance for readings
        """
        self.rest = requests.Session()
        self._login()

        self.sio = socketio.Client(logger=True)
        self.sio.on('connect',    self.on_connect)
        self.sio.on('disconnect', self.on_disconnect)
        self.sio.on('error',      self.on_error)
        self.sio.on('timelapse_conf', self.on_config)
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
        login_url = "http://127.0.0.1:5555/login"

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
            "username": "admin",
            "password": "admin",
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
        #threading.Thread(target=self._image_loop, daemon=True).start()

    def _status_loop(self) -> None:
        """Periodically emit the current timelapse status."""
        while True:
            data = {
                "bed_temperature": 26.09,
                "nozzle_temperature": 26.22,
                "file_name": "",
                "percentage": 0,
                "elapsed_time": 3,
                "print_speed": 100,
                "current_layer": 6,
                "total_layers": 25,
                "nozzle_type": "STAINLESS_STEEL",
                "nozzle_diameter": 0.4,
                "print_error_code": 0,
                "status": "IDLE",
                "gcode_status": "FAILED"
            }
            try:
                self.sio.emit('status2v', data)
            except Exception:
                logger.exception("StatusReporter: error sending status")

            woke = self._status_event.wait(timeout=self.status_interval)
            if woke:
                logger.info(
                    "StatusReporter: status interval updated, resetting wait")
            self._status_event.clear()

    def _temphum_loop(self) -> None:
        """Periodically read DHT22 and emit temperature/humidity."""
        import random
        while True:
            try:
                data = {'temperature': random.uniform(20.0, 30.0), 'humidity': random.uniform(30.0, 70.0)}
                self.sio.emit('temphum', data)
            except Exception:
                logger.exception("StatusReporter: error sending temphum")

            woke = self._temphum_event.wait(timeout=self.temphum_interval)
            if woke:
                logger.info(
                    "StatusReporter: temphum interval updated, resetting wait")
            self._temphum_event.clear()


    def send_image(self, jpeg_bytes: bytes) -> None:
        """
        Emit a base64-encoded image over Socket.IO.
        """
        try:
            payload = base64.b64encode(jpeg_bytes).decode('utf-8')
            self.sio.emit('image', {'image': payload})
        except Exception:
            logger.exception("StatusReporter: error sending image")


    def on_connect(self) -> None:
        """Socket.IO connect handler."""
        logger.info("StatusReporter: connected to server")

    def on_disconnect(self) -> None:
        """Socket.IO disconnect handler."""
        logger.info("StatusReporter: disconnected from server")

    def on_error(self, data: dict) -> None:
        """Socket.IO error handler."""
        logger.error("StatusReporter: server error: %s", data)

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
        url = f"http://127.0.0.1:5555/api/timelapse_config"

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

def main():
    reporter = StatusReporter()
    reporter.connect()
    while True:
        sleep(1)  # Keep the main thread alive
        
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()