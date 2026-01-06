import os
import json

class HtmlLiveReporter:
    def __init__(self):
        self.desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        self.html_path = os.path.join(self.desktop, "GeekSquad_Dashboard_V40.html")
        self.js_path = os.path.join(self.desktop, "dashboard_data.js")
        self._bootstrapped = False

    def _ensure_files(self):
        if self._bootstrapped:
            return
        os.makedirs(self.desktop, exist_ok=True)

        # Create minimal HTML if missing (reads dashboard_data.js every second)
        if not os.path.exists(self.html_path):
            html = """<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>GeekSquad Dashboard</title>
  <style>
    body{font-family:Segoe UI,Arial,sans-serif;margin:20px;background:#0b0b0b;color:#fff}
    .card{border:1px solid #222;border-radius:10px;padding:14px;margin:10px 0;background:#111}
    .k{color:#8a8a8a}
    .v{font-size:22px}
    .row{display:flex;gap:10px;flex-wrap:wrap}
    .mini{min-width:220px;flex:1}
    progress{width:100%}
    a{color:#00ff9d}
  </style>
</head>
<body>
  <h2>Live Transfer Dashboard</h2>

  <div class="card">
    <div class="k">Status</div>
    <div id="run_status" class="v">IDLE</div>
  </div>

  <div class="row">
    <div class="card mini"><div class="k">Done Bytes</div><div id="done_bytes" class="v">0</div></div>
    <div class="card mini"><div class="k">Done Files</div><div id="done_files" class="v">0</div></div>
    <div class="card mini"><div class="k">Speed (MB/s)</div><div id="avg_speed" class="v">0</div></div>
  </div>

  <div class="card">
    <div class="k">Progress</div>
    <progress id="pct" value="0" max="100"></progress>
    <div id="pct_label" class="k">0%</div>
  </div>

  <script>
    function fmtBytes(n){
      n = Number(n||0);
      const units=['B','KB','MB','GB','TB'];
      let i=0;
      while(n>=1024 && i<units.length-1){ n/=1024; i++; }
      return n.toFixed(i===0?0:2)+' '+units[i];
    }
    window.updateDashboard = function(state){
      try{
        document.getElementById('run_status').textContent = state.run_status || state.status || 'IDLE';
        document.getElementById('done_bytes').textContent = fmtBytes(state.done_bytes || state.bytes_done || 0);
        document.getElementById('done_files').textContent = String(state.done_files || state.session_files_done || 0);
        const sp = Number(state.avg_speed || state.current_speed || 0);
        document.getElementById('avg_speed').textContent = sp.toFixed(2);
        const pct = Number(state.pct_data || 0);
        document.getElementById('pct').value = pct;
        document.getElementById('pct_label').textContent = pct.toFixed(1) + '%';
      }catch(e){}
    }
    function tick(){
      const s = document.createElement('script');
      s.src = 'dashboard_data.js?ts=' + Date.now();
      s.onload = () => { s.remove(); };
      s.onerror = () => { s.remove(); };
      document.body.appendChild(s);
    }
    setInterval(tick, 1000);
    tick();
  </script>
</body>
</html>"""
            with open(self.html_path, "w", encoding="utf-8") as f:
                f.write(html)

        if not os.path.exists(self.js_path):
            with open(self.js_path, "w", encoding="utf-8") as f:
                f.write("window.updateDashboard({});")

        self._bootstrapped = True

    def update_from_state(self, state_data):
        self._ensure_files()
        js = f"window.updateDashboard({json.dumps(state_data)});"
        try:
            temp = self.js_path + ".tmp"
            with open(temp, "w", encoding="utf-8") as f:
                f.write(js)
            os.replace(temp, self.js_path)
        except Exception:
            pass
