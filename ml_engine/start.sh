#!/bin/bash

# Wurdo ML Engine Startup Script
# This script starts the ML engine with Docker and ngrok

echo "🚀 Starting Wurdo ML Engine..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create .env file with your configuration:"
    echo "  - NGROK_AUTHTOKEN"
    echo "  - NGROK_DOMAIN"
    echo "  - UPSTASH_REDIS_REST_URL"
    echo "  - UPSTASH_REDIS_REST_TOKEN"
    echo "  - FRONTEND_URL"
    exit 1
fi

# Load environment variables
source .env

# Check required environment variables
if [ -z "$NGROK_AUTHTOKEN" ] || [ "$NGROK_AUTHTOKEN" = "your_ngrok_auth_token_here" ]; then
    echo "❌ Error: NGROK_AUTHTOKEN not set in .env file"
    exit 1
fi

if [ -z "$NGROK_DOMAIN" ] || [ "$NGROK_DOMAIN" = "your_ngrok_domain_here" ]; then
    echo "❌ Error: NGROK_DOMAIN not set in .env file"
    exit 1
fi

echo "✅ Environment variables loaded"
echo "🌐 ngrok domain: $NGROK_DOMAIN"
echo "🔗 Frontend URL: $FRONTEND_URL"

# Build and start the services
echo "🐳 Building and starting Docker services..."
docker-compose up --build

echo "🎉 ML Engine started successfully!"
echo "📊 ngrok dashboard: http://localhost:4040"
echo "🔗 ML Engine API: https://$NGROK_DOMAIN"
