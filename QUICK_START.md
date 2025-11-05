# OMNIVID - Quick Start Guide

Get up and running in 5 minutes! 🚀

## 📋 Prerequisites Checklist

- [ ] Python 3.9+ installed
- [ ] Node.js 18+ installed
- [ ] Docker installed (for production)
- [ ] Redis installed or running via Docker
- [ ] FFmpeg installed (included in Docker)

---

## ⚡ Fastest Path to Running

### Option 1: Local Development (No Docker)

```powershell
# 1. Setup backend
cd C:\Users\HP\Desktop\omnivid\backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 2. Start Redis (choose one)
# Via Docker:
docker run -d -p 6379:6379 redis:latest
# Via WSL:
wsl redis-server

# 3. Configure
copy .env.example .env
notepad .env  # Update REMOTION_ROOT path

# 4. Start services (3 separate terminals)

# Terminal 1 - API
python main.py

# Terminal 2 - Worker
celery -A celery_app worker --loglevel=info --pool=solo

# Terminal 3 - Test
curl http://localhost:8000/health
```

### Option 2: Docker (Recommended)

```powershell
# 1. Navigate to project
cd C:\Users\HP\Desktop\omnivid

# 2. Start everything
docker-compose up -d

# 3. Check status
docker-compose ps

# 4. View logs
docker-compose logs -f

# 5. Test API
curl http://localhost:8000/health
```

---

## 🎬 Your First Render

### Via Python

```python
import requests

# Submit job
response = requests.post("http://localhost:8000/render", json={
    "output_filename": "test_video.mp4",
    "width": 1280,
    "height": 720,
    "fps": 30,
    "quality": "medium"
})

task_id = response.json()["task_id"]
print(f"Job ID: {task_id}")

# Check status
status = requests.get(f"http://localhost:8000/render/{task_id}")
print(status.json())
```

### Via cURL

```bash
# Submit
curl -X POST http://localhost:8000/render \
  -H "Content-Type: application/json" \
  -d '{"output_filename":"test.mp4","width":1280,"height":720}'

# Status
curl http://localhost:8000/render/{task_id}

# Download
curl http://localhost:8000/download/test.mp4 -o test.mp4
```

### Via Browser

1. Open http://localhost:8000/docs
2. Try `/render` endpoint
3. Fill in parameters
4. Click "Execute"

---

## 🧪 Test Everything

```powershell
cd backend
python test_remotion.py
```

Tests check:
- ✅ Node.js & FFmpeg installed
- ✅ Adapter initialization
- ✅ Asset management
- ✅ Rendering pipeline
- ✅ Export/import

---

## 🔍 Common Issues & Fixes

### "Redis connection failed"
```powershell
# Check if Redis is running
docker ps | findstr redis
# Or
Test-NetConnection localhost -Port 6379

# Start Redis
docker run -d -p 6379:6379 redis:latest
```

### "Node.js not found"
```powershell
# Check installation
node --version
npm --version

# Install if missing
# Download from https://nodejs.org
```

### "FFmpeg not found"
```powershell
# Check installation
ffmpeg -version

# Install via Chocolatey (Windows)
choco install ffmpeg

# Or download from https://ffmpeg.org
```

### "Port 8000 already in use"
```powershell
# Find process using port
netstat -ano | findstr :8000

# Kill process (replace PID)
taskkill /PID <PID> /F

# Or change port in .env
# PORT=8001
```

### "ModuleNotFoundError"
```powershell
# Ensure venv is activated
.\venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt
```

---

## 📊 Monitor Your System

### Check API Health
```powershell
curl http://localhost:8000/health
```

### Check Worker Health
```powershell
curl http://localhost:8000/health/celery
```

### View Active Tasks
```powershell
# Via Flower (if enabled)
# http://localhost:5555

# Via CLI
docker exec omnivid-celery-worker celery -A celery_app inspect active
```

### View Logs
```powershell
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f celery-worker
```

---

## 🎯 Quick Commands Reference

### Docker

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Restart
docker-compose restart

# Rebuild
docker-compose build --no-cache

# Scale workers
docker-compose up -d --scale celery-worker=3

# View logs
docker-compose logs -f [service_name]

# Execute command in container
docker exec -it omnivid-api bash
```

### Celery

```bash
# Start worker
celery -A celery_app worker --loglevel=info --pool=solo

# Inspect active tasks
celery -A celery_app inspect active

# Purge all tasks
celery -A celery_app purge

# Stats
celery -A celery_app inspect stats
```

### API

```bash
# Health check
GET /health

# Submit render
POST /render

# Get status
GET /render/{task_id}

# Get result
GET /render/{task_id}/result

# Cancel job
DELETE /render/{task_id}

# List outputs
GET /outputs

# Download file
GET /download/{filename}
```

---

## 🚀 Next Actions

1. **Verify Setup**
   - [ ] API responds at http://localhost:8000
   - [ ] Docs load at http://localhost:8000/docs
   - [ ] Health checks pass
   - [ ] Celery worker is running

2. **Test Render**
   - [ ] Submit a simple test job
   - [ ] Monitor status
   - [ ] Download result
   - [ ] Verify video plays

3. **Configure for Your Use**
   - [ ] Set up Remotion project
   - [ ] Update `.env` with correct paths
   - [ ] Test with your compositions
   - [ ] Add custom scenes

4. **Scale & Deploy**
   - [ ] Test with multiple workers
   - [ ] Monitor performance
   - [ ] Review DEPLOYMENT.md
   - [ ] Deploy to cloud

---

## 📚 Documentation Links

- **Full Backend Docs**: `backend/README.md`
- **Deployment Guide**: `DEPLOYMENT.md`
- **Project Summary**: `PROJECT_SUMMARY.md`
- **API Docs**: http://localhost:8000/docs

---

## 💡 Pro Tips

1. **Use Docker for consistency** - Eliminates "works on my machine"
2. **Monitor with Flower** - Visual task queue monitoring
3. **Scale workers dynamically** - Based on queue length
4. **Use quality presets** - Balance render time vs file size
5. **Clean up tmp files** - Prevent disk space issues
6. **Set proper timeouts** - Avoid stuck jobs
7. **Test locally first** - Before deploying to production
8. **Check logs often** - Early detection of issues

---

## 🆘 Need Help?

1. **Read the error message carefully**
2. **Check logs**: `docker-compose logs -f`
3. **Verify configuration**: `.env` file
4. **Test components individually**
5. **Review documentation**
6. **Run test suite**: `python test_remotion.py`

---

**You're all set! Start rendering amazing videos! 🎬✨**
