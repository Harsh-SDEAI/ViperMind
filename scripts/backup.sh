#!/bin/bash

# ViperMind Backup Script
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="vipermind_backup_${TIMESTAMP}"

echo -e "${GREEN}💾 Starting ViperMind backup...${NC}"

# Create backup directory
mkdir -p ${BACKUP_DIR}

# Load environment variables
if [ -f ".env.production" ]; then
    export $(cat .env.production | grep -v '^#' | xargs)
elif [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo -e "${RED}❌ No environment file found${NC}"
    exit 1
fi

echo -e "${YELLOW}📊 Creating database backup...${NC}"

# Database backup
if docker-compose -f docker-compose.prod.yml ps db | grep -q "Up"; then
    docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U ${POSTGRES_USER} -d ${POSTGRES_DB} > ${BACKUP_DIR}/${BACKUP_NAME}_database.sql
    echo -e "${GREEN}✅ Database backup completed${NC}"
else
    echo -e "${YELLOW}⚠️ Database container is not running, skipping database backup${NC}"
fi

echo -e "${YELLOW}📁 Creating Redis backup...${NC}"

# Redis backup
if docker-compose -f docker-compose.prod.yml ps redis | grep -q "Up"; then
    docker-compose -f docker-compose.prod.yml exec -T redis redis-cli BGSAVE
    sleep 2
    docker cp $(docker-compose -f docker-compose.prod.yml ps -q redis):/data/dump.rdb ${BACKUP_DIR}/${BACKUP_NAME}_redis.rdb
    echo -e "${GREEN}✅ Redis backup completed${NC}"
else
    echo -e "${YELLOW}⚠️ Redis container is not running, skipping Redis backup${NC}"
fi

echo -e "${YELLOW}📦 Creating application backup...${NC}"

# Application files backup
tar -czf ${BACKUP_DIR}/${BACKUP_NAME}_app.tar.gz \
    --exclude='node_modules' \
    --exclude='__pycache__' \
    --exclude='.git' \
    --exclude='*.log' \
    --exclude='backups' \
    .

echo -e "${GREEN}✅ Application backup completed${NC}"

echo -e "${YELLOW}📋 Creating backup manifest...${NC}"

# Create backup manifest
cat > ${BACKUP_DIR}/${BACKUP_NAME}_manifest.json << EOF
{
  "backup_name": "${BACKUP_NAME}",
  "timestamp": "${TIMESTAMP}",
  "date": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "files": {
    "database": "${BACKUP_NAME}_database.sql",
    "redis": "${BACKUP_NAME}_redis.rdb",
    "application": "${BACKUP_NAME}_app.tar.gz"
  },
  "environment": {
    "postgres_db": "${POSTGRES_DB}",
    "postgres_user": "${POSTGRES_USER}"
  },
  "version": "1.0.0"
}
EOF

echo -e "${GREEN}✅ Backup manifest created${NC}"

# Calculate backup sizes
DB_SIZE=$(du -h ${BACKUP_DIR}/${BACKUP_NAME}_database.sql 2>/dev/null | cut -f1 || echo "N/A")
REDIS_SIZE=$(du -h ${BACKUP_DIR}/${BACKUP_NAME}_redis.rdb 2>/dev/null | cut -f1 || echo "N/A")
APP_SIZE=$(du -h ${BACKUP_DIR}/${BACKUP_NAME}_app.tar.gz 2>/dev/null | cut -f1 || echo "N/A")

echo -e "\n${GREEN}🎉 Backup completed successfully!${NC}"
echo -e "${GREEN}📊 Backup Summary:${NC}"
echo -e "   Backup Name: ${BACKUP_NAME}"
echo -e "   Database Size: ${DB_SIZE}"
echo -e "   Redis Size: ${REDIS_SIZE}"
echo -e "   Application Size: ${APP_SIZE}"
echo -e "   Location: ${BACKUP_DIR}/"

# Clean up old backups (keep last 7 days)
echo -e "${YELLOW}🧹 Cleaning up old backups...${NC}"
find ${BACKUP_DIR} -name "vipermind_backup_*" -type f -mtime +7 -delete
echo -e "${GREEN}✅ Old backups cleaned up${NC}"

# Optional: Upload to S3 if configured
if [ ! -z "${BACKUP_S3_BUCKET}" ] && [ ! -z "${AWS_ACCESS_KEY_ID}" ]; then
    echo -e "${YELLOW}☁️ Uploading backup to S3...${NC}"
    
    if command -v aws &> /dev/null; then
        aws s3 cp ${BACKUP_DIR}/${BACKUP_NAME}_database.sql s3://${BACKUP_S3_BUCKET}/backups/
        aws s3 cp ${BACKUP_DIR}/${BACKUP_NAME}_redis.rdb s3://${BACKUP_S3_BUCKET}/backups/
        aws s3 cp ${BACKUP_DIR}/${BACKUP_NAME}_app.tar.gz s3://${BACKUP_S3_BUCKET}/backups/
        aws s3 cp ${BACKUP_DIR}/${BACKUP_NAME}_manifest.json s3://${BACKUP_S3_BUCKET}/backups/
        echo -e "${GREEN}✅ Backup uploaded to S3${NC}"
    else
        echo -e "${YELLOW}⚠️ AWS CLI not found, skipping S3 upload${NC}"
    fi
fi

echo -e "\n${GREEN}✅ Backup process completed!${NC}"