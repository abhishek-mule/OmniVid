# OmniVid - Cinematic Video Generation Platform

## 🎬 Overview

OmniVid is a premium, creator-first video generation platform that transforms natural language descriptions into stunning, professional videos using AI. Built with Next.js 14, React, Framer Motion, and TailwindCSS, it delivers a magical, intuitive user experience without complexity.

## ✨ Key Features

### 1. **Cinematic Landing Page**
- Animated gradient backgrounds with particle effects
- Bold hero section with clear CTAs
- Feature showcase with micro-interactions
- "How It Works" section with step-by-step visualization
- Creator showcase gallery
- Responsive design with dark/light theme support

### 2. **Video Generation Studio**
- **Natural Language Input**: Describe your video in plain English
- **Prompt Editor**: Smart suggestions and character counter
- **Template Selection**: Choose from 6+ professionally designed templates
- **Advanced Controls**:
  - Resolution: 720p, 1080p, 2K, 4K
  - Frame Rate: 24, 30, 60 FPS
  - Duration: 5-60 seconds (adjustable slider)
  - Quality: Fast, Balanced, Best
- **Real-time Progress Tracking**: Stage-by-stage visualization
- **Animated Generate Button**: Magical micro-interactions
- **Live Preview**: Video preview with playback controls

### 3. **Dashboard**
- **Analytics Overview**:
  - Total videos created
  - Watch time statistics
  - Total views and engagement metrics
  - Trend indicators (+/- percentages)
- **Video History**:
  - Sortable grid/list view
  - Quick preview on hover
  - Status badges (completed, processing, failed)
  - Action buttons (Play, Download, Share)
- **Stats Cards**: Animated with gradient icons

### 4. **Template Gallery**
- **Filterable Categories**:
  - Marketing, Business, Education
  - Entertainment, Technology, Lifestyle
- **Style Filters**:
  - Modern, Cinematic, Corporate
  - Vibrant, Minimal, Creative
- **Search Functionality**: Real-time template search
- **Template Cards**:
  - Preview thumbnails with gradient backgrounds
  - Rating system (star ratings)
  - Download counts
  - Tag system for easy discovery
  - "Use Template" CTA

### 5. **Authentication & Profile** (Ready for Integration)
- Secure auth flow
- User profile settings
- Subscription management
- Usage analytics

## 🎨 Design System

### Color Palette
```css
/* Primary Gradients */
--gradient-primary: linear-gradient(to right, #7c3aed, #db2777);
--gradient-hero: linear-gradient(to bottom right, #7c3aed/20, #db2777/20);

/* Component Colors */
--violet: #7c3aed
--fuchsia: #db2777
--pink: #ec4899
--cyan: #06b6d4
--amber: #f59e0b
```

### Typography
- **Headings**: Bold, tracking-tight
- **Body**: Leading-relaxed for readability
- **Gradients**: Used for emphasis on key headings

### Animations
- **Framer Motion**: Smooth page transitions
- **Micro-interactions**: Hover effects, scale transforms
- **Loading States**: Rotating spinners, progress bars
- **Entrance Animations**: Staggered fade-ins

