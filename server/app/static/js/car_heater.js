console.log('🚗 car_heater.js loaded');

function fmtTs(ts) {
  if (!ts) return '—';
  try {
    const d = new Date(ts);
    return d.toLocaleString(undefined, {
      year: 'numeric', month: '2-digit', day: '2-digit',
      hour: '2-digit', minute: '2-digit', second: '2-digit'
    });
  } catch {
    return '—';
  }
}

function fmtNum(v, unit = '', digits = 1) {
  if (v === null || v === undefined) return '—';
  const n = Number(v);
  if (!Number.isFinite(n)) return '—';
  return `${n.toFixed(digits)}${unit}`;
}

function applyTempPill(el, temp) {
  if (!el) return;
  const n = Number(temp);
  el.classList.remove('pill-warm', 'pill-hot', 'pill-muted');
  if (!Number.isFinite(n)) {
    el.classList.add('pill-muted');
    return;
  }
  if (n >= 40) el.classList.add('pill-hot');
  else if (n >= 30) el.classList.add('pill-warm');
  else el.classList.add('pill-muted');
}

function updateStatusUI(status) {
  const heaterPill = document.getElementById('heaterStatePill');
  const powerPill = document.getElementById('powerPill');
  const ambientPill = document.getElementById('ambientPill');
  const deviceTempPill = document.getElementById('deviceTempPill');
  const voltagePill = document.getElementById('voltagePill');
  const currentPill = document.getElementById('currentPill');

  const tsEl = document.getElementById('tsValue');
  const instantEl = document.getElementById('instantPowerValue');
  const energyLastEl = document.getElementById('energyLastMinValue');
  const energyTotalEl = document.getElementById('energyTotalValue');
  const deviceTempEl = document.getElementById('deviceTempValue');
  const ambientTempEl = document.getElementById('ambientTempValue');
  const sourceEl = document.getElementById('sourceValue');

  if (!status) {
    if (heaterPill) {
      heaterPill.classList.remove('pill-on', 'pill-off');
      heaterPill.classList.add('pill-unknown');
      heaterPill.textContent = 'Unknown';
    }
    return;
  }

  const isOn = !!status.is_heater_on;
  const instantW = status.instant_power_w;
  const ambient = status.ambient_temp;
  const devTemp = status.device_temp_c ?? status.device_temp_f;

  if (heaterPill) {
    heaterPill.classList.remove('pill-on', 'pill-off', 'pill-unknown');
    heaterPill.classList.add(isOn ? 'pill-on' : 'pill-off');
    heaterPill.textContent = isOn ? 'Heater ON' : 'Heater OFF';
  }
  if (powerPill) {
    powerPill.textContent = `Power: ${fmtNum(instantW, ' W', 1)}`;
  }
  if (ambientPill) {
    ambientPill.textContent = `Ambient: ${fmtNum(ambient, ' °C', 1)}`;
  }
  if (deviceTempPill) {
    deviceTempPill.textContent = `Device: ${fmtNum(status.device_temp_c, ' °C', 1)}`;
    applyTempPill(deviceTempPill, status.device_temp_c);
  }
  if (voltagePill) {
    voltagePill.textContent = `U: ${fmtNum(status.voltage_v, ' V', 1)}`;
  }
  if (currentPill) {
    currentPill.textContent = `I: ${fmtNum(status.current_a, ' A', 2)}`;
  }

  if (tsEl) tsEl.textContent = fmtTs(status.timestamp);
  if (instantEl) instantEl.textContent = fmtNum(instantW, ' W', 1);
  if (energyLastEl) {
    const v = status.energy_last_min_wh;
    energyLastEl.textContent = (v === null || v === undefined) ? '—' : `${v} Wh (last min)`;
  }
  if (energyTotalEl) {
    const v = status.energy_total_wh;
    energyTotalEl.textContent = (v === null || v === undefined) ? '—' : `${v} Wh`;
  }
  if (deviceTempEl) deviceTempEl.textContent = fmtNum(status.device_temp_c, ' °C', 1);
  if (ambientTempEl) ambientTempEl.textContent = fmtNum(ambient, ' °C', 1);
  if (sourceEl) sourceEl.textContent = status.source || '—';
}

const COMMAND_ACTIONS = {
  turn_on: 'Turn ON',
  turn_off: 'Turn OFF',
  get_logs: 'Get logs',
  esp_restart: 'Restart ESP',
  shelly_restart: 'Restart Shelly',
};

