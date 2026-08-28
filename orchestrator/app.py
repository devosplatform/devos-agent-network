"""
DevOS Orchestrator — Cloud Run service (hackathon Google All Things Agentic).

Prova de deploy: rede de agentes governada + observável em produção.
GET / serve um dashboard visual dark; endpoints JSON para a demo.

Endpoints:
  GET /            → dashboard HTML (visual)
  GET /health      → healthcheck (Cloud Run liveness)
  GET /agents      → JSON lista de agentes
  GET /mesa        → JSON governança
  GET /api/status  → JSON consolidado (para o dashboard)

Deploy: ./deploy.sh (após gcloud auth login + conta criada)
"""
import os
import uuid
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse

try:
    from google.cloud import firestore
    HAS_FIRESTORE = bool(os.environ.get("GOOGLE_CLOUD_PROJECT"))
except ImportError:
    HAS_FIRESTORE = False

app = FastAPI(
    title="DevOS Orchestrator",
    description="Rede de agentes autônomos governada e observável — Google All Things Agentic 2026",
    version="1.1.0",
)

NODES = [
    {"id": "potencia", "name": "POTÊNCIA", "emoji": "⚡", "role": "Orchestrator / Sub-CEO",
     "stack": "Python · FastAPI · crons · skills", "status": "online",
     "detail": "Pipeline YT Radar, 17 crons, decisões, memória + skills"},
    {"id": "luna", "name": "LUNA", "emoji": "🌙", "role": "Central Hub (VPS)",
     "stack": "Gateway · MCP · Docker · MQTT", "status": "online",
     "detail": "Telegram bot, MCP bridge, cloudflared tunnel, broker MQTT"},
    {"id": "bisturi", "name": "BISTURI", "emoji": "🔪", "role": "Watchdog / Scout",
     "stack": "Market radars · threat scans", "status": "online",
     "detail": "Radares de mercado, varreduras, postmortems, briefings"},
    {"id": "cortex", "name": "CORTEX", "emoji": "🧠", "role": "LLM Server",
     "stack": "Ollama · 5 models · router", "status": "online",
     "detail": "qwen32b, cortexq6, embeddings, router :9091"},
]

GOVERNANCE_RULES = [
    "Antes de agir em território compartilhado, conferir a MESA",
    "Decisões óbvias → executar. Decisões com trade-off → apresentar opções",
    "Código exige aprovação explícita, salvo autonomia concedida",
    "Ferramenta certa para o trabalho certo: script puro para determinístico, LLM para julgamento",
]

OBSERVABILITY = [
    "Watchdog silencioso — alerta só quando algo cai",
    "Briefing diário 07:00 — estado completo da rede",
    "Radar de coesão — detecta divergência entre nós",
    "Postmortems versionados — falhas viram lições",
]

FEEDBACK_LOOPS = [
    "Skills = procedimentos aprendidos",
    "Reflection semanal — o sistema analisa a si mesmo",
    "Poda de memória automática",
    "Provider-agnostic: DeepSeek + Gemini",
]

METRICS = [
    {"label": "Agentes em produção", "value": "4", "icon": "🖥️"},
    {"label": "Uptime", "value": "30+ dias", "icon": "⏱️"},
    {"label": "Briefings/dia", "value": "~10", "icon": "📊"},
    {"label": "Supervisão humana", "value": "0%", "icon": "🤖"},
]


def _db():
    if not HAS_FIRESTORE:
        return None
    return firestore.Client()


def _record_event(event: str, detail: str):
    doc = {
        "event": event,
        "detail": detail,
        "ts": datetime.now(timezone.utc).isoformat(),
        "id": uuid.uuid4().hex[:8],
    }
    db = _db()
    if db:
        db.collection("devos_events").add(doc)
    else:
        print(f"[event] {doc['ts']} {event}: {detail}")


