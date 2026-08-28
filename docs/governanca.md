# Governança & Observabilidade — Como 4 Agentes Vivem Juntos

> O que torna o DevOS uma **rede**, não uma coleção de scripts:
> governança compartilhada, observabilidade e comunicação estruturada.

## MESA.md — a Mesa da Tríade

Um arquivo versionado (`~/triade/shared/MESA.md`) que funciona como **estado
ao vivo da rede**:

```
✅ Status dos Nós (POTÊNCIA, LUNA, BISTURI, CORTEX)
📊 Últimas 24h (o que cada agente entregou)
🎯 Decisões Pendentes (o que precisa de dono + prazo)
⏱ Próximos Passos (checklist executável)
```

**Regra de ouro:** antes de agir em território compartilhado, o agente
**confere a MESA**. Isso elimina colisão entre agentes trabalhando no mesmo
sistema.

## Protocolo de Comunicação

| Canal | Uso | Latência |
|-------|-----|----------|
| SSH + MCP | Comando síncrono entre nós | ~1-2s |
| git (triade/) | Documentos, decisões, atas | ~5min (push automático) |
| MQTT :2883 | Eventos/pub-sub | ~100ms |
| Relay outboxes | Handoffs assíncronos (CORTEX /tmp/) | ~2s |
| Telegram | Entrega para humano | instantâneo |

## Observabilidade

### Watchdog silencioso
Script que roda a cada 30min. **Silencioso quando tudo OK** — só fala quando
algo cai. Zero ruído, alerta imediato.

### Briefing diário 07:00
Cada manhã: estado dos nós + memória + crons + atividade YT. O humano (CEO)
abre a sessão sabendo exatamente o que aconteceu.

### Radar de Coesão
Detecta divergência entre nós (ex: dois agentes editando o mesmo arquivo,
skills duplicadas, memórias conflitantes). Alerta quando a rede se desalinha.

### Postmortems
Toda falha vira um documento: sintoma → causa raiz → correção → prevenção.
A rede **não esquece** — ela aprende com os próprios erros.

## Decisões & Autonomia

- **Decisões óbvias** → o agente executa direto
- **Decisões com trade-off** → apresenta opções ao humano (verde/amarelo/vermelho)
- **Território compartilhado** → conferir MESA antes
- **Código** → aprovação explícita, salvo autonomia concedida

Esse modelo é o que permite **autonomia com responsabilidade** — o oposto
de um script solto ou de um chatbot que só conversa.
