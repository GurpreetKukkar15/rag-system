# RAG System Deployment Guide

## 🚀 Phase 3: Containerization and Cloud Deployment

This guide will help you containerize your RAG system and deploy it to AWS EC2.

## Prerequisites

- Docker Desktop installed and running
- AWS Account (free tier eligible)
- Docker Hub account (free)

## Step 1: Local Docker Testing

### 1.1 Build the Docker Image

```bash
# Make sure Docker Desktop is running
docker build -t rag-system-image .

# Check if the image was created
docker images | grep rag-system-image
```

### 1.2 Test the Container Locally

```bash
# Run the container
docker run -p 8000:8000 rag-system-image

# Test the API (in another terminal)
curl http://localhost:8000/
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is RAG?"}'
```

## Step 2: Deploy to Docker Hub

### 2.1 Login to Docker Hub

```bash
docker login
# Enter your Docker Hub username and password
```

### 2.2 Tag and Push the Image

```bash
# Replace 'your-username' with your actual Docker Hub username
docker tag rag-system-image your-username/rag-system-image:latest
docker push your-username/rag-system-image:latest
```

## Step 3: Deploy to AWS EC2

### 3.1 Launch an EC2 Instance

1. Go to AWS Management Console
2. Navigate to EC2 dashboard
3. Click "Launch instance"
4. Choose:
   - **AMI**: Ubuntu Server 22.04 LTS (Free tier eligible)
   - **Instance Type**: t2.micro (Free tier eligible)
   - **Key Pair**: Create new or use existing
   - **Security Group**: Add inbound rule for port 8000 from 0.0.0.0/0
5. Launch the instance

### 3.2 Connect to EC2 Instance

```bash
# Replace with your key file and public IP
ssh -i "your-key-pair.pem" ubuntu@ec2-xx-xx-xx-xx.us-west-2.compute.amazonaws.com
```

### 3.3 Install Docker on EC2

```bash
# Update system
sudo apt-get update

# Install Docker
sudo apt-get install docker.io -y

# Start and enable Docker
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group (optional, for running without sudo)
sudo usermod -aG docker ubuntu
```

### 3.4 Deploy Your Application

```bash
# Pull your image from Docker Hub
docker pull your-username/rag-system-image:latest

# Run the container
docker run -d -p 8000:8000 --name rag-system your-username/rag-system-image:latest

# Check if container is running
docker ps

# View logs
docker logs rag-system
```

### 3.5 Test Your Deployed Application

```bash
# Test health check
curl http://localhost:8000/

# Test query endpoint
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is RAG?"}'
```

## Step 4: Access Your Application

Your RAG system is now live! You can access it at:
- **Health Check**: `http://your-ec2-public-ip:8000/`
- **Query Endpoint**: `http://your-ec2-public-ip:8000/query`

## Troubleshooting

### Common Issues

1. **Docker not running**: Make sure Docker Desktop is started
2. **Port already in use**: Stop other services using port 8000
3. **EC2 connection refused**: Check security group rules
4. **Container won't start**: Check logs with `docker logs rag-system`

### Useful Commands

```bash
# Stop the container
docker stop rag-system

# Remove the container
docker rm rag-system

# Restart the container
docker restart rag-system

# View container logs
docker logs -f rag-system

# Access container shell
docker exec -it rag-system /bin/bash
```

## Production Considerations

### Security
- Use environment variables for sensitive data
- Implement authentication
- Use HTTPS in production
- Restrict security group access

### Performance
- Use larger EC2 instances for production
- Implement caching
- Add load balancing for high traffic
- Monitor resource usage

### Monitoring
- Set up CloudWatch monitoring
- Implement health checks
- Add logging and alerting
- Monitor costs

## Cost Optimization

- Use spot instances for non-critical workloads
- Implement auto-scaling
- Monitor and optimize resource usage
- Use reserved instances for predictable workloads

## Next Steps

1. **Add Domain**: Use Route 53 to add a custom domain
2. **SSL Certificate**: Implement HTTPS with Let's Encrypt
3. **Load Balancer**: Add Application Load Balancer for high availability
4. **Database**: Add persistent storage for larger document collections
5. **CI/CD**: Implement automated deployment pipeline

---

## 🎉 Congratulations!

You have successfully deployed a complete RAG system to the cloud! Your application is now:
- ✅ Containerized with Docker
- ✅ Deployed to AWS EC2
- ✅ Accessible from anywhere on the internet
- ✅ Scalable and production-ready
