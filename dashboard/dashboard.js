(function(){
const lerp = (a,b,t)=>a+(b-a)*t;
const clamp = (x,min,max)=>Math.max(min,Math.min(max,x));

const el = (id)=>document.getElementById(id);
const statusEl = el("status");
const speedEl = el("speed");
const filesEl = el("files");
const threadsEl = el("threads");
const doneBytesEl = el("doneBytes");
const pctEl = el("pct");
const batchesEl = el("batches");
const fillEl = el("fill");
const dotsEl = el("dots");

let target = { speed:0, files:0, threads:0, doneBytes:0, pct:0, batchesDone:0, batchesTotal:0, status:"IDLE", streams:[] };
let view   = { speed:0, files:0, threads:0, doneBytes:0, pct:0 };

function fmtBytes(n){
    n = Number(n||0);
    const u = ["B","KB","MB","GB","TB"];
    let i=0;
    while(n>=1024 && i<u.length-1){ n/=1024; i++; }
    return (i===0? n.toFixed(0) : n.toFixed(2)) + " " + u[i];
}

async function readSnapshot(){
    try{
    const r = await fetch("../state_snapshot.json?ts="+Date.now(), {cache:"no-store"});
    if(!r.ok) return;
    const s = await r.json();
    target.status = s.run_status || s.status || "IDLE";
    target.speed = Number(s.speed_mb_s || s.avg_speed || 0);
    target.files = Number(s.done_files || s.session_files_done || 0);
    target.threads = Number(s.active_threads || 0);
    target.doneBytes = Number(s.done_bytes || s.bytes_done || 0);
    target.pct = Number(s.pct || s.pct_data || 0);
    target.batchesDone = Number(s.batches_done || 0);
    target.batchesTotal = Number(s.batches_total || 0);
    target.streams = Array.isArray(s.streams) ? s.streams : [];
    }catch(e){}
}

function renderDots(){
    const n = Math.max(8, Math.min(16, target.streams.length || 8));
    dotsEl.innerHTML = "";
    for(let i=0;i<n;i++){
    const d = document.createElement("div");
    d.className = "dot";
    const st = target.streams[i]?.status;
    if(st === "active") d.classList.add("on");
    if(st === "error") d.classList.add("err");
    dotsEl.appendChild(d);
    }
}

function tick(){
    // Smooth values even if snapshot updates every 15s
    const t = 0.12;
    view.speed = lerp(view.speed, target.speed, t);
    view.files = lerp(view.files, target.files, t);
    view.threads = lerp(view.threads, target.threads, t);
    view.doneBytes = lerp(view.doneBytes, target.doneBytes, t);
    view.pct = lerp(view.pct, target.pct, t);

    statusEl.textContent = target.status;
    speedEl.textContent = view.speed.toFixed(2) + " MB/s";
    filesEl.textContent = Math.round(view.files).toString();
    threadsEl.textContent = Math.round(view.threads).toString();
    doneBytesEl.textContent = fmtBytes(view.doneBytes);
    pctEl.textContent = view.pct.toFixed(1) + "%";
    batchesEl.textContent = (target.batchesDone|0) + "/" + (target.batchesTotal|0);

    fillEl.style.width = clamp(view.pct,0,100).toFixed(1) + "%";
    requestAnimationFrame(tick);
}

// snapshot poll (slow changing)
setInterval(readSnapshot, 1200);
setInterval(renderDots, 1500);
readSnapshot();
renderDots();
requestAnimationFrame(tick);
})();
