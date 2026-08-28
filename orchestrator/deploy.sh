#!/bin/bash
# deploy.sh — Deploy do DevOS Orchestrator no Google Cloud Run.
# PRÉ-REQUISITOS:
#   1. Conta GCP criada (https://cloud.google.com/)
#   2. gcloud instalado:  sudo apt install google-cloud-cli  (ou curl instalador oficial)
#   3. Autenticado:       gcloud auth login
#
# USO:
#   ./deploy.sh <project-id> [regiao]
#   Ex: ./deploy.sh devos-hackathon-2026 us-central1

set -euo pipefail

PROJECT_ID="${1:?Usage: ./deploy.sh <project-id> [regiao]}"
REGION="${2:-us-central1}"
SERVICE="devos-orchestrator"
IMAGE="gcr.io/${PROJECT_ID}/${SERVICE}"

echo "🚀 Deploy DevOS Orchestrator em ${REGION} (projeto ${PROJECT_ID})"

# 1. Garantir que o projeto existe / está selecionado
gcloud config set project "${PROJECT_ID}"
echo "✅ Projeto selecionado: ${PROJECT_ID}"

# 2. Habilitar APIs necessárias
echo "📦 Habilitando APIs (Cloud Run, Firestore, Artifact Registry)..."
gcloud services enable run.googleapis.com firestore.googleapis.com artifactregistry.googleapis.com
echo "✅ APIs habilitadas"

# 3. Criar Firestore (primeira vez)
if ! gcloud firestore databases list --project="${PROJECT_ID}" 2>/dev/null | grep -q "${PROJECT_ID}"; then
  echo "🗄 Criando Firestore em ${REGION}..."
  gcloud firestore databases create --location="${REGION}" --project="${PROJECT_ID}" \
    || echo "⚠️ Firestore pode já existir ou a API ainda está propagando — continuando"
fi
echo "✅ Firestore pronto"

# 4. Build da imagem
echo "🐳 Buildando imagem ${IMAGE}..."
gcloud builds submit --tag "${IMAGE}"
echo "✅ Imagem publicada"

# 5. Deploy no Cloud Run (público, sem autenticação para a demo)
echo "☁️ Deploy ${SERVICE} no Cloud Run..."
gcloud run deploy "${SERVICE}" \
  --image "${IMAGE}" \
  --platform managed \
  --region "${REGION}" \
  --allow-unauthenticated \
  --memory 256Mi \
  --min-instances 0

# 6. URL final
URL=$(gcloud run services describe "${SERVICE}" --region "${REGION}" --format='value(status.url)')
echo ""
echo "🎉 ORQUESTRADOR NO AR: ${URL}"
echo "   Health: ${URL}/health"
echo "   Agents: ${URL}/agents"
echo "   Mesa:   ${URL}/mesa"
