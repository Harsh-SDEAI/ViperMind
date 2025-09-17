# Production Deployment Guide

This guide covers deploying ViperMind to a production environment with proper security, monitoring, and performance optimizations.

## Prerequisites

### System Requirements
- **OS**: Ubuntu 20.04+ or CentOS 8+
- **RAM**: Minimum 4GB, Recommended 8GB+
- **CPU**: Minimum 2 cores, Recommended 4+ cores
- **Storage**: Minimum 20GB SSD
- **Network**: Stable internet connection

### Required Software
- Docker 20.10+
- Docker Compose 2.0+
- Git
- SSL certificates (for HTTPS)

### Required Services
- OpenAI API account with credits
- Domain name (optional but recommended)
- Email service (for notifications)

## Pre-Deployment Setup

### 1. Server Preparation

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Logout and login to apply Docker group changes
```

### 2. Firewall Configuration

```bash
# Configure UFW firewall
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable
```

### 3. SSL Certificate Setup

#### Option A: Let's Encrypt (Recommended)
```bash
# Install Certbot
sudo apt install certbot

# Generate certificate (replace with your domain)
sudo certbot certonly --standalone -d your-domain.com -d www.your-domain.com
```

#### Option B: Self-signed Certificate (Development)
```bash
# Create SSL directory
sudo mkdir -p /etc/nginx/ssl

# Generate self-signed certificate
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/nginx/ssl/key.pem \
  -out /etc/nginx/ssl/cert.pem
```

## Deployment Process

### 1. Clone Repository

```bash
# Clone the repository
git clone https://github.com/your-org/vipermind.git
cd vipermind

# Checkout the latest stable release
git checkout v1.0.0
```

### 2. Environment Configuration

```bash
# Copy production environment template
cp .env.production .env

# Edit environment variables
nano .env
```

**Critical Environment Variables:**
```bash
# Security - MUST CHANGE THESE
SECRET_KEY=your_very_secure_secret_key_here_at_least_32_characters_long
POSTGRES_PASSWORD=your_secure_database_password
GRAFANA_PASSWORD=your_secure_grafana_password

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Domain Configuration
REACT_APP_API_URL=https://your-domain.com

# Database Configuration
POSTGRES_USER=vipermind_user
POSTGRES_DB=vipermind_prod

# Optional: Backup Configuration
BACKUP_S3_BUCKET=your-backup-bucket
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
```

### 3. SSL Configuration

```bash
# Create nginx SSL directory
mkdir -p nginx/ssl

# Copy SSL certificates
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/key.pem
sudo chown $USER:$USER nginx/ssl/*
```

### 4. Deploy Application

```bash
# Make deployment script executable
chmod +x scripts/deploy.sh

# Run deployment
./scripts/deploy.sh production
```

The deployment script will:
1. Validate environment configuration
2. Create database backup (if existing)
3. Pull and build Docker images
4. Start services in correct order
5. Run database migrations
6. Perform health checks
7. Optimize performance

### 5. Post-Deployment Verification

```bash
# Check service status
docker-compose -f docker-compose.prod.yml ps

# Verify API health
curl -f https://your-domain.com/api/v1/monitoring/status

# Check application logs
docker-compose -f docker-compose.prod.yml logs -f backend
```

## Security Hardening

### 1. Database Security

```bash
# Connect to database container
docker-compose -f docker-compose.prod.yml exec db psql -U vipermind_user -d vipermind_prod

# Create read-only user for monitoring
CREATE USER monitoring WITH PASSWORD 'monitoring_password';
GRANT CONNECT ON DATABASE vipermind_prod TO monitoring;
GRANT USAGE ON SCHEMA public TO monitoring;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO monitoring;
```

### 2. Network Security

```bash
# Restrict Docker daemon access
sudo chmod 660 /var/run/docker.sock

# Configure fail2ban for SSH protection
sudo apt install fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 3. Application Security

Update `nginx/nginx.conf` with security headers:
```nginx
# Security headers
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

## Monitoring Setup

### 1. Grafana Configuration

1. Access Grafana at `https://your-domain.com:3001`
2. Login with admin credentials from `.env`
3. Import dashboards from `monitoring/grafana/dashboards/`
4. Configure alert notifications

### 2. Log Management

```bash
# Configure log rotation
sudo tee /etc/logrotate.d/docker-containers << EOF
/var/lib/docker/containers/*/*.log {
    rotate 7
    daily
    compress
    size=1M
    missingok
    delaycompress
    copytruncate
}
EOF
```

### 3. Automated Monitoring

Create monitoring cron jobs:
```bash
# Edit crontab
crontab -e

