#!/usr/bin/env python3
"""
yt_process.py — Processa briefing YT via DeepSeek API (REASONING tier).
Preenche TESE CENTRAL, CONEXÃO DevOS, e gera versão ELEVADA.
Uso: python3 yt_process.py <briefing.md>
"""
import sys, json, urllib.request, re, os
from pathlib import Path
from datetime import datetime, timezone, time

# DeepSeek API (OpenAI-compatible) — DEFAULT
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"
# Modelo configurável via env (DEEPSEEK_MODEL). Default: v4-flash (nome oficial atual).
# deepseek-v4-pro (0813) tem modo reasoning — consome tokens antes do output.
MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-flash")

# Provider alternativo: GEMINI (YT_PROVIDER=gemini) — hackathon Google All Things Agentic.
# Usa endpoint OpenAI-compatible do Gemini (mesma interface, zero mudança no pipeline).
# Pitfall: Gemini 2.5 consome tokens de reasoning antes do output (igual DeepSeek Pro) —
# o boost de max_tokens abaixo cobre isso.
PROVIDER = os.environ.get("YT_PROVIDER", "deepseek")
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

# V4 Pro gasta ~metade do max_tokens em reasoning antes do conteúdo final.
# Boost automático para não truncar o output real.
PRO_MAX_TOKENS_BOOST = 3

def _load_api_key() -> str:
    """Carrega a chave do provider ativo (DEEPSEEK ou GOOGLE) do ambiente ou .env."""
    env_name = "GOOGLE_API_KEY" if PROVIDER == "gemini" else "DEEPSEEK_API_KEY"
    key = os.environ.get(env_name, "")
    if key:
        return key
    # Fallback: ler do .env do Hermes
    env_files = [Path.home() / ".hermes" / ".env", Path.home() / ".env"]
    for f in env_files:
        if f.exists():
            for line in f.read_text().split('\n'):
                if line.startswith(f'{env_name}='):
                    return line.split('=', 1)[1].strip().strip('"').strip("'")
    return ""

def _api_url() -> str:
    return GEMINI_URL if PROVIDER == "gemini" else DEEPSEEK_URL

def _active_model() -> str:
    return GEMINI_MODEL if PROVIDER == "gemini" else MODEL

DEEPSEEK_KEY = _load_api_key()

def _check_peak_hours() -> bool:
    """
    Verifica se está em horário de pico da DeepSeek API.
    Peak UTC: 01:00-04:00 e 06:00-10:00 — preço 2x.
    Retorna True se estiver no pico.
    """
    now = datetime.now(timezone.utc).time()
    peak1 = time(1, 0), time(4, 0)
    peak2 = time(6, 0), time(10, 0)
    in_peak = (peak1[0] <= now < peak1[1]) or (peak2[0] <= now < peak2[1])
    if in_peak:
        print(f"   ⚠️  PEAK HOURS DeepSeek — custo 2x (UTC {now.hour:02d}:{now.minute:02d})")
        print(f"   Peak windows: UTC 01:00-04:00 e 06:00-10:00")
        print(f"   BRT: 22:00-01:00 e 03:00-07:00")
    return in_peak

