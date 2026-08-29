# DevOS — Autonomous Enterprise Agent Network

> **Hackathon Google "All Things Agentic" — Track 3 (Fortified Enterprise Suite)**
> Uma rede de agentes autônomos, governada, observável e em produção — operando 24/7.

**Status:** Submissão pública (slice) — agosto 2026
**Stack:** Python · FastAPI · Docker · MQTT · Ollama · Google Gemini · DeepSeek · Cloud Run (GCP)

---

## O Problema

Chatbots respondem. Agentes **entregam**. A diferença é um sistema de produção:

- Um agente isolado é um demo. Uma **rede de agentes governada** é um produto.
- A maioria das demos de "agentes" morre na falta de: **memória durável, governança, observabilidade e feedback loops**.
- Empresas querem agentes que trabalhem *sozinhos* — coleta → processamento → decisão → entrega — **sem supervisão humana**, e que **melhorem com o tempo**.

## A Solução: Harness Engineering

O DevOS é uma **plataforma de inteligência operacional** construída sobre o conceito de *Harness*:

```
Harness = Regras + Ferramentas + Memória + Skills + Verificações + Feedback Loops
```

Cada agente opera dentro de um harness que define **o que pode fazer, como faz, e como sabe que fez certo**.

### Os 4 Nós (em produção, 24/7)

| Nó | Papel | O que roda |
|----|-------|------------|
| **POTÊNCIA** | Orquestrador / Sub-CEO | Pipeline YT Radar, crons, handoffs, decisões |
| **LUNA** | Hub central (VPS) | Gateway, MCP bridge, Telegram, Docker, MQTT broker |
| **BISTURI** | Vigilância / PAD | Radares de mercado, varreduras, postmortems |
| **CORTEX** | Cérebro LLM local | Ollama: 5 modelos (qwen32b, cortexq6, embed), router |

### Governança

- **MESA.md** — status ao vivo dos nós, decisões pendentes, coordenação cross-agente
- **Tríade** — protocolo de comunicação entre agentes (git + MQTT + relay)
- **Regras compartilhadas** — cada agente conhece os limites e o território dos outros

### Observabilidade

- Healthchecks automáticos (watchdog silencioso, alerta quando cai)
- Briefing diário 07:00 com estado de tudo
- Radar de coesão (detecta divergência entre nós)
- Logs de deploy versionados

### Feedback Loops

- Skills são **procedimentos aprendidos** — cada tarefa complexa vira conhecimento reutilizável
- Reflection semanal — o sistema analisa os próprios padrões e se ajusta
- Postmortems — falhas viram lições permanentes

## O Caso: Pipeline YT Radar (autônomo em produção)

Um agente que **trabalha sozinho** todos os dias:

```
1. COLETA   → 19 canais de YouTube monitorados (cron 08h/20h)
2. PROCESSO → transcrição → extração de tese via LLM (DeepSeek/Gemini)
3. ELEVA    → briefing C-Level com score, risco, ação e owner
4. SINETIZA → relatório diário consolidado (18h)
5. ENTREGA  → Telegram + Tríade + arquivamento
6. APRENDE  → erros viram correções no pipeline (skills + postmortems)
```

**Resultado:** ~10 briefings/dia, 0 intervenção humana, 30+ dias rodando.

## Arquitetura (visão de alto nível)

```
┌─────────────────────────────────────────────────────┐
│                 DEVOS — 4 NÓS EM PRODUÇÃO            │
│                                                     │
│  ⚡ POTÊNCIA (WSL)      🌙 LUNA (VPS)               │
│  ├─ Orquestrador       ├─ Gateway Telegram         │
│  ├─ YT Radar pipeline  ├─ MCP Bridge (interna)     │
│  ├─ Crons (17 jobs)    ├─ Docker + MQTT (interna)  │
│  └─ Handoffs/Decisões  └─ cloudflared tunnel       │
│                                                     │
│  🔪 BISTURI (PAD)      🧠 CORTEX (LLM Server)      │
│  ├─ Radares mercado    ├─ Ollama (interna)         │
│  ├─ Varreduras         ├─ 5 modelos (qwen32b etc)  │
│  └─ Postmortems        └─ Router de modelos        │
│                                                     │
│  └── Comunicação: SSH + MQTT + git + relay outboxes │
└─────────────────────────────────────────────────────┘
```

## Diferenciais vs Demos de Laboratório

1. **Produção real** — 24/7 por 30+ dias, não uma demo de 4 minutos
2. **Multi-nó heterogêneo** — WSL + VPS + PAD + servidor LLM dedicado
3. **Memória persistente** — Knowledge Graph, fact_store, memórias, MESA
4. **Governança viva** — regras compartilhadas, não apenas RBAC estático
5. **Adaptação contínua** — skills aprendidas, reflection, postmortems
6. **Zero vendor lock-in** — DeepSeek hoje, Gemini amanhã (adapter provider)

## Repositório — Estrutura

```
public-slice/
├── architecture/          ← diagrama + explicação dos 4 nós
├── harness/               ← o conceito Harness (regras+memória+skills+verificações)
├── pipeline/              ← caso YT Radar (coleta→entrega→aprendizado)
└── docs/                  ← governança, observabilidade, decisões
```

> ⚠️ Este é um **slice público** do DevOS. Credenciais, infraestrutura interna,
> estratégia comercial e dados de clientes foram removidos propositalmente.

## Começando

```bash
# 1. Clone
git clone <repo-url> devos-hackathon && cd devos-hackathon

# 2. Pipeline YT Radar (caso de uso)
cd pipeline
pip install -r requirements.txt
# Configurar LLM: DeepSeek (DEEPSEEK_API_KEY) ou Gemini (GOOGLE_API_KEY)
python3 yt_process.py <briefing.md>
```

## Licença

MIT — código de demonstração para fins de hackathon.
