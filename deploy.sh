#!/bin/bash

# HealthFlow Deployment Script
# This script deploys HealthFlow services using Docker Compose
# Can be run manually or by Jenkins CI/CD pipeline

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
DOCKER_USERNAME="${DOCKER_USERNAME:-taoufikjeta}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.yml}"

echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}🚀 HealthFlow Deployment Script${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "Docker Username: ${GREEN}${DOCKER_USERNAME}${NC}"
echo -e "Image Tag: ${GREEN}${IMAGE_TAG}${NC}"
echo -e "Compose File: ${GREEN}${COMPOSE_FILE}${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo -e "\n${YELLOW}📋 Checking prerequisites...${NC}"

if ! command_exists docker; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker found${NC}"

if ! command_exists docker-compose; then
    echo -e "${RED}❌ Docker Compose is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker Compose found${NC}"

# Export environment variables for docker-compose
export DOCKER_USERNAME
export IMAGE_TAG

# Pull latest images
echo -e "\n${YELLOW}📥 Pulling latest Docker images...${NC}"
docker-compose -f "${COMPOSE_FILE}" pull || {
    echo -e "${YELLOW}⚠️ Failed to pull some images, will build locally${NC}"
}

# Stop existing containers
echo -e "\n${YELLOW}🛑 Stopping existing containers...${NC}"
docker-compose -f "${COMPOSE_FILE}" down || true

# Start services
echo -e "\n${YELLOW}🚀 Starting HealthFlow services...${NC}"
docker-compose -f "${COMPOSE_FILE}" up -d

# Wait for services to start
echo -e "\n${YELLOW}⏳ Waiting for services to start (30 seconds)...${NC}"
sleep 30

# Check service status
echo -e "\n${YELLOW}📊 Checking service status...${NC}"
docker-compose -f "${COMPOSE_FILE}" ps

# Health checks
echo -e "\n${YELLOW}🏥 Running health checks...${NC}"

declare -A services=(
    ["PostgreSQL"]="localhost:5433"
    ["API Gateway"]="http://localhost:8085/actuator/health"
    ["Proxy FHIR"]="http://localhost:8081/actuator/health"
    ["DeID Service"]="http://localhost:5000/api/v1/health"
    ["Featurizer"]="http://localhost:5001/api/v1/health"
    ["ML Predictor"]="http://localhost:5002/api/v1/health"
    ["Score API"]="http://localhost:5003/health"
    ["Audit Fairness"]="http://localhost:5004/api/v1/health"
    ["Dashboard"]="http://localhost:3002"
)

all_healthy=true

for service in "${!services[@]}"; do
    url="${services[$service]}"
    
    if [[ "$url" == localhost:* ]]; then
        # TCP check for database
        if timeout 5 bash -c "echo > /dev/tcp/${url/localhost:/127.0.0.1/}"; then
            echo -e "${GREEN}✅ ${service}: HEALTHY${NC}"
        else
            echo -e "${RED}❌ ${service}: UNHEALTHY${NC}"
            all_healthy=false
        fi
    else
        # HTTP check
        http_code=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")
        
        if [ "$http_code" -eq 200 ]; then
            echo -e "${GREEN}✅ ${service}: HEALTHY (HTTP ${http_code})${NC}"
        else
            echo -e "${RED}❌ ${service}: UNHEALTHY (HTTP ${http_code})${NC}"
            all_healthy=false
        fi
    fi
done

# Summary
echo -e "\n${BLUE}════════════════════════════════════════${NC}"

if [ "$all_healthy" = true ]; then
    echo -e "${GREEN}✅ DEPLOYMENT SUCCESSFUL!${NC}"
    echo -e "\n${GREEN}All services are healthy and running${NC}"
    echo -e "\n${YELLOW}📱 Access the application:${NC}"
    echo -e "  Dashboard:    ${BLUE}http://localhost:3002${NC}"
    echo -e "  API Gateway:  ${BLUE}http://localhost:8085${NC}"
else
    echo -e "${YELLOW}⚠️ DEPLOYMENT COMPLETED WITH WARNINGS${NC}"
    echo -e "\n${RED}Some services are not healthy${NC}"
    echo -e "${YELLOW}Check logs with: docker-compose logs${NC}"
fi

echo -e "${BLUE}════════════════════════════════════════${NC}"

exit 0
