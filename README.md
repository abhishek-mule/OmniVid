🧠 AbhiAntrik (OMNIVID AI)

Stop editing videos. Start compiling them.

The Vision: AI Compiler for Video

AbhiAntrik — codename OMNIVID AI — is an experimental, open-source platform that acts as a universal AI compiler for video. It automates high-fidelity content creation by orchestrating professional rendering and editing engines based on natural language prompts.

Our goal is simple: Prompt → Code → Animation → Render.

We are building the first system capable of translating a simple text instruction into complex, multi-engine video production logic for cinematic, mathematical, and branded content.

⚙️ How It Works: The Orchestration Layer

AbhiAntrik breaks down a prompt into structured Scene JSON and compiles that data into native code for specialized back-end engines. This modular approach allows for the highest quality output across diverse formats.

Engine

Specialty

Compiler Output

Remotion

Web/Motion Graphics, Data Visualization

React/JavaScript

Manim

Scientific & Mathematical Animations

Python Code

Blender

Procedural 3D Modeling & Rendering

Python/Blend Scene

DaVinci Resolve

Professional Assembly, Color Grading, Transitions

Python Timeline Script

FFmpeg

Final Mix, Transcoding, Audio Composition

CLI Commands

Architecture Flow

graph TD
    A[User Prompt] --> B(LLM Parser);
    B --> C{Scene JSON};
    C --> D[Remotion Compiler];
    C --> E[Manim Compiler];
    C --> F[Blender Compiler];
    C --> G[Resolve Compiler];
    D --> R1(JS/React Video);
    E --> R2(Python Animation);
    F --> R3(3D Scene/Asset);
    G --> H(Python Timeline);
    H --> I(Final MP4/Video);
    R1 --> I;
    R2 --> I;
    R3 --> I;
    I --> J(FFmpeg Orchestrator);
    J --> K(Final Render Output);


🚀 Key Differentiators

Use Case

Status

AbhiAntrik Advantage

Branding

In Progress

Auto-generate hundreds of branded intros/outros using Remotion templates.

Education

Prototype

Compile complex equations or algorithms directly into Manim visual logic.

Cinematics

Prototype

Procedurally generate 3D assets (Blender) and assemble them with professional grade (Resolve) color and sound.

Scalability

Core Feature

Automate A/B testing and batch rendering of thousands of video variants.

🛠️ Quick Setup for Developers

This project is built primarily on Python 3.11 for the core orchestration and React/Node for the Remotion layer.

1. Clone & Dependencies

# Get the repository
git clone [https://github.com/abhi-antrik/omnivid-ai.git](https://github.com/abhi-antrik/omnivid-ai.git)
cd omnivid-ai

# Python dependencies (Orchestrator, Manim, Compilers)
pip install -r requirements.txt

# Node/Remotion dependencies (Web-based rendering)
npm install


2. Run the CLI

The primary interface is the abhi command line utility.

# Example: Generate a quick animation
abhi run "Create a logo reveal with a 2-second glow effect."

# Example: Process a structured JSON scene file
abhi run ./scene_drafts/cinematic_intro.json


⚠️ DaVinci Resolve Integration Note

For full DaVinci Resolve automation, you must be running the Resolve Studio version and enable the Python scripting API under Preferences → System → General → External Scripting.

🧑‍💻 Author & License

Creator: Abhishek Mule

Philosophy: Building the AI Compiler for the Creative Era.

License: MIT License. Open for experimentation and research use.
