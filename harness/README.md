# Harness Engineering — o Núcleo Conceitual do DevOS

> Harness = Regras + Ferramentas + Memória + Skills + Verificações + Feedback Loops

## Por que "Harness"?

Um harness (arreio) é o que conecta potência a controle. Um cavalo sem arreio
é força bruta; com arreio, vira tração útil. Agentes de IA sem harness são
LLMs soltos — impressionantes, imprevisíveis, inúteis para produção.

O DevOS opera agentes **com harness completo**: cada nó sabe o que pode fazer,
como faz, e como verifica que fez certo.

## Os 6 Componentes

### 1. Regras
Todo agente carrega um **SOUL.md** (identidade + regras comportamentais) e
acessa regras compartilhadas da rede. Exemplos reais:
- "Memória é sagrada. Guarde, confie, use."
- "Veredito primeiro, ação depois. Sem enrolação."
- "Conferir a MESA antes de agir em território compartilhado."
- "Código exige aprovação explícita, salvo autonomia concedida."

**Por que importa:** regras tornam o comportamento *determinístico o suficiente*
para auditoria. Sem regras, cada resposta do agente é um sorteio.

### 2. Ferramentas
Cada agente tem um toolset explícito (terminal, arquivos, web, MCP, cron,
delegação). Ferramentas são **registradas com schema** — o LLM só usa o que
existe, e o sistema valida as chamadas.

**Por que importa:** ferramentas transformam o LLM de "conversador" em "operador".
Ele não sugere comandos — executa, dentro do que está autorizado.

### 3. Memória
Três camadas:
- **Memória persistente** (MEMORY.md + USER.md) — fatos duráveis injetados em todo turno
- **Fact store** — fatos com trust_score (0-1); score ≥0.7 é autoritativo
- **Session DB** — histórico completo pesquisável (FTS5)

**Por que importa:** sem memória, o agente esquece entre sessões. Com memória,
ele melhora com o tempo — o mesmo erro não se repete.

### 4. Skills
Procedimentos reutilizáveis salvos como SKILL.md (gatilhos + passos + pitfalls).
O agente carrega a skill certa no momento certo — conhecimento procedural
não fica na cabeça do LLM, fica versionado no sistema de arquivos.

**Exemplo real:** a skill `yt-radar` documenta o pipeline completo de YouTube,
com todos os pitfalls descobertos em 60+ dias de operação.

**Por que importa:** skills são o "aprendizado de longo prazo" do sistema.
Cada tarefa complexa resolvida vira uma skill — o próximo agente não
reaprende do zero.

### 5. Verificações
- Healthchecks automáticos (watchdog silencioso, alerta quando cai)
- Verificação de escrita (hash do arquivo escrito vs intenção)
- Testes (pytest no backend, 114/114 no whatsapp-ia)
- Segurança: fail2ban, honeypot, senhas base64, bancos em 127.0.0.1

**Por que importa:** sem verificação, o agente *diz* que fez — com verificação,
ele *prova*. O DevOS exige prova, não narrativa.

### 6. Feedback Loops
- **Reflection semanal** — o sistema analisa os próprios padrões de sessões e sugere melhorias
- **Postmortems** — falhas viram lições permanentes na Tríade
- **Poda de memória** — memória cheia é sanitizada automaticamente
- **Skills maintenance** — skills desatualizadas são corrigidas no uso

**Por que importa:** feedback é o que separa "automação" de "inteligência
operacional". O sistema melhora a si mesmo.

## Harness vs Chatbot

| | Chatbot | Harness DevOS |
|---|---|---|
| Saída | Texto | Ação verificada |
| Memória | Contexto da sessão | Persistente + fact store + KG |
| Aprendizado | Nenhum | Skills + reflection + postmortems |
| Controle | Prompt | Regras + ferramentas + verificação |
| Produção | Demo | 24/7 com observabilidade |
| Auditoria | Impossível | Determinístico o suficiente |

## Como isso escala

O harness não é um monólito — é um **padrão aplicado a cada nó**:
- POTÊNCIA: harness de orquestração (crons, decisões, pipeline)
- LUNA: harness de hub (gateway, comunicação, infra)
- BISTURI: harness de vigilância (radares, varreduras)
- CORTEX: harness de inferência (router, modelos, embeddings)

Cada nó é autônomo no seu domínio, governado pelas regras compartilhadas,
observável pela rede, e melhora com feedback. **Essa é a tese do Track 3.**