function updateSingleCommandStatus(action, status) {
  const el = document.getElementById(`cmdStatus_${action}`);
  if (!el) return;

  el.classList.remove('status-queued', 'status-sent', 'status-success', 'status-error');

  if (!status) {
    el.textContent = '';
    el.style.display = 'none';
    return;
  }

  let text = '';
  let cls = '';
  switch (status) {
    case 'queued':
      text = 'Queued';
      cls = 'status-queued';
      break;
    case 'sent':
      text = 'Sent to ESP';
      cls = 'status-sent';
      break;
    case 'success':
      text = 'Success';
      cls = 'status-sent';
      break;
    case 'failed':
      text = 'Failed';
      cls = 'status-error';
      break;
    default:
      text = String(status);
      break;
  }

  el.textContent = text;
  if (cls) el.classList.add(cls);
  el.style.display = '';
}

function updateCommandStatusUI(commandStatus) {
  const actions = Object.keys(COMMAND_ACTIONS);
  if (!commandStatus) {
    actions.forEach(action => updateSingleCommandStatus(action, null));
    return;
  }
  actions.forEach(action => {
    updateSingleCommandStatus(action, commandStatus[action]);
  });
}

function setQueueStatus(mode, text) {
  const el = document.getElementById('queueStatus');
  if (!el) return;
  el.classList.remove('queue-idle', 'queue-pending', 'queue-sent');
  if (mode) el.classList.add(mode);
  el.textContent = text;
}

function queueCommand(action) {
  const payload = { action: action };
  setQueueStatus('queue-pending', 'Action queued…');
  updateSingleCommandStatus(action, 'queued');

  // Prefer Socket.IO for low latency; fall back to HTTP if needed.
  try {
    if (window.socket) {
      window.socket.emit('car_heater_control', payload);
      return;
    }
  } catch (err) {
    console.warn('Socket emit failed, falling back to HTTP:', err);
  }

  // HTTP fallback endpoint
  fetch('/api/car_heater/queue', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Requested-With': 'XMLHttpRequest',
    },
    body: JSON.stringify(payload),
  }).then(resp => {
    if (!resp.ok) throw new Error('HTTP ' + resp.status);
    return resp.json();
  }).then(data => {
    console.log('Queue HTTP result:', data);
    setQueueStatus('queue-pending', 'Action queued');
  }).catch(err => {
    console.error('Queue HTTP error:', err);
    setQueueStatus('queue-idle', 'Failed to queue action');
  });
}

document.addEventListener('DOMContentLoaded', () => {
  // Initial status from server-rendered context
  if (window.CAR_HEATER_LAST_STATUS) {
    updateStatusUI(window.CAR_HEATER_LAST_STATUS);
  }

  if (window.CAR_HEATER_CMD_STATUS) {
    updateCommandStatusUI(window.CAR_HEATER_CMD_STATUS);
  }

  const btnOn = document.getElementById('btnTurnOn');
  const btnOff = document.getElementById('btnTurnOff');
  const btnLogs = document.getElementById('btnGetLogs');
  const btnEspRestart = document.getElementById('btnEspRestart');
  const btnShellyRestart = document.getElementById('btnShellyRestart');

  if (btnOn) btnOn.addEventListener('click', () => queueCommand('turn_on'));
  if (btnOff) btnOff.addEventListener('click', () => queueCommand('turn_off'));
  if (btnLogs) btnLogs.addEventListener('click', () => queueCommand('get_logs'));
  if (btnEspRestart) {
    btnEspRestart.addEventListener('click', () => {
      if (window.confirm('Restart ESP? This will reboot the microcontroller.')) {
        queueCommand('esp_restart');
      }
    });
  }
  if (btnShellyRestart) {
    btnShellyRestart.addEventListener('click', () => {
      if (window.confirm('Restart Shelly? This will reboot the relay device.')) {
        queueCommand('shelly_restart');
      }
    });
  }

  if (window.socket) {
    window.socket.on('car_heater_status', data => {
      console.log('📡 car_heater_status:', data);
      if (data && data.status) {
        updateStatusUI(data.status);
      } else {
        updateStatusUI(data);
      }
      if (data && (data.command_status || data.commandStatus)) {
        updateCommandStatusUI(data.command_status || data.commandStatus);
      }
      // When a new status arrives, assume commands were delivered
      setQueueStatus('queue-sent', 'Last command sent to car');
    });

    window.socket.on('car_heater_action_result', data => {
      console.log('📡 car_heater_action_result:', data);
      if (!data) return;
      const ok = data.ok !== false;
      setQueueStatus(ok ? 'queue-sent' : 'queue-idle',
                     ok ? 'Last action sent' : 'Action failed');
      if (ok && data.action) {
        updateSingleCommandStatus(data.action, 'queued');
      }
    });
  }
});
