#!/bin/bash

# CodeSage - Google Cloud Run Deployment Script
# This script automates the deployment process

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   CodeSage - Cloud Run Deployment         ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

# Configuration
PROJECT_ID="codesage"
SERVICE_NAME="codesage"
REGION="us-central1"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ Error: gcloud CLI is not installed${NC}"
    echo "Install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

echo -e "${GREEN}✅ gcloud CLI found${NC}"

# Check if logged in
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
    echo -e "${YELLOW}⚠️  Not logged in to gcloud${NC}"
    echo "Running: gcloud auth login"
    gcloud auth login
fi

echo -e "${GREEN}✅ Authenticated with gcloud${NC}"

# Set project
echo -e "${BLUE}📍 Setting project to: ${PROJECT_ID}${NC}"
gcloud config set project ${PROJECT_ID}

# Prompt for Gemini API key
echo ""
echo -e "${YELLOW}🔑 Gemini API Key Configuration${NC}"
echo "You can get your API key from: https://aistudio.google.com/app/apikey"
echo ""
read -p "Enter your Gemini API key (or press Enter to use existing secret): " GEMINI_API_KEY

# Check if required files exist
echo ""
echo -e "${BLUE}📋 Checking required files...${NC}"

if [ ! -f "Dockerfile" ]; then
    echo -e "${RED}❌ Dockerfile not found${NC}"
    exit 1
fi

if [ ! -f ".dockerignore" ]; then
    echo -e "${YELLOW}⚠️  .dockerignore not found (optional but recommended)${NC}"
fi

if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}❌ requirements.txt not found${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Required files found${NC}"

# Enable required APIs
echo ""
echo -e "${BLUE}🔧 Enabling required APIs...${NC}"
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
echo -e "${GREEN}✅ APIs enabled${NC}"

# Store API key as secret if provided
if [ ! -z "$GEMINI_API_KEY" ]; then
    echo ""
    echo -e "${BLUE}🔐 Storing API key in Secret Manager...${NC}"
    
    # Check if secret exists
    if gcloud secrets describe gemini-api-key &> /dev/null; then
        echo "Secret already exists. Adding new version..."
        echo -n "$GEMINI_API_KEY" | gcloud secrets versions add gemini-api-key --data-file=-
    else
        echo "Creating new secret..."
        echo -n "$GEMINI_API_KEY" | gcloud secrets create gemini-api-key --data-file=-
    fi
    
    # Grant Cloud Run access to secret
    PROJECT_NUMBER=$(gcloud projects describe ${PROJECT_ID} --format="value(projectNumber)")
    gcloud secrets add-iam-policy-binding gemini-api-key \
        --member=serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com \
        --role=roles/secretmanager.secretAccessor \
        --quiet || true
    
    echo -e "${GREEN}✅ API key stored securely${NC}"
fi

# Build and deploy
echo ""
echo -e "${BLUE}🚀 Deploying to Cloud Run...${NC}"
echo "This may take a few minutes..."
echo ""

gcloud run deploy ${SERVICE_NAME} \
    --source . \
    --region ${REGION} \
    --platform managed \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 3600 \
    --max-instances 10 \
    --set-secrets GEMINI_API_KEY=gemini-api-key:latest

# Get the service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region ${REGION} --format="value(status.url)")

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     Deployment Successful! 🎉              ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}📍 Your service is now live at:${NC}"
echo -e "${GREEN}${SERVICE_URL}${NC}"
echo ""
echo -e "${BLUE}📊 Useful commands:${NC}"
echo "  View logs:    gcloud run services logs read ${SERVICE_NAME} --region ${REGION}"
echo "  Update:       ./deploy.sh"
echo "  Delete:       gcloud run services delete ${SERVICE_NAME} --region ${REGION}"
echo ""
echo -e "${BLUE}💡 Next steps:${NC}"
echo "  1. Open ${SERVICE_URL} in your browser"
echo "  2. Test the refactoring functionality"
echo "  3. Monitor logs for any issues"
echo "  4. Set up custom domain (optional)"
echo ""
echo -e "${GREEN}Happy coding! 🚀${NC}"