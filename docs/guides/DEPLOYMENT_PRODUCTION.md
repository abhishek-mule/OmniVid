# OmniVid Production Deployment Guide

This guide covers deploying OmniVid to production environments with Docker, scaling configurations, and monitoring setup.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Production Deployment](#production-deployment)
- [SSL Configuration](#ssl-configuration)
- [Monitoring & Logging](#monitoring--logging)
- [Scaling](#scaling)
- [Backup & Recovery](#backup--recovery)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements
- **OS**: Linux (Ubuntu 20.04+ recommended)
- **Memory**: Minimum 8GB RAM (16GB+ recommended)
- **Storage**: Minimum 50GB SSD (100GB+ recommended)
- **CPU**: Minimum 4 cores (8+ cores recommended for production)
- **Docker**: Version 20.10+
- **Docker Compose**: Version 2.0+

### Required Services
- Domain name with DNS access
- SSL certificates (Let's Encrypt recommended)
- External database (PostgreSQL 15+ recommended for production)
- Redis cluster (for production scaling)

## Environment Setup

### 1. Clone Repository
```bash
git clone https://github.com/your-org/omnivid.git
cd omnivid
```

### 2. Create Production Environment File
```bash
cp .env.example .env.prod
```

Edit `.env.prod` with production values:
```bash
# Database Configuration
DB_HOST=your-production-db-host
DB_PORT=5432
DB_USER=omnivid
DB_PASSWORD=your-secure-password
DB_NAME=omnivid_prod

# Redis Configuration
REDIS_HOST=your-production-redis-host
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password

# Security
SECRET_KEY=your-very-secure-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# API Configuration
API_PORT=8000
FRONTEND_PORT=3000
DEBUG=False
LOG_LEVEL=INFO

# Email Configuration (for notifications)
SMTP_HOST=your-smtp-server
SMTP_PORT=587
SMTP_USER=your-email@domain.com
SMTP_PASSWORD=your-email-password

# File Storage
OUTPUT_DIR=/app/output
ASSETS_DIR=/app/assets
TEMP_DIR=/app/tmp
MAX_FILE_SIZE=100MB

# Monitoring
FLOWER_USER=admin
FLOWER_PASSWORD=secure-flower-password
GRAFANA_PASSWORD=secure-grafana-password

# External Services
# Add any external API keys, CDN URLs, etc.
```

### 3. Create Directory Structure
```bash
# Create data directories
mkdir -p data/{redis,postgres,output,assets,tmp,prometheus,grafana}
mkdir -p logs/{api,celery,nginx,postgres}
mkdir -p config/{nginx/ssl,prometheus,grafana}
```

## Production Deployment

### Method 1: Docker Compose (Recommended)

#### Basic Production Deployment
```bash
# Build and start services
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d

# Check service status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

#### With Monitoring Stack
```bash
# Include monitoring services
docker-compose -f docker-compose.prod.yml --profile monitoring --env-file .env.prod up -d
```

### Method 2: Kubernetes (Advanced)
See `k8s/` directory for Kubernetes manifests.

### Method 3: Cloud Platform Deployment

#### AWS ECS
```bash
# Build and push images to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin your-account.dkr.ecr.us-east-1.amazonaws.com

docker build -t omnivid-backend ./backend
docker tag omnivid-backend:latest your-account.dkr.ecr.us-east-1.amazonaws.com/omnivid-backend:latest
docker push your-account.dkr.ecr.us-east-1.amazonaws.com/omnivid-backend:latest

# Deploy using ECS Task Definition
aws ecs register-task-definition --cli-input-json file://aws/task-definition.json
aws ecs update-service --cluster omnivid-cluster --service omnivid-service --force-new-deployment
```

#### Google Cloud Run
```bash
# Build and deploy to Cloud Run
gcloud builds submit --tag gcr.io/your-project/omnivid-backend ./backend
gcloud run deploy omnivid-backend --image gcr.io/your-project/omnivid-backend --platform managed

gcloud builds submit --tag gcr.io/your-project/omnivid-frontend ./frontend
gcloud run deploy omnivid-frontend --image gcr.io/your-project/omnivid-frontend --platform managed
```

## SSL Configuration

### Using Let's Encrypt (Recommended)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Generate certificates
sudo certbot certonly --standalone -d yourdomain.com -d api.yourdomain.com

# Copy certificates to project
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem config/nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem config/nginx/ssl/key.pem

# Set proper permissions
sudo chmod 600 config/nginx/ssl/key.pem
sudo chown $USER:$USER config/nginx/ssl/*.pem
```

### Self-Signed Certificates (Development)
```bash
# Generate self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout config/nginx/ssl/key.pem \
  -out config/nginx/ssl/cert.pem
```

## Monitoring & Logging

### Service Health Checks
All services include built-in health checks:

```bash
# Check service health
curl http://localhost/api/health
curl http://localhost:8000/health
curl http://localhost:3000/api/health

# Check WebSocket status
curl http://localhost/ws/status
```

### Log Management

#### View Logs
```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f api
docker-compose -f docker-compose.prod.yml logs -f celery-worker
docker-compose -f docker-compose.prod.yml logs -f nginx

# Recent logs only
docker-compose -f docker-compose.prod.yml logs --tail=100 api
```

#### Log Rotation
Logs are automatically rotated via Docker logging drivers. Additional log rotation:

```bash
# Add to /etc/logrotate.d/omnivid
/path/to/omnivid/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0644 $USER $USER
    postrotate
        docker-compose -f /path/to/omnivid/docker-compose.prod.yml restart nginx
    endscript
}
```

### Monitoring Dashboard Access
- **Prometheus**: http://your-domain:9090
- **Grafana**: http://your-domain:3001 (admin/password from env)
- **Flower**: http://your-domain:5555

## Scaling

### Horizontal Scaling

#### Scale API Services
```bash
# Scale API instances
docker-compose -f docker-compose.prod.yml up -d --scale api=3

# Scale Celery workers
docker-compose -f docker-compose.prod.yml up -d --scale celery-worker=4
```

#### Load Balancing
Nginx automatically load balances across API instances. For external load balancing:

```nginx
upstream backend {
    server api-1:8000 max_fails=3 fail_timeout=30s;
    server api-2:8000 max_fails=3 fail_timeout=30s;
    server api-3:8000 max_fails=3 fail_timeout=30s;
    keepalive 32;
}
```

### Vertical Scaling

#### Resource Limits
Adjust resource limits in `docker-compose.prod.yml`:

```yaml
deploy:
  resources:
    limits:
      memory: 4G
      cpus: '2.0'
    reservations:
      memory: 2G
      cpus: '1.0'
```

#### Database Optimization
```sql
-- PostgreSQL performance tuning
ALTER SYSTEM SET shared_buffers = '2GB';
ALTER SYSTEM SET effective_cache_size = '6GB';
ALTER SYSTEM SET work_mem = '64MB';
ALTER SYSTEM SET maintenance_work_mem = '512MB';
SELECT pg_reload_conf();
```

### Redis Clustering
For high availability, set up Redis cluster:

```yaml
redis-cluster:
  image: redis:7-alpine
  command: redis-server --cluster-enabled yes --cluster-config-file nodes.conf
  # Additional Redis cluster configuration
```

## Backup & Recovery

### Database Backup
```bash
# Create backup
docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U omnivid omnivid > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore backup
docker-compose -f docker-compose.prod.yml exec -T postgres psql -U omnivid omnivid < backup_20231215_120000.sql
```

### Automated Backups
```bash
# Add to crontab
0 2 * * * cd /path/to/omnivid && ./scripts/backup.sh
```

### File Storage Backup
```bash
# Backup user files
tar -czf files_backup_$(date +%Y%m%d).tar.gz data/output data/assets

# Restore files
tar -xzf files_backup_20231215.tar.gz
```

### Disaster Recovery
1. **Infrastructure Recovery**: Redeploy using Docker Compose
2. **Database Recovery**: Restore from latest backup
3. **Application Recovery**: Redeploy containers
4. **Verification**: Run health checks and test endpoints

## Security Best Practices

### Container Security
```bash
# Scan images for vulnerabilities
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image omnivid-backend:latest

# Use non-root users (already configured)
# Regular security updates
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d
```

### Network Security
```yaml
# docker-compose.prod.yml
services:
  nginx:
    ports:
      - "80:80"
      - "443:443"  # Only expose necessary ports
    
  api:
    networks:
      - internal  # Use internal networks
    expose:
      - "8000"
```

### Environment Security
- Use strong passwords and keys
- Enable firewall rules
- Regular security updates
- Monitor access logs
- Use HTTPS in production

## Troubleshooting

### Common Issues

#### Service Won't Start
```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs service-name

# Check disk space
df -h

# Check memory
free -h

# Restart specific service
docker-compose -f docker-compose.prod.yml restart service-name
```

#### Database Connection Issues
```bash
# Test database connection
docker-compose -f docker-compose.prod.yml exec postgres psql -U omnivid -c "SELECT 1;"

# Check database logs
docker-compose -f docker-compose.prod.yml logs postgres
```

#### Redis Connection Issues
```bash
# Test Redis connection
docker-compose -f docker-compose.prod.yml exec redis redis-cli ping

# Check Redis logs
docker-compose -f docker-compose.prod.yml logs redis
```

#### WebSocket Connection Issues
```bash
# Test WebSocket endpoint
wscat -c ws://localhost/ws/videos/test

# Check WebSocket status
curl http://localhost/ws/status
```

### Performance Issues

#### High Memory Usage
```bash
# Check memory usage per container
docker stats

# Optimize Celery worker concurrency
# Edit celery-worker command in docker-compose.prod.yml
command: celery -A src.workers.celery_app worker --loglevel=info --concurrency=1
```

#### Slow API Responses
```bash
# Check API logs for errors
docker-compose -f docker-compose.prod.yml logs api | grep ERROR

# Check database performance
docker-compose -f docker-compose.prod.yml exec postgres psql -U omnivid -c "
  SELECT query, calls, total_time, mean_time 
  FROM pg_stat_statements 
  ORDER BY total_time DESC 
  LIMIT 10;"
```

#### Video Processing Queue Backlog
```bash
# Check Celery queue status
docker-compose -f docker-compose.prod.yml exec celery-worker celery -A src.workers.celery_app inspect active

# Monitor task completion
docker-compose -f docker-compose.prod.yml exec flower flower
```

### Debug Mode
For debugging issues, temporarily enable debug mode:

```bash
# Edit docker-compose.prod.yml
environment:
  - DEBUG=True
  - LOG_LEVEL=DEBUG
```

**Note**: Always disable debug mode in production!

### Getting Help
1. Check logs first
2. Verify configuration
3. Test individual components
4. Review this documentation
5. Check GitHub issues
6. Contact support team

## Maintenance

### Regular Tasks
- **Weekly**: Check log sizes and clean up
- **Monthly**: Update base images
- **Quarterly**: Review security configurations
- **Annually**: Disaster recovery testing

### Update Process
```bash
# 1. Backup current deployment
./scripts/backup.sh

# 2. Pull latest changes
git pull origin main

# 3. Update environment if needed
cp .env.prod .env.prod.backup

# 4. Build and deploy
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# 5. Run database migrations
docker-compose -f docker-compose.prod.yml exec api python -m alembic upgrade head

# 6. Verify deployment
./scripts/health-check.sh
```

This completes the production deployment guide. For additional support, refer to the troubleshooting section or contact the development team.