#!/bin/bash
# Docker Local Testing Script for Sprint 1 Day 3
# This script validates the Docker setup and local deployment

set -e

echo "🐳 Testing Docker Setup for UK Election Simulator"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ $1${NC}"
    else
        echo -e "${RED}✗ $1${NC}"
        exit 1
    fi
}

# Test 1: Build Docker image
echo -e "${YELLOW}Step 1: Building Docker image...${NC}"
docker build -t ukge-simulator:test . > /dev/null 2>&1
print_status "Docker image built successfully"

# Test 2: Run container
echo -e "${YELLOW}Step 2: Starting container...${NC}"
CONTAINER_ID=$(docker run -d --name ukge-test-script -p 8505:8501 ukge-simulator:test)
print_status "Container started with ID: ${CONTAINER_ID:0:12}"

# Test 3: Wait for application to be ready
echo -e "${YELLOW}Step 3: Waiting for application to be ready...${NC}"
sleep 20

# Test 4: Health check
echo -e "${YELLOW}Step 4: Testing health endpoint...${NC}"
curl -f http://localhost:8505/_stcore/health > /dev/null 2>&1
print_status "Health check passed"

# Test 5: Main application check
echo -e "${YELLOW}Step 5: Testing main application...${NC}"
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8505)
if [ "$HTTP_STATUS" -eq 200 ]; then
    print_status "Main application responding (HTTP $HTTP_STATUS)"
else
    echo -e "${RED}✗ Main application failed (HTTP $HTTP_STATUS)${NC}"
    exit 1
fi

# Test 6: Docker compose test
echo -e "${YELLOW}Step 6: Testing Docker Compose...${NC}"
docker stop ukge-test-script > /dev/null 2>&1
docker rm ukge-test-script > /dev/null 2>&1

# Change port in compose for this test
sed -i 's/8504:8501/8506:8501/' docker-compose.yml
docker compose up -d > /dev/null 2>&1
sleep 20

curl -f http://localhost:8506/_stcore/health > /dev/null 2>&1
print_status "Docker Compose deployment successful"

# Cleanup
echo -e "${YELLOW}Cleaning up...${NC}"
docker compose down > /dev/null 2>&1
# Restore original port
sed -i 's/8506:8501/8504:8501/' docker-compose.yml
docker rmi ukge-simulator:test > /dev/null 2>&1

echo ""
echo -e "${GREEN}🎉 All Docker tests passed successfully!${NC}"
echo -e "${GREEN}The application is ready for Day 4 deployment tasks.${NC}"
