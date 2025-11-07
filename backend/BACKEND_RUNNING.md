/pōī# 🎬 OmniVid Backend - Now Running!

## ✅ Backend Status: **RUNNING**

Your OmniVid backend server is now live and ready to handle requests!

---

## 📍 Server Information

- **API Server**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Alternative Docs**: http://localhost:8000/redoc
- **WebSocket**: ws://localhost:8000/ws/videos/{video_id}
- **Health Check**: http://localhost:8000/health

---

## 🚀 Available Endpoints

### Core Endpoints

#### 1. **Create Video**
```http
POST http://localhost:8000/api/videos/create
Content-Type: application/json

{
  "prompt": "Create a cinematic product showcase video",
  "settings": {
    "resolution": "1080p",
    "fps": 30,
    "duration": 15,
    "quality": "balanced",
    "template": "modern"
  }
}
```

**Response:**
```json
{
  "video_id": "uuid-here",
  "status": "queued",
  "message": "Video generation started"
}
```

#### 2. **Get Video Status**
```http
GET http://localhost:8000/api/videos/{video_id}/status
```

**Response:**
```json
{
  "video_id": "uuid-here",
  "status": "processing",
  "progress": 60,
  "stage": "Rendering video...",
  "output_url": null,
  "error": null
}
```

#### 3. **List All Videos**
```http
GET http://localhost:8000/api/videos
```

#### 4. **Delete Video**
```http
DELETE http://localhost:8000/api/videos/{video_id}
```

#### 5. **List Templates**
```http
GET http://localhost:8000/api/templates
```

#### 6. **Get Template Details**
```http
GET http://localhost:8000/api/templates/{template_id}
```

### WebSocket Connection

Connect to receive real-time progress updates:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/videos/{video_id}');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Progress:', data.progress);
  console.log('Stage:', data.stage);
  console.log('Status:', data.status);
};
```

---

## 🎯 Test the API

### Using cURL

```bash
# Create a video
curl -X POST http://localhost:8000/api/videos/create \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A modern product demo video",
    "settings": {
      "resolution": "1080p",
      "fps": 30,
      "duration": 15,
      "quality": "balanced"
    }
  }'

# Check health
curl http://localhost:8000/health

# List templates
curl http://localhost:8000/api/templates
```

### Using PowerShell

```powershell
# Create a video
$body = @{
    prompt = "A cinematic travel video"
    settings = @{
        resolution = "1080p"
        fps = 30
        duration = 15
        quality = "balanced"
    }
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/videos/create" `
    -Method Post `
    -Body $body `
    -ContentType "application/json"
```

---

## 🔌 Connect Frontend to Backend

Update your frontend `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

Then restart your frontend:

```bash
cd frontend
npm run dev
```

---

## 📊 Video Generation Stages

The backend simulates a 5-stage video generation process:

1. **Analyzing prompt...** (0-20%)
2. **Generating script...** (20-40%)
3. **Creating scenes...** (40-60%)
4. **Rendering video...** (60-80%)
5. **Finalizing...** (80-100%)

Each stage takes approximately 2 seconds (configurable).

---

## 🎨 Features Implemented

✅ **RESTful API** with FastAPI
✅ **WebSocket Support** for real-time updates
✅ **CORS Enabled** for frontend integration
✅ **Swagger Documentation** at `/docs`
✅ **Video Generation Simulation** with progress tracking
✅ **Template Management** endpoints
✅ **Health Check** endpoint
✅ **In-memory Storage** (ready for database integration)

---

## 🔧 Configuration

Backend settings are in `.env`:

```env
HOST=0.0.0.0
PORT=8000
DEBUG=False
CORS_ORIGINS=["http://localhost:3000"]
```

---

## 🛠️ Development Commands

```bash
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run backend
python simple_main.py

# View logs
# Server logs appear in terminal

# Stop server
# Press Ctrl+C in terminal
```

---

## 📚 API Documentation

Visit **http://localhost:8000/docs** for:
- Interactive API testing
- Request/response schemas
- Example payloads
- Try it out functionality

---

## 🔄 Next Steps

### 1. Test the API
Open http://localhost:8000/docs and try creating a video

### 2. Connect Frontend
Update frontend environment variables and restart

### 3. Monitor Progress
Watch real-time updates via WebSocket connection

### 4. Integrate Real Video Generation
Replace simulation with actual Remotion/FFmpeg rendering

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Kill process on port 8000
npx kill-port 8000
```

### CORS Issues
Check that frontend URL is in `CORS_ORIGINS` in the backend

### WebSocket Connection Failed
Ensure backend is running and WebSocket URL is correct

---

## 📝 Notes

- **Current Implementation**: Simulated video generation (no actual rendering)
- **Storage**: In-memory (videos lost on restart)
- **Authentication**: Not implemented (add for production)
- **Rate Limiting**: Not implemented (add for production)

---

## 🚀 Production Deployment

For production, you'll need:
1. Database (PostgreSQL/MongoDB)
2. Redis for caching
3. Celery for background tasks
4. Actual video rendering (Remotion/FFmpeg)
5. File storage (S3/Cloud Storage)
6. Authentication & authorization
7. Rate limiting
8. Monitoring & logging

---

**Your backend is ready! Start creating videos! 🎬✨**

Server running at: **http://localhost:8000**
Documentation: **http://localhost:8000/docs**
