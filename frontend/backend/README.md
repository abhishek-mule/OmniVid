# OMNIVID Backend

AI-powered video generation and orchestration API built with FastAPI, Celery, and multi-engine rendering support.

## 🏗️ Architecture

```
omnivid/backend/
├── base_engine.py       # Abstract base adapter
├── remotion_adapter.py  # Remotion implementation
├── celery_app.py        # Task queue
├── main.py              # FastAPI application
├── config.py            # Configuration management
├── test_remotion.py     # Test suite
└── requirements.txt     # Dependencies
```

## ⚙️ Prerequisites

- **Python 3.9+**
- **Node.js 18+** (for Remotion)
- **Redis** (for Celery broker)
- **Remotion project** (see setup below)

## 📦 Installation

### 1. Install Python Dependencies

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 2. Install Redis

**Option A: Using Windows Subsystem for Linux (WSL)**
```bash
sudo apt-get update
sudo apt-get install redis-server
redis-server
```

**Option B: Using Docker**
```powershell
docker run -d -p 6379:6379 redis:latest
```

**Option C: Download Windows build**
- Download from: https://github.com/microsoftarchive/redis/releases

### 3. Setup Remotion Project

```powershell
# Navigate to frontend or separate directory
cd ../frontend

# Create Remotion project
npx create-video@latest

# Or use existing project
cd your-remotion-project

# Install dependencies
npm ci
```

### 4. Configure Environment

```powershell
# Copy example env file
cp .env.example .env

# Edit .env with your settings
notepad .env
```

Update these critical values:
- `REMOTION_ROOT`: Path to your Remotion project
- `REMOTION_COMPOSITION_ID`: Your composition name

## 🚀 Running the Application

### Start Redis (if not already running)
```powershell
# If using WSL
wsl redis-server

# Or using Docker
docker start <redis-container-id>
```

### Start Celery Worker
```powershell
# In one terminal (with venv activated)
celery -A celery_app worker --loglevel=info --pool=solo
```

### Start FastAPI Server
```powershell
# In another terminal (with venv activated)
python main.py

# Or using uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 🧪 Testing

### Run Test Suite
```powershell
python test_remotion.py
```

The test suite validates:
- ✅ Environment setup (Node.js, Remotion)
- ✅ Adapter initialization
- ✅ Asset management
- ✅ Scene configuration
- ✅ Effects & animations
- ✅ Render configuration
- ✅ Full render pipeline
- ✅ Export/import functionality

### Quick API Test
```powershell
# Check health
curl http://localhost:8000/health

# Check API docs
# Open browser to http://localhost:8000/docs
```

## 📡 API Endpoints

### Health Checks
- `GET /` - Root endpoint
- `GET /health` - API health status
- `GET /health/celery` - Celery worker health

### Rendering
- `POST /render` - Submit render job
- `GET /render/{task_id}` - Get render status
- `GET /render/{task_id}/result` - Get render result
- `DELETE /render/{task_id}` - Cancel render job

### File Management
- `GET /outputs` - List rendered videos
- `GET /download/{filename}` - Download video

## 💡 Usage Examples

### Example 1: Simple Render
```python
import requests

render_request = {
    "output_filename": "my_video.mp4",
    "width": 1920,
    "height": 1080,
    "fps": 30,
    "quality": "high"
}

# Submit job
response = requests.post("http://localhost:8000/render", json=render_request)
task_id = response.json()["task_id"]

# Check status
status = requests.get(f"http://localhost:8000/render/{task_id}")
print(status.json())
```

### Example 2: Render with Scenes and Assets
```python
render_request = {
    "output_filename": "complex_video.mp4",
    "width": 1280,
    "height": 720,
    "fps": 30,
    "quality": "high",
    "scenes": [
        {
            "name": "Intro",
            "duration": 5.0,
            "layers": [
                {"type": "text", "content": "Welcome to OMNIVID"},
                {"type": "background", "color": "#000000"}
            ]
        }
    ],
    "assets": [
        {
            "path": "C:/assets/logo.png",
            "type": "image",
            "id": "logo_asset"
        }
    ]
}

response = requests.post("http://localhost:8000/render", json=render_request)
```

### Example 3: Direct Adapter Usage
```python
from remotion_adapter import RemotionAdapter, RenderConfig

# Initialize adapter
adapter = RemotionAdapter(
    remotion_root="C:/projects/remotion",
    composition_id="MyComposition"
)
adapter.initialize()

# Configure render
config = RenderConfig(
    output_path="./output/video.mp4",
    width=1920,
    height=1080,
    fps=30,
    quality="high"
)

# Render
result = adapter.render(config)
print(f"Status: {result.status}")
print(f"Output: {result.output_path}")
```

## 🔧 Configuration

### Environment Variables

See `.env.example` for all available options.

**Key Settings:**

| Variable | Description | Default |
|----------|-------------|---------|
| `REMOTION_ROOT` | Path to Remotion project | Required |
| `REMOTION_COMPOSITION_ID` | Composition to render | `MyComposition` |
| `DEFAULT_QUALITY` | Quality preset | `high` |
| `RENDER_TIMEOUT` | Max render time (seconds) | `600` |
| `CELERY_BROKER_URL` | Redis connection string | `redis://localhost:6379/0` |

### Quality Presets

- `low` - CRF 28 (smaller files, lower quality)
- `medium` - CRF 23 (balanced)
- `high` - CRF 18 (recommended)
- `ultra` - CRF 15 (best quality, large files)

## 🐛 Troubleshooting

### Redis Connection Error
```
Error: Cannot connect to Redis
```
**Solution:** Ensure Redis is running on port 6379

### Remotion Not Found
```
Error: Remotion not installed in project
```
**Solution:** Run `npm ci` in your Remotion project directory

### Node.js Not Found
```
Error: Node.js not found or not working
```
**Solution:** Install Node.js 18+ from https://nodejs.org

### Import Errors
```
ModuleNotFoundError: No module named 'xxx'
```
**Solution:** Activate venv and run `pip install -r requirements.txt`

## 📊 Monitoring

### Celery Flower (Optional)
```powershell
pip install flower
celery -A celery_app flower
# Open http://localhost:5555
```

### View Task Queue
```python
from celery_app import celery_app

inspector = celery_app.control.inspect()
print(inspector.active())
print(inspector.scheduled())
```

## 🚦 Next Steps

1. ✅ Test RemotionAdapter with your Remotion project
2. ⬜ Implement FFmpegAdapter for advanced compositing
3. ⬜ Build BlenderAdapter for 3D rendering
4. ⬜ Add ManimAdapter for mathematical animations
5. ⬜ Create orchestration layer to route between engines
6. ⬜ Implement AI-powered scene generation
7. ⬜ Build template marketplace integration

## 📚 Additional Resources

- [Remotion Documentation](https://www.remotion.dev/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Celery Documentation](https://docs.celeryq.dev)
- [Redis Documentation](https://redis.io/docs)

## 📄 License

MIT License - See LICENSE file for details
