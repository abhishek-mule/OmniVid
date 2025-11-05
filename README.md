# ⚡ AbhiAntrik — The AI Compiler for Video Creation

**AbhiAntrik** (codename: **OMNIVID AI**) is building the future of how videos are made.  
No timelines. No templates. Just **type what you imagine**, and let the AI compile it into motion.

> “Don’t edit videos — **compile them.**”

---

## 🚀 What Is It?

AbhiAntrik is an **AI-driven, multi-engine video automation framework** that fuses:
- 🎬 **DaVinci Resolve** – cinematic editing & color  
- 🧮 **Manim** – mathematical animations  
- 💻 **Remotion** – React-based motion graphics  
- 🌀 **Blender** – 3D procedural generation  
- 🧩 **FFmpeg** – video orchestration & rendering  

Together, they form the first-ever **AI compiler for visual storytelling**.  
A text prompt becomes code → code becomes animation → animation becomes a rendered video.

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

````

---

## 🧩 Core Philosophy

> 🎥 **Prompt → Code → Render.**  
> The creative engine that bridges imagination and automation.

AbhiAntrik isn’t a video editor — it’s a **creative operating system**.  
Think of it as **Next.js + Unity + DaVinci Resolve**, fused into one AI brain.

---

## 💡 Use-Cases

| Use-Case | Description |
|-----------|--------------|
| 🎞️ **Brand Intros & Trailers** | Generate cinematic intros, logo reveals, and transitions. |
| 📚 **Educational Animations** | Turn math or code into animated explanations. |
| 🧠 **AI Template Generation** | Auto-create video templates from text. |
| 🧰 **Batch Video Production** | Automate 1000+ variations with different data/branding. |
| 🎬 **AI-Assisted Filmmaking** | Script → Scene JSON → Rendered visuals. |

---

## ⚙️ Tech Stack

| Layer | Technology |
|--------|-------------|
| **Prompt Parsing** | Mixtral-8x7B / GPT-5 |
| **Core Engine** | Python 3.11 |
| **Front-End** | React + Remotion |
| **3D & VFX** | Blender + DaVinci Resolve |
| **Compositing** | FFmpeg |
| **Automation** | Python scripting APIs |

---

## 🧠 Example Workflow

### 🗣️ Input Prompt
> “Make a glowing 3D intro that says ‘Welcome to AbhiAntrik’ and fades into a rotating Earth animation with ambient music.”

### 🧩 AI Output
```json
{
  "scenes": [
    {
      "engine": "Remotion",
      "type": "TextIntro",
      "effect": "Glow",
      "duration": 5
    },
    {
      "engine": "Blender",
      "type": "3DObject",
      "asset": "earth.glb",
      "rotation": [0, 1, 0],
      "duration": 7
    }
  ],
  "audio": "cinematic_ambient.mp3"
}
````

### 💻 CLI Command

```bash
abhi run "Create cinematic startup intro"
```

### 🎬 Output

* Text scene → Rendered via Remotion
* Earth scene → Generated via Blender
* Audio + transitions → Compiled with FFmpeg
* Final color & export → Automated in DaVinci Resolve

---

## 🧱 Project Structure

```
abhi_core/         → AI Orchestrator + LLM routing
parsers/           → Prompt → Scene JSON
compilers/         → Engine code generators
engines/           → Wrappers (Resolve, Blender, Remotion, Manim)
assets/            → Templates, transitions, SFX
cli/               → Command-line interface
```

---

## 🧰 Quick Start

```bash
# Clone the repo
git clone https://github.com/abhi-antrik/omnivid-ai.git
cd omnivid-ai

# Install dependencies
pip install -r requirements.txt
npm install

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

## 🧩 The Long Game

AbhiAntrik’s goal is to become the **AI Compiler for the Creative Era** —
where code, creativity, and computation converge.

* ⚙️ **Automation-first** design
* 🧠 **LLM-powered creativity**
* 🌐 **Cross-engine orchestration**
* 💰 **Marketplace-ready** architecture

---

## 🧑‍💻 Creator

**Abhishek Mule** — Builder of AbhiAntrik / OMNIVID AI
*AI Developer | Creative Technologist | Founder*

📧 `contact@abhiantrik.dev`
🌐 [https://abhiantrik.dev](https://abhiantrik.dev)

---

## ⚖️ License

MIT License — open for research, experimentation, and innovation.

---

### ✨ Tagline

> “Imagine. Compile. Create. — Welcome to the next era of video.”

```

---

Would you like me to make a **slightly shorter and cleaner GitHub version** (optimized for repo display and Markdown preview), or keep this **full cinematic README** style for portfolio/pitch deck?
```
