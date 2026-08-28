# Pipeline YT Radar — Agente Autônomo em Produção

> Caso de uso principal do hackathon: um agente que trabalha sozinho,
> todos os dias, sem supervisão — e entrega valor real.

## O Fluxo (6 estágios)

```
┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐
│ COLETA  │ → │ PROCESSA│ → │ ELEVA   │ → │ SINTETI │ → │ ENTREGA │ → │ APRENDE │
│ 19 can. │   │ transc. │   │ C-Level │   │ diário  │   │ TG+arq. │   │ skills  │
└─────────┘   └─────────┘   └─────────┘   └─────────┘   └─────────┘   └─────────┘
   08h/20h       LLM API      score 0-100     18h        Telegram      postmortem
```

### 1. COLETA — cron 08h/20h
- 19 canais de YouTube (IA, agentes, negócios, dev) em `canais.yml`
- Download de transcrição via YouTube Research Engine
- Guarda briefing bruto: título, canal, duração, URL, transcrição

### 2. PROCESSA — LLM provider-agnostic
- `yt_process.py` extrai **TESE CENTRAL**, **ARGUMENTOS**, **IMPLICAÇÃO**
- Provider configurável via env: `YT_PROVIDER=deepseek|gemini`
- Modelo configurável via env: `DEEPSEEK_MODEL` ou `GEMINI_MODEL`
- Pitfall tratado: modelos com reasoning (V4 Pro, Gemini 2.5) consomem
  tokens antes do output → boost automático de `max_tokens`

```bash
# DeepSeek (default)
python3 yt_process.py briefing.md

# Gemini (hackathon)
YT_PROVIDER=gemini python3 yt_process.py briefing.md
```

### 3. ELEVA — briefing C-Level
- Formato executivo: AVALIAÇÃO (score /100), IMPLICAÇÃO ESTRATÉGICA,
  OPORTUNIDADE, RISCO, AÇÃO (owner + prazo), CONEXÃO PORTFÓLIO
- Score decomposto: Tese 25 + Profundidade 25 + Conexão 20 + Audiência 15 + Ação 15

### 4. SINTETIZA — relatório diário (18h)
- Consolida todos os briefings elevados do dia
- SUMÁRIO + RANKING + TOP 3 INSIGHTS + PADRÕES + SUGESTÕES + MELHORIAS

### 5. ENTREGA
- Telegram (via relay HTTP :8099)
- Arquivo na Tríade (`~/triade/potencia/briefings/`) — versionado
- Sincronizado para os 4 nós

### 6. APRENDE
- Briefings com placeholder → detectados e re-processados
- Pitfalls documentados na skill `yt-radar`
- Diagnóstico de pipeline salvo quando algo degrada

## Resultados Reais (agosto 2026)

- **~10 briefings/dia**, 0 intervenção humana
- **30+ dias** rodando em produção
- **670 briefings** POTÊNCIA + **145** Bisturi arquivados
- **2 falhas de infra recuperadas** (VPS down, provider fallback) via postmortem
- **Adapters multi-provider** em produção (DeepSeek + Gemini)

## Código

- `yt_process.py` — processador de briefing (adapter LLM)
- `yt_radar_potencia.py` — coletor de canais
- `canais.yml` — lista de canais monitorados

> Este pipeline roda hoje, em produção, na infraestrutura DevOS. Não é demo.
> É o caso de uso que prova a tese: **agentes autônomos governados entregam
> valor em produção, 24/7.**
