#!/bin/bash

# Railway Programmatic Deployment Script
echo "🚂 Starting Railway deployment..."

# Install Railway CLI if not present
if ! command -v railway &> /dev/null; then
    echo "Installing Railway CLI..."
    npm install -g @railway/cli
fi

# Login to Railway
railway login

# Initialize project
railway init

# Add environment variables
railway variables set PORT=8501

# Deploy
railway up

echo "✅ Deployed to Railway!"
railway status 