@app.get("/", response_class=HTMLResponse)
def dashboard():
    _record_event("root", "GET / (dashboard)")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    nodes_html = ""
    for n in NODES:
        nodes_html += f"""
        <div class="node-card">
          <div class="node-header">
            <span class="node-emoji">{n['emoji']}</span>
            <div>
              <div class="node-name">{n['name']}</div>
              <div class="node-role">{n['role']}</div>
            </div>
            <span class="status-pill"><span class="dot"></span>{n['status']}</span>
          </div>
          <div class="node-detail">{n['detail']}</div>
          <div class="node-stack">{n['stack']}</div>
        </div>"""

    rules_html = "".join(f"<li>{r}</li>" for r in GOVERNANCE_RULES)
    obs_html = "".join(f"<li>{o}</li>" for o in OBSERVABILITY)
    loops_html = "".join(f"<li>{l}</li>" for l in FEEDBACK_LOOPS)
    metrics_html = "".join(f"""
        <div class="metric-card">
          <div class="metric-icon">{m['icon']}</div>
          <div class="metric-value">{m['value']}</div>
          <div class="metric-label">{m['label']}</div>
        </div>""" for m in METRICS)

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>DevOS — Autonomous Enterprise Agent Network</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ background: #020617; color: #e2e8f0; font-family: 'Segoe UI', system-ui, sans-serif; min-height: 100vh; }}
  .container {{ max-width: 1100px; margin: 0 auto; padding: 40px 24px; }}
  .hero {{ text-align: center; margin-bottom: 40px; }}
  .hero .badge {{ display: inline-block; background: rgba(34,211,238,0.1); border: 1px solid rgba(34,211,238,0.3); color: #22d3ee; padding: 6px 14px; border-radius: 20px; font-size: 12px; letter-spacing: 1px; margin-bottom: 16px; text-transform: uppercase; }}
  .hero h1 {{ font-size: 34px; font-weight: 700; color: #f8fafc; }}
  .hero h1 span {{ color: #22d3ee; }}
  .hero p {{ color: #94a3b8; margin-top: 10px; font-size: 15px; }}
  .hero .live {{ display: inline-flex; align-items: center; gap: 6px; margin-top: 14px; font-size: 13px; color: #34d399; }}
  .hero .live .pulse {{ width: 8px; height: 8px; background: #34d399; border-radius: 50%; animation: pulse 2s infinite; }}
  @keyframes pulse {{ 0%,100% {{ opacity: 1; }} 50% {{ opacity: 0.3; }} }}
  .metrics {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 40px; }}
  .metric-card {{ background: #0f172a; border: 1px solid #1e293b; border-radius: 12px; padding: 20px; text-align: center; }}
  .metric-icon {{ font-size: 24px; }}
  .metric-value {{ font-size: 28px; font-weight: 700; color: #22d3ee; margin: 6px 0 2px; }}
  .metric-label {{ font-size: 12px; color: #94a3b8; }}
  .section {{ margin-bottom: 32px; }}
  .section-title {{ font-size: 13px; letter-spacing: 2px; text-transform: uppercase; color: #64748b; margin-bottom: 16px; }}
  .section-title span {{ color: #22d3ee; }}
  .grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }}
  .node-card {{ background: #0f172a; border: 1px solid #1e293b; border-radius: 12px; padding: 20px; transition: border-color 0.2s; }}
  .node-card:hover {{ border-color: #22d3ee; }}
  .node-header {{ display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }}
  .node-emoji {{ font-size: 28px; }}
  .node-name {{ font-size: 16px; font-weight: 600; color: #f8fafc; }}
  .node-role {{ font-size: 12px; color: #94a3b8; }}
  .status-pill {{ margin-left: auto; display: inline-flex; align-items: center; gap: 6px; background: rgba(52,211,153,0.1); border: 1px solid rgba(52,211,153,0.3); color: #34d399; padding: 4px 10px; border-radius: 12px; font-size: 11px; text-transform: uppercase; }}
  .status-pill .dot {{ width: 6px; height: 6px; background: #34d399; border-radius: 50%; }}
  .node-detail {{ font-size: 13px; color: #cbd5e1; margin-bottom: 8px; }}
  .node-stack {{ font-size: 11px; color: #64748b; font-family: 'Cascadia Code', 'Consolas', monospace; }}
  .info-card {{ background: #0f172a; border: 1px solid #1e293b; border-radius: 12px; padding: 20px; }}
  .info-card h3 {{ font-size: 14px; color: #f8fafc; margin-bottom: 12px; }}
  .info-card ul {{ list-style: none; }}
  .info-card li {{ font-size: 13px; color: #94a3b8; padding: 6px 0; border-bottom: 1px solid #1e293b; }}
  .info-card li:last-child {{ border-bottom: none; }}
  .info-card li::before {{ content: '▹ '; color: #22d3ee; }}
  .footer {{ text-align: center; margin-top: 40px; padding-top: 24px; border-top: 1px solid #1e293b; color: #475569; font-size: 12px; }}
  .footer a {{ color: #22d3ee; text-decoration: none; }}
  .footer .ts {{ display: block; margin-top: 6px; font-family: 'Cascadia Code', monospace; font-size: 11px; }}
  @media (max-width: 700px) {{ .metrics {{ grid-template-columns: repeat(2, 1fr); }} .grid {{ grid-template-columns: 1fr; }} }}
</style>
</head>
<body>
<div class="container">
  <div class="hero">
    <div class="badge">Google All Things Agentic · Track 3 — Fortified Enterprise Suite</div>
    <h1>DEVOS <span>Agent Network</span></h1>
    <p>Harness = Regras + Ferramentas + Memória + Skills + Verificações + Feedback Loops</p>
    <div class="live"><span class="pulse"></span> Rede em produção — 24/7 · {now}</div>
  </div>

  <div class="metrics">{metrics_html}</div>

  <div class="section">
    <div class="section-title">🖥️ <span>AGENTES EM PRODUÇÃO</span></div>
    <div class="grid">{nodes_html}</div>
  </div>

  <div class="section">
    <div class="section-title">⚙️ <span>GOVERNANÇA &amp; OBSERVABILIDADE</span></div>
    <div class="grid">
      <div class="info-card">
        <h3>Regras de Governança</h3>
        <ul>{rules_html}</ul>
      </div>
      <div class="info-card">
        <h3>Observabilidade</h3>
        <ul>{obs_html}</ul>
      </div>
      <div class="info-card">
        <h3>Feedback Loops</h3>
        <ul>{loops_html}</ul>
      </div>
      <div class="info-card">
        <h3>APIs Públicas</h3>
        <ul>
          <li><code>/health</code> — healthcheck</li>
          <li><code>/agents</code> — agentes (JSON)</li>
          <li><code>/mesa</code> — governança (JSON)</li>
          <li><code>/api/status</code> — consolidado (JSON)</li>
        </ul>
      </div>
    </div>
  </div>

  <div class="footer">
    <a href="https://github.com/devosplatform/devos-agent-network">github.com/devosplatform/devos-agent-network</a>
    <span class="ts">slice público · sem credenciais · Google All Things Agentic 2026</span>
  </div>
</div>
</body>
</html>"""


@app.get("/health")
def health():
    return JSONResponse({"status": "ok", "ts": datetime.now(timezone.utc).isoformat()})


@app.get("/agents")
def agents():
    _record_event("agents", "GET /agents")
    return JSONResponse({"agents": NODES})


@app.get("/mesa")
def mesa():
    _record_event("mesa", "GET /mesa")
    return JSONResponse({
        "governance_rules": GOVERNANCE_RULES,
        "observability": OBSERVABILITY,
        "feedback_loops": FEEDBACK_LOOPS,
    })


@app.get("/api/status")
def status():
    _record_event("status", "GET /api/status")
    return JSONResponse({
        "service": "DevOS Orchestrator",
        "version": "1.1.0",
        "nodes": NODES,
        "metrics": METRICS,
        "ts": datetime.now(timezone.utc).isoformat(),
    })


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