def call_deepseek(system_prompt: str, user_prompt: str, max_tokens: int = 2000) -> str:
    """Chama o LLM do provider ativo (DeepSeek ou Gemini via endpoint OpenAI-compatible)."""
    if not DEEPSEEK_KEY:
        return f"ERRO: chave do provider {PROVIDER} não configurada"

    active_model = _active_model()
    api_url = _api_url()

    # Boost para modelos com reasoning (DeepSeek V4 Pro e Gemini 2.5): consome tokens antes do output
    if PROVIDER == "gemini" or "pro" in active_model:
        max_tokens = max_tokens * PRO_MAX_TOKENS_BOOST

    body = json.dumps({
        "model": active_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.7,
        "max_tokens": max_tokens,
        "stream": False
    }).encode()
    
    req = urllib.request.Request(api_url, data=body, headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_KEY}"
    })
    
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read())
            return result["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"ERRO {PROVIDER} API: {e}"

def extract_metadata(text: str) -> dict:
    """Extrai metadados do briefing bruto."""
    meta = {}
    title_match = re.search(r'^# (.+)$', text, re.MULTILINE)
    meta['title'] = title_match.group(1) if title_match else "Desconhecido"
    
    canal_match = re.search(r'\*\*Canal:\*\* (.+)', text)
    meta['channel'] = canal_match.group(1) if canal_match else "?"
    
    dur_match = re.search(r'\*\*Duração:\*\* (.+)', text)
    meta['duration'] = dur_match.group(1) if dur_match else "?"
    
    url_match = re.search(r'\*\*URL:\*\* (.+)', text)
    meta['url'] = url_match.group(1) if url_match else "?"
    
    # Extract transcript
    trans_match = re.search(r'## Transcrição\n\n(.+)', text, re.DOTALL)
    meta['transcript'] = trans_match.group(1).strip() if trans_match else ""
    meta['transcript_len'] = len(meta['transcript'])
    
    # Extract video ID from URL
    vid_match = re.search(r'(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})', meta['url'])
    meta['video_id'] = vid_match.group(1) if vid_match else "?"
    
    return meta

def generate_tese(meta: dict) -> str:
    """Gera TESE CENTRAL do vídeo."""
    transcript = meta['transcript'][:8000]
    
    system = "Você é um analista estratégico sênior. Extraia a tese central de vídeos técnicos. Responda em português, tom direto e cirúrgico."
    
    user = f"""Analise esta transcrição de vídeo e extraia:

1. TESE CENTRAL: (2-3 frases — qual é a ideia-força? Qual o argumento principal?)
2. ARGUMENTOS: (3-4 bullet points com os argumentos de suporte)
3. IMPLICAÇÃO: (1 frase — o que isso significa pra quem trabalha com tecnologia?)

Vídeo: {meta['title']}
Canal: {meta['channel']}
Duração: {meta['duration']}

Transcrição:
{transcript}

Responda em markdown, direto, sem introdução como "Aqui está a análise"."""
    
    return call_deepseek(system, user, 1000)

def generate_conexao(meta: dict, tese: str) -> str:
    """Gera CONEXÃO DevOS."""
    transcript = meta['transcript'][:6000]
    
    system = """Você é o Sub CEO do DevOS, uma "Harness Engineering Platform" — plataforma de inteligência operacional com agentes IA.

Contexto DevOS:
- Stack: Python/FastAPI, PHP/Laravel, Angular, Docker, MQTT
- Arquitetura: Tríade multi-nó (POTÊNCIA+LUNA+BISTURI) + CORTEX Router + Knowledge Graph
- Agentes: Hermes Agent com SOUL.md, skills, memory, MCP, cron
- Portfólio: rjdcore (API 31 endpoints), mercadinho (delivery), whatsapp-ia (bot vendas), servico-pro, associacaocaju
- Diferencial: Harness = regras + ferramentas + memória + skills + verificações + feedback loops
- Posicionamento: "AI-Native Operational Intelligence", validado Stanford/Tsinghua 6X performance

Responda em português, tom direto e executivo."""
    
    user = f"""Com base na transcrição e tese abaixo, identifique conexões estratégicas com o DevOS.

Vídeo: {meta['title']} | Canal: {meta['channel']}

TESE CENTRAL:
{tese[:600]}

Trecho da transcrição:
{transcript[:5000]}

Responda com:
1. CONEXÃO DIRETA: (1 parágrafo — como isso se conecta ao que o DevOS já faz? Valida? Contradiz? Amplia?)
2. OPORTUNIDADE: (1-2 parágrafos — que produto/feature/serviço isso sugere para o portfólio DevOS?)
3. RISCO/AMEAÇA: (1 frase — isso ameaça algo do ecossistema DevOS?)
4. AÇÃO CONCRETA: (1-2 bullets — o que fazer em 24-48h?)"""
    
    return call_deepseek(system, user, 1200)

def generate_elevated(meta: dict, tese: str, conexao: str) -> str:
    """Gera versão ELEVADA (formato C-Level)."""
    
    system = """Você é o CORTEX do DevOS. Transforme análises de vídeo em briefings C-Level no formato exato abaixo. 
Responda em português, tom executivo, sem introdução."""
    
    user = f"""Gere um briefing executivo neste formato EXATO:

```
# 📡 [TÍTULO DO VÍDEO] — ELEVADO
> POTÊNCIA (Sub CEO) · {datetime.now().strftime('%d/%m/%Y')} · Original: [VIDEO_ID] · [CANAL] · [DURAÇÃO]

## 📊 AVALIAÇÃO: XX/100 🟢🟡🔴
Tese: X/25 | Profundidade: X/25 | Conexão DevOS: X/20 — [justificativa 1 linha] | Audiência: X/15 | Ação: X/15

## 🧠 IMPLICAÇÃO ESTRATÉGICA
(1 parágrafo denso — o que isso significa para o posicionamento DevOS?)

## 💰 OPORTUNIDADE
(2-3 bullets com oportunidades concretas: features, produtos, serviços, posicionamento)

## ⚠️ RISCO
(1 frase — maior risco ou ameaça)

## 🎬 AÇÃO
| Ação | Owner | Prazo |
|------|-------|-------|
| [ação 1] | POTÊNCIA | [prazo] |
| [ação 2] | POTÊNCIA | [prazo] |

## 🔗 CONEXÃO PORTFÓLIO
- **projeto1**: [1 linha de conexão]
- **projeto2**: [1 linha de conexão]

## ⏱ TIMELINE
🟢 Agora: [ação imediata]
🟡 Esta semana: [ação curto prazo]
```

DADOS DO VÍDEO:
- Título: {meta['title']}
- Canal: {meta['channel']}
- Duração: {meta['duration']}
- Vídeo ID: {meta['video_id']}

ANÁLISE:
- TESE: {tese[:800]}
- CONEXÃO: {conexao[:800]}

Gere APENAS o briefing no formato acima. Não adicione introdução nem comentários."""
    
    return call_deepseek(system, user, 1500)

def main():
    if len(sys.argv) < 2:
        print("Uso: python3 yt_process.py <briefing.md>")
        sys.exit(1)
    
    if not DEEPSEEK_KEY:
        print("ERRO: DEEPSEEK_API_KEY não definida no ambiente")
        sys.exit(1)
    
    briefing_path = Path(sys.argv[1])
    if not briefing_path.exists():
        print(f"ERRO: {briefing_path} não encontrado")
        sys.exit(1)
    
    text = briefing_path.read_text()
    meta = extract_metadata(text)

    # ⏰ Guard: horário de pico DeepSeek (SÓ quando provider é deepseek)
    if PROVIDER == "deepseek" and _check_peak_hours():
        print("   🚨 ABORTANDO: Horário de pico DeepSeek — custo 2x.")
        print("   Use --force-peak para ignorar este guard.")
        if "--force-peak" not in sys.argv:
            sys.exit(1)
        print("   ⚠️  Forçando execução no pico (custo 2x)...\n")

    print(f"📺 {meta['title'][:80]}")
    print(f"   Canal: {meta['channel']} | Duração: {meta['duration']}")
    print(f"   Transcrição: {meta['transcript_len']:,} chars")
    print(f"   API: {PROVIDER.upper()} ({_active_model()})")
    
    if meta['transcript_len'] < 100:
        print("   ⚠️ Transcrição muito curta — pulando processamento")
        sys.exit(1)
    
    # 1. TESE CENTRAL
    print(f"\n[1/3] Gerando TESE CENTRAL via {PROVIDER.upper()}...")
    tese = generate_tese(meta)
    print(f"   {'✅' if not tese.startswith('ERRO') else '❌'} {len(tese)} chars")
    if tese.startswith('ERRO'):
        print(f"   {tese}")
        sys.exit(1)
    
    # 2. CONEXÃO DevOS
    print("[2/3] Gerando CONEXÃO DevOS...")
    conexao = generate_conexao(meta, tese)
    print(f"   {'✅' if not conexao.startswith('ERRO') else '❌'} {len(conexao)} chars")
    if conexao.startswith('ERRO'):
        print(f"   {conexao}")
        sys.exit(1)
    
    # 3. ELEVATED
    print("[3/3] Gerando versão ELEVADA...")
    elevated = generate_elevated(meta, tese, conexao)
    print(f"   {'✅' if not elevated.startswith('ERRO') else '❌'} {len(elevated)} chars")
    
    # Atualizar briefing original
    updated = text.replace(
        "`[Preencher via CORTEX Router — Qwen 32B]`",
        tese
    )
    updated = updated.replace(
        "`[Preencher via CORTEX Router]`",
        conexao
    )
    briefing_path.write_text(updated)
    print(f"\n📝 Briefing atualizado: {briefing_path}")
    
    # Salvar versão elevada
    elevated_dir = briefing_path.parent / "elevated"
    elevated_dir.mkdir(exist_ok=True)
    elevated_path = elevated_dir / f"{briefing_path.stem}-elevated.md"
    elevated_path.write_text(elevated)
    print(f"📡 Versão elevada: {elevated_path}")
    
    # Summary
    print(f"\n{'='*50}")
    print("TESE CENTRAL:")
    print(tese[:300])
    print(f"\n{'='*50}")
    print("CONEXÃO DevOS:")
    print(conexao[:300])

if __name__ == '__main__':
    main()