## 📁 Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── page.tsx                 # Landing page
│   │   ├── generate/
│   │   │   └── page.tsx            # Video generation studio
│   │   ├── dashboard/
│   │   │   └── page.tsx            # User dashboard
│   │   └── templates/
│   │       └── page.tsx            # Template gallery
│   ├── components/
│   │   ├── landing/
│   │   │   ├── HeroSection.tsx
│   │   │   ├── FeaturesSection.tsx
│   │   │   ├── HowItWorksSection.tsx
│   │   │   ├── ShowcaseSection.tsx
│   │   │   └── CTASection.tsx
│   │   ├── generate/
│   │   │   ├── VideoGeneratorStudio.tsx
│   │   │   ├── PromptEditor.tsx
│   │   │   ├── VideoControls.tsx
│   │   │   ├── TemplateSelector.tsx
│   │   │   ├── ProgressTracker.tsx
│   │   │   └── VideoPreview.tsx
│   │   ├── dashboard/
│   │   │   └── DashboardOverview.tsx
│   │   ├── templates/
│   │   │   ├── TemplateGallery.tsx
│   │   │   └── TemplateFilters.tsx
│   │   └── ui/                     # Reusable UI components
│   ├── hooks/
│   │   └── use-toast.ts           # Toast notification system
│   └── lib/
│       └── utils.ts               # Utility functions
```

## 🚀 Getting Started

### Prerequisites
```bash
Node.js 18+ 
npm or yarn
```

### Installation
```bash
cd frontend
npm install
```

### Development
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

### Build
```bash
npm run build
npm start
```

## 🔧 Required Dependencies

### Core Dependencies
```json
{
  "next": "14.0.4",
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "framer-motion": "^10.18.0",
  "lucide-react": "^0.294.0"
}
```

### UI Components (Radix UI)
```bash
npm install @radix-ui/react-dialog
npm install @radix-ui/react-dropdown-menu
npm install @radix-ui/react-label
npm install @radix-ui/react-slot
npm install @radix-ui/react-toast
npm install @radix-ui/react-tabs
npm install @radix-ui/react-slider
npm install @radix-ui/react-progress
```

### Styling
```bash
npm install tailwindcss-animate
npm install class-variance-authority
npm install clsx tailwind-merge
```

## 🎯 Next Steps for Integration

### 1. Remotion Integration
```typescript
// Install Remotion
npm install remotion

// Create video compositions
import { Composition } from 'remotion';

// Example composition structure
export const RemotionRoot = () => {
  return (
    <>
      <Composition
        id="VideoTemplate"
        component={VideoTemplate}
        durationInFrames={150}
        fps={30}
        width={1920}
        height={1080}
      />
    </>
  );
};
```

### 2. Backend API Integration
```typescript
// Update lib/api.ts
export const videoApi = {
  create: async (request: VideoCreateRequest) => {
    const response = await fetch('/api/videos/create', {
      method: 'POST',
      body: JSON.stringify(request),
    });
    return response.json();
  },
  
  getProgress: async (videoId: string) => {
    const response = await fetch(`/api/videos/${videoId}/progress`);
    return response.json();
  },
};
```

### 3. WebSocket for Real-time Updates
```typescript
// hooks/useVideoWebSocket.ts
export function useVideoWebSocket(videoId: string | null) {
  const [progress, setProgress] = useState(0);
  const [stage, setStage] = useState('');
  
  useEffect(() => {
    if (!videoId) return;
    
    const ws = new WebSocket(`ws://your-api/videos/${videoId}`);
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setProgress(data.progress);
      setStage(data.stage);
    };
    
    return () => ws.close();
  }, [videoId]);
  
  return { progress, stage };
}
```

### 4. Authentication
```typescript
// Use NextAuth.js or Supabase Auth
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);
```

## 🎨 Customization

### Theme Colors
Edit `tailwind.config.js`:
```javascript
theme: {
  extend: {
    colors: {
      primary: {
        DEFAULT: 'hsl(var(--primary))',
        foreground: 'hsl(var(--primary-foreground))',
      },
    },
  },
}
```

### Animation Timing
Adjust Framer Motion variants in components:
```typescript
const variants = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.8 }, // Adjust duration
};
```

## 📱 Responsive Design

All components are fully responsive with breakpoints:
- **Mobile**: < 768px
- **Tablet**: 768px - 1024px
- **Desktop**: > 1024px

## 🌙 Dark/Light Theme

Theme switching is built-in using `next-themes`:
```typescript
import { ThemeProvider } from 'next-themes';

// Wrap app in layout.tsx
<ThemeProvider attribute="class" defaultTheme="system">
  {children}
</ThemeProvider>
```

## 🔐 Security Best Practices

- Environment variables for API keys
- Input sanitization
- Rate limiting on API routes
- Secure file uploads
- CORS configuration

## 📊 Performance Optimization

- Image optimization with Next.js Image
- Code splitting with dynamic imports
- Lazy loading for heavy components
- Memoization with React.memo
- Virtual scrolling for large lists

## 🐛 Troubleshooting

### Missing Dependencies
```bash
npm install @radix-ui/react-progress @radix-ui/react-slider @radix-ui/react-tabs
```

### TypeScript Errors
Ensure `tsconfig.json` has correct paths:
```json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

## 📄 License

MIT License - feel free to use for commercial projects

## 🤝 Contributing

Contributions welcome! Please follow the existing code style and component patterns.

---

**Built with ❤️ for creators who demand the best**
