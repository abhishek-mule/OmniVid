# 🎬 OmniVid - The AI Compiler for Video Creation

**OmniVid** is a premium, creator-first video generation platform that transforms natural language into stunning professional videos using AI. It combines a powerful backend AI compiler with a sleek, intuitive frontend built with Next.js 14, Framer Motion, and TailwindCSS.

> “Don’t edit videos — **compile them.**”

---

## 🚀 What Is It?

OmniVid is an **AI-driven, multi-engine video automation framework** that fuses:
- 🎬 **DaVinci Resolve** – cinematic editing & color
- 🧮 **Manim** – mathematical animations
- 💻 **Remotion** – React-based motion graphics
- 🌀 **Blender** – 3D procedural generation
- 🧩 **FFmpeg** – video orchestration & rendering

Together, they form the first-ever **AI compiler for visual storytelling**. A text prompt becomes code → code becomes animation → animation becomes a rendered video.

![alt text](image.png)


---

## ✨ Key Features

### 🎨 Cinematic Landing Page
- Animated gradient backgrounds with particle effects
- Bold hero section with dual CTAs
- Feature showcase with micro-interactions
- Step-by-step "How It Works" visualization
- Creator showcase gallery
- Responsive dark/light theme support

### 🎬 Video Generation Studio
- Natural language prompt input with smart suggestions
- Advanced controls: Resolution (720p-4K), FPS (24-60), Duration, Quality
- 6+ professional templates to choose from
- Real-time stage-by-stage progress tracking
- Animated generate button with magical effects
- Live video preview with playback controls

### 📊 Analytics Dashboard
- Overview stats: Videos, Watch Time, Views, Engagement
- Sortable video history with quick previews
- Status badges and action buttons
- Animated stat cards with gradient icons

### 🎭 Template Gallery
- 8+ professionally designed templates
- Filterable by category and style
- Real-time search functionality
- Star ratings and download counts
- Preview and "Use Template" CTAs

---

## 🧠 How It Works

```
User Prompt
│
▼
[LLM Parser]  →  Converts natural language → scene logic
│
▼
[AI Compiler] →  Generates engine-specific code (JS / PY / JSON)
│
▼
[Render Engines] →  Remotion | Manim | Blender | Resolve
│
▼
[FFmpeg Orchestrator] →  Final cinematic export
```

---

## ⚙️ Tech Stack

| Layer | Technology |
|--------|-------------|
| **Frontend** | Next.js 14, React, Tailwind CSS, Framer Motion |
| **UI Components** | Radix UI primitives, Lucide React |
| **State Management** | React Query |
| **Forms** | React Hook Form + Zod validation |
| **Database** | Supabase (PostgreSQL) |
| **Prompt Parsing** | Mixtral-8x7B / GPT-5 |
| **Core Engine** | Python 3.11 |
| **3D & VFX** | Blender + DaVinci Resolve |
| **Compositing** | FFmpeg |
| **Automation** | Python scripting APIs |

---

## 🧰 Quick Start

### Frontend

```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install

# Copy environment variables
cp .env.local.example .env.local

# Update with your Supabase credentials
# NEXT_PUBLIC_SUPABASE_URL=your_url
# NEXT_PUBLIC_SUPABASE_ANON_KEY=your_key

# Start development server
npm run dev

# Open http://localhost:3000
```

### Backend

```bash
# Navigate to the backend directory
# (Assuming a backend directory exists at the root)
cd ../backend

# Install dependencies
pip install -r requirements.txt

# Run a test render
python abhi_core/run.py "Create a logo reveal animation"
```

Enable DaVinci Resolve scripting (Studio version):
```
Preferences → System → General → External Scripting
```

---

## 🧭 Roadmap

* [x] LLM → Scene JSON parser
* [x] Remotion compiler
* [x] FFmpeg orchestrator
* [ ] DaVinci Resolve API automation
* [ ] Blender 3D node compiler
* [ ] Manim animation integration
* [ ] Web dashboard (Next.js)
* [ ] Cloud rendering & template marketplace

---

## ⚖️ License

MIT License — open for research, experimentation, and innovation.
