#!/bin/bash

# ViperMind Deployment Script
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-production}
BACKUP_BEFORE_DEPLOY=${2:-true}

echo -e "${GREEN}🚀 Starting ViperMind deployment for ${ENVIRONMENT} environment${NC}"

# Check if required files exist
if [ ! -f ".env.${ENVIRONMENT}" ]; then
    echo -e "${RED}❌ Environment file .env.${ENVIRONMENT} not found${NC}"
    exit 1
fi

if [ ! -f "docker-compose.prod.yml" ]; then
    echo -e "${RED}❌ Production docker-compose file not found${NC}"
    exit 1
fi

# Load environment variables
export $(cat .env.${ENVIRONMENT} | grep -v '^#' | xargs)

echo -e "${YELLOW}📋 Pre-deployment checks...${NC}"

# Check Docker and Docker Compose
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed${NC}"
    exit 1
fi

# Check required environment variables
required_vars=("POSTGRES_PASSWORD" "SECRET_KEY" "OPENAI_API_KEY")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo -e "${RED}❌ Required environment variable $var is not set${NC}"
        exit 1
    fi
done

echo -e "${GREEN}✅ Pre-deployment checks passed${NC}"

# Backup existing data if requested
if [ "$BACKUP_BEFORE_DEPLOY" = "true" ]; then
    echo -e "${YELLOW}💾 Creating backup...${NC}"
    ./scripts/backup.sh
    echo -e "${GREEN}✅ Backup completed${NC}"
fi

# Pull latest images
echo -e "${YELLOW}📥 Pulling latest Docker images...${NC}"
docker-compose -f docker-compose.prod.yml pull

# Build custom images
echo -e "${YELLOW}🔨 Building application images...${NC}"
docker-compose -f docker-compose.prod.yml build --no-cache

# Stop existing services
echo -e "${YELLOW}🛑 Stopping existing services...${NC}"
docker-compose -f docker-compose.prod.yml down

# Start database and Redis first
echo -e "${YELLOW}🗄️ Starting database and cache services...${NC}"
docker-compose -f docker-compose.prod.yml up -d db redis

# Wait for database to be ready
echo -e "${YELLOW}⏳ Waiting for database to be ready...${NC}"
timeout=60
counter=0
while ! docker-compose -f docker-compose.prod.yml exec -T db pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB} > /dev/null 2>&1; do
    if [ $counter -ge $timeout ]; then
        echo -e "${RED}❌ Database failed to start within ${timeout} seconds${NC}"
        exit 1
    fi
    sleep 1
    counter=$((counter + 1))
done

echo -e "${GREEN}✅ Database is ready${NC}"

# Run database migrations
echo -e "${YELLOW}🔄 Running database migrations...${NC}"
docker-compose -f docker-compose.prod.yml run --rm backend python -m alembic upgrade head

# Start all services
echo -e "${YELLOW}🚀 Starting all services...${NC}"
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be healthy
echo -e "${YELLOW}🏥 Waiting for services to be healthy...${NC}"
services=("backend" "frontend" "nginx")
for service in "${services[@]}"; do
    echo -e "${YELLOW}   Checking ${service}...${NC}"
    timeout=120
    counter=0
    while ! docker-compose -f docker-compose.prod.yml ps ${service} | grep -q "healthy"; do
        if [ $counter -ge $timeout ]; then
            echo -e "${RED}❌ ${service} failed to become healthy within ${timeout} seconds${NC}"
            docker-compose -f docker-compose.prod.yml logs ${service}
            exit 1
        fi
        sleep 2
        counter=$((counter + 2))
    done
    echo -e "${GREEN}   ✅ ${service} is healthy${NC}"
done

# Run post-deployment tasks
echo -e "${YELLOW}🔧 Running post-deployment tasks...${NC}"

# Warm up the cache
echo -e "${YELLOW}   Warming up cache...${NC}"
docker-compose -f docker-compose.prod.yml exec -T backend python scripts/warm_cache.py

# Run performance optimization
echo -e "${YELLOW}   Running performance optimization...${NC}"
docker-compose -f docker-compose.prod.yml exec -T backend python optimize_performance.py

# Verify deployment
echo -e "${YELLOW}🔍 Verifying deployment...${NC}"
if curl -f -s "http://localhost/api/v1/monitoring/status" > /dev/null; then
    echo -e "${GREEN}✅ API is responding${NC}"
else
    echo -e "${RED}❌ API is not responding${NC}"
    exit 1
fi

if curl -f -s "http://localhost/health" > /dev/null; then
    echo -e "${GREEN}✅ Frontend is responding${NC}"
else
    echo -e "${RED}❌ Frontend is not responding${NC}"
    exit 1
fi

# Show deployment summary
echo -e "\n${GREEN}🎉 Deployment completed successfully!${NC}"
echo -e "${GREEN}📊 Deployment Summary:${NC}"
echo -e "   Environment: ${ENVIRONMENT}"
echo -e "   Frontend URL: http://localhost"
echo -e "   API URL: http://localhost/api/v1"
echo -e "   Monitoring: http://localhost:3001 (Grafana)"
echo -e "   Metrics: http://localhost:9090 (Prometheus)"

echo -e "\n${YELLOW}📝 Next Steps:${NC}"
echo -e "   1. Configure SSL certificates for HTTPS"
echo -e "   2. Set up domain name and DNS"
echo -e "   3. Configure monitoring alerts"
echo -e "   4. Set up automated backups"
echo -e "   5. Review security settings"

echo -e "\n${GREEN}✅ ViperMind is now running in ${ENVIRONMENT} mode!${NC}"