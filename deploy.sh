#!/bin/bash

# RAG System Deployment Script
# This script helps you deploy your RAG system to AWS EC2

echo "🚀 RAG System Deployment Script"
echo "================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop and try again."
    exit 1
fi

echo "✅ Docker is running"

# Build the Docker image
echo "📦 Building Docker image..."
docker build -t rag-system-image .

if [ $? -eq 0 ]; then
    echo "✅ Docker image built successfully"
else
    echo "❌ Failed to build Docker image"
    exit 1
fi

# Test the container locally
echo "🧪 Testing container locally..."
docker run -d -p 8000:8000 --name rag-test rag-system-image

# Wait for container to start
sleep 5

# Test the API
echo "🔍 Testing API..."
response=$(curl -s http://localhost:8000/ | grep -o '"status":"[^"]*"')

if [[ $response == *"ready"* ]]; then
    echo "✅ API is working correctly"
else
    echo "❌ API test failed"
    docker logs rag-test
    docker stop rag-test
    docker rm rag-test
    exit 1
fi

# Clean up test container
docker stop rag-test
docker rm rag-test

echo ""
echo "🎉 Local testing completed successfully!"
echo ""
echo "Next steps for AWS deployment:"
echo "1. Push to Docker Hub:"
echo "   docker tag rag-system-image your-username/rag-system-image:latest"
echo "   docker push your-username/rag-system-image:latest"
echo ""
echo "2. Deploy to AWS EC2:"
echo "   - Launch an EC2 instance (Ubuntu, t2.micro)"
echo "   - Install Docker on EC2"
echo "   - Pull and run your image"
echo ""
echo "See DEPLOYMENT.md for detailed instructions."
