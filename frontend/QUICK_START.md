# 🚀 Quick Start Guide

## Installation (2 minutes)

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

## 📍 Navigation

| Route | Description |
|-------|-------------|
| `/` | Landing page with hero, features, showcase |
| `/generate` | Video generation studio |
| `/dashboard` | Analytics and video history |
| `/templates` | Template gallery with filters |

## 🎨 Key Components

### Landing Page Components
```typescript
import { HeroSection } from '@/components/landing/HeroSection';
import { FeaturesSection } from '@/components/landing/FeaturesSection';
import { HowItWorksSection } from '@/components/landing/HowItWorksSection';
import { ShowcaseSection } from '@/components/landing/ShowcaseSection';
import { CTASection } from '@/components/landing/CTASection';
```

### Video Generator Components
```typescript
import { VideoGeneratorStudio } from '@/components/generate/VideoGeneratorStudio';
import { PromptEditor } from '@/components/generate/PromptEditor';
import { VideoControls } from '@/components/generate/VideoControls';
import { TemplateSelector } from '@/components/generate/TemplateSelector';
import { ProgressTracker } from '@/components/generate/ProgressTracker';
import { VideoPreview } from '@/components/generate/VideoPreview';
```

### Dashboard Components
```typescript
import { DashboardOverview } from '@/components/dashboard/DashboardOverview';
```

### Template Components
```typescript
import { TemplateGallery } from '@/components/templates/TemplateGallery';
import { TemplateFilters } from '@/components/templates/TemplateFilters';
```

### UI Components
```typescript
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Progress } from '@/components/ui/progress';
import { Slider } from '@/components/ui/slider';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
```

## 🎯 Common Tasks

### Change Primary Color
Edit `src/app/globals.css`:
```css
:root {
  --primary: 262 83% 58%; /* Violet - change these values */
}
```

### Add New Template
Edit `src/components/generate/TemplateSelector.tsx`:
```typescript
const templates = [
  // Add new template
  {
    id: 'your-template',
    name: 'Your Template Name',
    description: 'Description',
    gradient: 'from-blue-500 to-cyan-600',
  },
  // ... existing templates
];
```

### Customize Animation Speed
In any component with Framer Motion:
```typescript
// Slower
transition={{ duration: 1.2 }}

// Faster
transition={{ duration: 0.4 }}
```

### Add New Feature Card
Edit `src/components/landing/FeaturesSection.tsx`:
```typescript
const features = [
  {
    icon: YourIcon,
    title: 'Feature Title',
    description: 'Feature description',
    gradient: 'from-color-500 to-color-600',
  },
  // ... existing features
];
```

## 🔧 Troubleshooting

### TypeScript Errors
```bash
# Restart TypeScript server in VS Code
Ctrl+Shift+P → "TypeScript: Restart TS Server"
```

### Port Already in Use
```bash
npx kill-port 3000
# or
npm run dev -- -p 3001
```

### Missing Dependencies
```bash
npm install @radix-ui/react-progress @radix-ui/react-slider @radix-ui/react-tabs
```

### Clear Cache
```bash
rm -rf .next node_modules
npm install
```

## 📚 Documentation Files

- `README.md` - Main documentation
- `PLATFORM_GUIDE.md` - Comprehensive platform guide
- `SETUP.md` - Detailed setup instructions
- `FEATURES.md` - Complete feature list
- `QUICK_START.md` - This file

## 🎨 Color Gradients Reference

```css
/* Primary Gradients */
violet-fuchsia: from-violet-600 to-fuchsia-600
violet-purple: from-violet-500 to-purple-600
cyan-blue: from-cyan-500 to-blue-600
pink-rose: from-pink-500 to-rose-600
amber-orange: from-amber-500 to-orange-600
green-emerald: from-green-500 to-emerald-600
```

## 🚀 Next Steps

1. **Install dependencies**: `npm install`
2. **Start dev server**: `npm run dev`
3. **Explore pages**: Visit `/`, `/generate`, `/dashboard`, `/templates`
4. **Customize**: Update colors, gradients, content
5. **Integrate backend**: Connect to your API
6. **Deploy**: Push to Vercel or your platform

## 💡 Pro Tips

- Use `Ctrl+K` in VS Code to search files quickly
- All components are in `src/components/`
- Pages use Next.js App Router in `src/app/`
- Tailwind classes are in `src/app/globals.css`
- Icons from `lucide-react` package

## 🎬 Ready to Create!

Your cinematic video generation platform is ready to go. Start the dev server and begin customizing!

```bash
npm run dev
```

**Happy Creating! ✨**
