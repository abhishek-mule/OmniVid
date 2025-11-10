# 🚀 OmniVid Platform Setup Guide

## Quick Start

### 1. Install Dependencies

```bash
cd frontend
npm install
```

This will install all required packages including the newly added:
- `@radix-ui/react-progress`
- `@radix-ui/react-slider`
- `@radix-ui/react-tabs`

### 2. Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to see the platform.

### 3. Build for Production

```bash
npm run build
npm start
```

## 📦 What's Included

### Pages
- **Landing Page** (`/`) - Cinematic hero, features, how it works, showcase, CTA
- **Video Generator** (`/generate`) - Full video creation studio
- **Dashboard** (`/dashboard`) - Analytics and video history
- **Templates** (`/templates`) - Filterable template gallery

### Components

#### Landing Page Components
- `HeroSection` - Animated hero with gradient backgrounds
- `FeaturesSection` - Feature cards with hover effects
- `HowItWorksSection` - Step-by-step process visualization
- `ShowcaseSection` - Video showcase gallery
- `CTASection` - Call-to-action with decorative elements

#### Video Generator Components
- `VideoGeneratorStudio` - Main studio layout
- `PromptEditor` - Natural language input with suggestions
- `VideoControls` - Resolution, FPS, duration, quality controls
- `TemplateSelector` - Template selection grid
- `ProgressTracker` - Real-time generation progress
- `VideoPreview` - Video preview with playback

#### Dashboard Components
- `DashboardOverview` - Stats cards and recent videos

#### Template Components
- `TemplateGallery` - Filterable template grid
- `TemplateFilters` - Category, style, and search filters

#### UI Components
- `Button`, `Badge`, `Card`, `Input`, `Textarea`
- `Progress`, `Slider`, `Tabs`
- `Dialog`, `DropdownMenu`, `Label`, `Toast`

## 🎨 Customization

### Update Theme Colors

Edit `src/app/globals.css`:

```css
@layer base {
  :root {
    --primary: 262 83% 58%; /* Violet */
    --primary-foreground: 0 0% 100%;
    /* Add your custom colors */
  }
}
```

### Modify Animations

Adjust Framer Motion settings in components:

```typescript
// Example: Slower animations
transition={{ duration: 1.2 }} // Default is 0.8
```

### Change Gradients

Update gradient classes in components:

```typescript
// From
className="bg-gradient-to-r from-violet-600 to-fuchsia-600"

// To your custom gradient
className="bg-gradient-to-r from-blue-600 to-cyan-600"
```

## 🔌 Backend Integration

### 1. Set Up Environment Variables

Create `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=your-supabase-url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-key
```

### 2. Update API Client

Edit `src/lib/api.ts`:

```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL;

export const videoApi = {
  create: async (request: VideoCreateRequest) => {
    const response = await fetch(`${API_URL}/api/videos/create`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });
    return response.json();
  },
  // Add more endpoints
};
```

### 3. WebSocket Integration

Update `src/hooks/useVideoWebSocket.ts`:

```typescript
const WS_URL = process.env.NEXT_PUBLIC_WS_URL;

export function useVideoWebSocket(videoId: string | null) {
  useEffect(() => {
    if (!videoId) return;
    
    const ws = new WebSocket(`${WS_URL}/videos/${videoId}`);
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      // Handle progress updates
    };
    
    return () => ws.close();
  }, [videoId]);
}
```

## 🎬 Remotion Integration (Optional)

### Install Remotion

```bash
npm install remotion
```

### Create Video Compositions

Create `src/remotion/compositions/`:

```typescript
// VideoTemplate.tsx
import { AbsoluteFill } from 'remotion';

export const VideoTemplate = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: 'white' }}>
      {/* Your video content */}
    </AbsoluteFill>
  );
};
```

### Register Compositions

```typescript
// remotion/index.ts
import { Composition } from 'remotion';
import { VideoTemplate } from './compositions/VideoTemplate';

export const RemotionRoot = () => {
  return (
    <Composition
      id="VideoTemplate"
      component={VideoTemplate}
      durationInFrames={150}
      fps={30}
      width={1920}
      height={1080}
    />
  );
};
```

## 🐛 Troubleshooting

### Module Not Found Errors

If you see TypeScript errors about missing modules:

```bash
# Clear cache and reinstall
rm -rf node_modules .next
npm install
```

### Build Errors

```bash
# Check for TypeScript errors
npm run build

# Fix common issues
npm run lint --fix
```

### Port Already in Use

```bash
# Kill process on port 3000
npx kill-port 3000

# Or use a different port
npm run dev -- -p 3001
```

## 📱 Mobile Optimization

The platform is fully responsive. Test on different devices:

- Mobile: < 768px
- Tablet: 768px - 1024px  
- Desktop: > 1024px

## 🚀 Deployment

### Vercel (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

### Docker

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

## 📊 Performance Tips

1. **Image Optimization**: Use Next.js `<Image>` component
2. **Code Splitting**: Use dynamic imports for heavy components
3. **Lazy Loading**: Implement for video previews
4. **Caching**: Configure proper cache headers
5. **CDN**: Use for static assets

## 🔒 Security Checklist

- [ ] Environment variables properly configured
- [ ] API routes protected with authentication
- [ ] Input validation on all forms
- [ ] Rate limiting implemented
- [ ] CORS properly configured
- [ ] File upload size limits set
- [ ] XSS protection enabled

## 📚 Additional Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [Framer Motion Guide](https://www.framer.com/motion/)
- [Radix UI Components](https://www.radix-ui.com/)
- [TailwindCSS Docs](https://tailwindcss.com/docs)

## 🤝 Support

For issues or questions:
1. Check the troubleshooting section
2. Review component documentation
3. Check browser console for errors

---

**Happy Creating! 🎬✨**
