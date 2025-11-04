function log(msg){
  const el = document.getElementById('log');
  const ts = new Date().toLocaleTimeString();
  el.innerHTML += `[${ts}] ${msg}<br>`;
  el.scrollTop = el.scrollHeight;
}

async function refreshPorts(){
  try{
    const ports = await window.pywebview.api.get_serial_ports();
    const sel = document.getElementById('ports');
    sel.innerHTML = '';
    ports.forEach(p => {
      const opt = document.createElement('option'); opt.value = p; opt.text = p; sel.appendChild(opt);
    });
    log('Ports updated');
  }catch(e){ log('Error refreshing ports: ' + e); }
}

async function connect(){
  const sel = document.getElementById('ports');
  const port = sel.value;
  if(!port){ alert('Select a port first'); return; }
  const res = await window.pywebview.api.connect(port);
  if(res && res.connected){
    document.getElementById('status').textContent = '● Connected';
    document.getElementById('status').className = 'status connected';
    document.getElementById('connect').disabled = true;
    document.getElementById('disconnect').disabled = false;
    log('Connected to ' + port);
    updateStatus();
  } else {
    log('Failed to connect');
    alert('Failed to connect');
  }
}

async function disconnect(){
  await window.pywebview.api.disconnect();
  document.getElementById('status').textContent = '● Disconnected';
  document.getElementById('status').className = 'status disconnected';
  document.getElementById('connect').disabled = false;
  document.getElementById('disconnect').disabled = true;
  log('Disconnected');
}

async function send(){
  const input = document.getElementById('cmd-input');
  const text = input.value.trim();
  if(!text) return;
  await window.pywebview.api.send_command(text);
  log('Command sent: ' + text);
  input.value = '';
  updateStatus();
}

async function quick(e){
  const cmd = e.target.dataset.cmd;
  if(!cmd) return;
  await window.pywebview.api.send_command(cmd);
  log('Quick command: ' + cmd);
  updateStatus();
}

async function startVoice(){
  await window.pywebview.api.start_voice();
  document.getElementById('voice-start').disabled = true;
  document.getElementById('voice-stop').disabled = false;
  log('Voice started');
}
async function stopVoice(){
  await window.pywebview.api.stop_voice();
  document.getElementById('voice-start').disabled = false;
  document.getElementById('voice-stop').disabled = true;
  log('Voice stopped');
}

async function updateStatus(){
  try{
    const s = await window.pywebview.api.get_status();
    document.getElementById('armed').textContent = s.armed ? 'Yes' : 'No';
    document.getElementById('flying').textContent = s.flying ? 'Yes' : 'No';
    document.getElementById('last').textContent = s.last_command || 'None';
  }catch(e){ console.warn(e); }
}

// Wire up UI
window.addEventListener('DOMContentLoaded', () => {
  document.getElementById('refresh').addEventListener('click', refreshPorts);
  document.getElementById('connect').addEventListener('click', connect);
  document.getElementById('disconnect').addEventListener('click', disconnect);
  document.getElementById('send').addEventListener('click', send);
  document.getElementById('voice-start').addEventListener('click', startVoice);
  document.getElementById('voice-stop').addEventListener('click', stopVoice);

  document.querySelectorAll('.quick-btn').forEach(b => b.addEventListener('click', quick));

  refreshPorts();
  setInterval(updateStatus, 1500);
});