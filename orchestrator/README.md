# DevOS Orchestrator — Cloud Run

Prova de deploy do hackathon: a rede de agentes exposta como serviço público
no Google Cloud Run, com estado persistido no Firestore.

## Endpoints

| Endpoint | Função |
|----------|--------|
| `GET /` | Dashboard visual da rede (HTML dark) |
| `GET /health` | Healthcheck (liveness do Cloud Run) |
| `GET /agents` | Lista os 4 agentes (JSON) |
| `GET /mesa` | Regras de governança + observabilidade (JSON) |
| `GET /api/status` | Estado consolidado (JSON) |

## Deploy (pré-requisitos: conta GCP + gcloud autenticado)

```bash
./deploy.sh <project-id> us-central1
```

O script:
1. Seleciona o projeto
2. Habilita APIs (Cloud Run, Firestore, Artifact Registry, Cloud Build)
3. Cria o Firestore (primeira vez)
4. Builda a imagem via Cloud Build
5. Deploy no Cloud Run (público, `--allow-unauthenticated`)
6. Imprime a URL final

## Teste local (sem deploy)

```bash
pip install fastapi uvicorn
python3 -m uvicorn app:app --port 8080
# ou via TestClient:
python3 -c "
from fastapi.testclient import TestClient
import app
c = TestClient(app.app)
print(c.get('/health').json())
"
```

> Este serviço roda hoje em produção (Cloud Run). O código é o mesmo do
> dashboard exibido na demo — slice público, sem credenciais.