# Add monitoring jobs
# Health check every 5 minutes
*/5 * * * * curl -f https://your-domain.com/api/v1/monitoring/status || echo "Health check failed" | mail -s "ViperMind Health Alert" admin@your-domain.com

# Daily backup at 2 AM
0 2 * * * /path/to/vipermind/scripts/backup.sh

# Weekly performance optimization
0 3 * * 0 docker-compose -f /path/to/vipermind/docker-compose.prod.yml exec -T backend python optimize_performance.py
```

## Backup and Recovery

### 1. Automated Backups

The backup script creates:
- Database dump
- Redis snapshot
- Application files
- Configuration backup

```bash
# Manual backup
./scripts/backup.sh

# Restore from backup
./scripts/restore.sh backup_name_20231201_120000
```

### 2. Disaster Recovery

```bash
# Complete system restore
1. Restore server from backup/snapshot
2. Reinstall Docker and dependencies
3. Clone repository
4. Restore environment configuration
5. Run restore script
6. Verify system health
```

## Performance Optimization

### 1. Database Optimization

```bash
# Run performance optimization
docker-compose -f docker-compose.prod.yml exec backend python optimize_performance.py

# Monitor query performance
docker-compose -f docker-compose.prod.yml exec db psql -U vipermind_user -d vipermind_prod -c "SELECT * FROM pg_stat_activity;"
```

### 2. Caching Optimization

```bash
# Monitor Redis performance
docker-compose -f docker-compose.prod.yml exec redis redis-cli info memory
docker-compose -f docker-compose.prod.yml exec redis redis-cli info stats
```

### 3. Application Performance

```bash
# Monitor application metrics
curl https://your-domain.com/api/v1/monitoring/performance

# Check resource usage
docker stats
```

## Scaling Considerations

### Horizontal Scaling

For high-traffic deployments:

1. **Load Balancer**: Use nginx or cloud load balancer
2. **Multiple Backend Instances**: Scale backend containers
3. **Database Clustering**: PostgreSQL read replicas
4. **Redis Clustering**: Redis cluster mode
5. **CDN**: CloudFlare or AWS CloudFront

### Vertical Scaling

Resource recommendations by user load:

| Users | CPU | RAM | Storage |
|-------|-----|-----|---------|
| 1-100 | 2 cores | 4GB | 20GB |
| 100-500 | 4 cores | 8GB | 50GB |
| 500-1000 | 8 cores | 16GB | 100GB |
| 1000+ | 16+ cores | 32GB+ | 200GB+ |

## Troubleshooting

### Common Issues

1. **Service Won't Start**
   ```bash
   # Check logs
   docker-compose -f docker-compose.prod.yml logs service_name
   
   # Check resource usage
   df -h
   free -m
   ```

2. **Database Connection Issues**
   ```bash
   # Test database connectivity
   docker-compose -f docker-compose.prod.yml exec backend python -c "from app.db.session import engine; print(engine.execute('SELECT 1').scalar())"
   ```

3. **SSL Certificate Issues**
   ```bash
   # Renew Let's Encrypt certificate
   sudo certbot renew
   
   # Update nginx configuration
   docker-compose -f docker-compose.prod.yml restart nginx
   ```

### Performance Issues

1. **High Memory Usage**
   ```bash
   # Check container memory usage
   docker stats --no-stream
   
   # Optimize Redis memory
   docker-compose -f docker-compose.prod.yml exec redis redis-cli config set maxmemory 1gb
   ```

2. **Slow API Responses**
   ```bash
   # Check database performance
   docker-compose -f docker-compose.prod.yml exec backend python backend/test_performance_optimization.py
   
   # Monitor cache hit rates
   curl https://your-domain.com/api/v1/monitoring/metrics?metric_name=cache_hit_rate
   ```

## Maintenance

### Regular Maintenance Tasks

1. **Weekly**
   - Review monitoring alerts
   - Check backup integrity
   - Update security patches

2. **Monthly**
   - Review performance metrics
   - Clean up old logs and backups
   - Update dependencies

3. **Quarterly**
   - Security audit
   - Capacity planning review
   - Disaster recovery testing

### Update Process

```bash
# 1. Backup current system
./scripts/backup.sh

# 2. Pull latest changes
git fetch origin
git checkout v1.1.0  # or latest version

# 3. Update environment if needed
# Review .env.production for new variables

# 4. Deploy update
./scripts/deploy.sh production

# 5. Verify deployment
curl https://your-domain.com/api/v1/monitoring/status
```

## Support

For production deployment support:
- Email: support@vipermind.com
- Documentation: https://docs.vipermind.com
- Emergency: Create GitHub issue with "production" label