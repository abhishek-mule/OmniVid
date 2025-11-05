# OMNIVID Deployment Guide

Complete guide for deploying OMNIVID to production using Docker.

## 🐳 Docker Deployment

### Prerequisites
- Docker 20.10+ installed
- Docker Compose V2 installed
- At least 4GB RAM available
- 10GB disk space

### Quick Start

```bash
# 1. Clone or navigate to project
cd omnivid

# 2. Build and start all services
docker-compose up -d

# 3. Check status
docker-compose ps

# 4. View logs
docker-compose logs -f
```

### Services

The stack includes:
- **API** (port 8000) - FastAPI REST API
- **Celery Worker** - Background task processing
- **Redis** (port 6379) - Message broker
- **Flower** (port 5555) - Optional monitoring UI

### Accessing Services

- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Flower** (if enabled): http://localhost:5555

### Enable Monitoring

```bash
# Start with Flower monitoring
docker-compose --profile monitoring up -d
```

## 🔧 Configuration

### Environment Variables

Create `.env` file in backend directory:

```env
# Application
DEBUG=False
APP_NAME=OMNIVID
APP_VERSION=0.1.0

# Server
HOST=0.0.0.0
PORT=8000

# Remotion
REMOTION_ROOT=/path/to/remotion/project
REMOTION_COMPOSITION_ID=MyComposition

# Redis
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Storage
OUTPUT_DIR=/app/output
ASSETS_DIR=/app/assets
TEMP_DIR=/app/tmp
```

## 📊 Scaling

### Scale Celery Workers

```bash
# Scale to 3 workers
docker-compose up -d --scale celery-worker=3

# Check running workers
docker-compose ps celery-worker
```

### Resource Limits

Edit `docker-compose.yml`:

```yaml
services:
  celery-worker:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
```

## 🌐 Production Deployment

### Option 1: Railway

1. **Install Railway CLI**
```bash
npm i -g @railway/cli
```

2. **Login and Initialize**
```bash
railway login
railway init
```

3. **Deploy**
```bash
railway up
```

4. **Add Services**
- Add Redis from Railway marketplace
- Configure environment variables
- Deploy API and workers separately

### Option 2: Render

1. **Create `render.yaml`**
```yaml
services:
  - type: web
    name: omnivid-api
    env: docker
    dockerfilePath: ./backend/Dockerfile
    envVars:
      - key: REDIS_URL
        fromService:
          name: redis
          type: redis
          property: connectionString

  - type: worker
    name: omnivid-worker
    env: docker
    dockerfilePath: ./backend/Dockerfile
    dockerCommand: celery -A celery_app worker --loglevel=info

  - type: redis
    name: redis
    ipAllowList: []
```

2. **Deploy**
- Connect GitHub repo
- Render auto-deploys on push

### Option 3: AWS ECS

1. **Build and Push Image**
```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build
docker build -t omnivid-backend ./backend

# Tag
docker tag omnivid-backend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/omnivid-backend:latest

# Push
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/omnivid-backend:latest
```

2. **Create ECS Service**
- Create task definition
- Configure API and worker tasks
- Set up Application Load Balancer
- Configure ElastiCache Redis

### Option 4: DigitalOcean App Platform

1. **Create `app.yaml`**
```yaml
name: omnivid
services:
  - name: api
    github:
      repo: your-username/omnivid
      branch: main
      deploy_on_push: true
    dockerfile_path: backend/Dockerfile
    http_port: 8000
    instance_count: 1
    instance_size_slug: basic-xxs
    
  - name: worker
    github:
      repo: your-username/omnivid
      branch: main
    dockerfile_path: backend/Dockerfile
    run_command: celery -A celery_app worker --loglevel=info
    instance_count: 1
    instance_size_slug: basic-xs

databases:
  - name: redis
    engine: REDIS
```

2. **Deploy via CLI or UI**
```bash
doctl apps create --spec app.yaml
```

## 🔒 Security

### Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Use strong `API_KEY`
- [ ] Configure CORS properly
- [ ] Use HTTPS/TLS
- [ ] Secure Redis with password
- [ ] Use environment secrets manager
- [ ] Set up rate limiting
- [ ] Enable logging and monitoring
- [ ] Regular security updates

### Secure Redis

```yaml
services:
  redis:
    command: redis-server --requirepass ${REDIS_PASSWORD}
    environment:
      - REDIS_PASSWORD=${REDIS_PASSWORD}
```

## 📈 Monitoring

### Health Checks

```bash
# API health
curl http://localhost:8000/health

# Celery health
curl http://localhost:8000/health/celery
```

### Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f celery-worker

# Last 100 lines
docker-compose logs --tail=100
```

### Metrics with Flower

Access Flower at http://localhost:5555 to monitor:
- Active tasks
- Task history
- Worker status
- Queue lengths

## 🔄 Updates

### Deploy New Version

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Or with zero-downtime
docker-compose build
docker-compose up -d --no-deps --build api
docker-compose up -d --no-deps --build celery-worker
```

## 🧹 Maintenance

### Cleanup

```bash
# Remove stopped containers
docker-compose down

# Remove volumes (WARNING: deletes data)
docker-compose down -v

# Remove images
docker-compose down --rmi all
```

### Backup

```bash
# Backup output files
docker cp omnivid-api:/app/output ./backup/output

# Backup Redis data
docker exec omnivid-redis redis-cli SAVE
docker cp omnivid-redis:/data/dump.rdb ./backup/
```

## 🐛 Troubleshooting

### API Won't Start

```bash
# Check logs
docker-compose logs api

# Common issues:
# 1. Port 8000 already in use
# 2. Redis connection failed
# 3. Missing environment variables
```

### Worker Not Processing Jobs

```bash
# Check worker logs
docker-compose logs celery-worker

# Verify Redis connection
docker exec omnivid-redis redis-cli ping

# Check queues
docker exec omnivid-celery-worker celery -A celery_app inspect active
```

### Out of Memory

```bash
# Check resource usage
docker stats

# Increase limits in docker-compose.yml
# or scale down workers
```

## 📞 Support

For issues:
1. Check logs: `docker-compose logs`
2. Verify configuration: `docker-compose config`
3. Test services individually
4. Review GitHub issues

## 🔗 Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Celery Best Practices](https://docs.celeryq.dev/en/stable/userguide/tasks.html#best-practices)
