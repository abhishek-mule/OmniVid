'use client';

import { Button } from '@/components/ui/button';
import {
  Sparkles,
  Zap,
  Video,
  BarChart2,
  Users,
  Clock,
  Layers,
  Palette,
  Settings,
  Shield,
  Globe,
  Workflow
} from 'lucide-react';
import Link from 'next/link';
import { Navbar } from '@/components/navbar';
import { Footer } from '@/components/footer';
import { useGetStarted } from '@/hooks/useGetStarted';

export default function Features() {
  const { start } = useGetStarted();
  const features = [
    {
      icon: <Sparkles className="h-6 w-6" />,
      title: 'AI-Powered Generation',
      description: 'Transform text prompts into professional videos using advanced AI models trained on millions of hours of video content.'
    },
    {
      icon: <Zap className="h-6 w-6" />,
      title: 'Lightning Fast Rendering',
      description: 'Generate videos in minutes with our optimized rendering pipeline. No more waiting hours for your content.'
    },
    {
      icon: <Layers className="h-6 w-6" />,
      title: 'Multi-Engine Support',
      description: 'Powered by Remotion, FFmpeg, and custom AI engines to deliver the highest quality output.'
    },
    {
      icon: <Palette className="h-6 w-6" />,
      title: 'Custom Branding',
      description: 'Add your logo, colors, and fonts to create videos that match your brand identity perfectly.'
    },
    {
      icon: <Video className="h-6 w-6" />,
      title: 'Multiple Formats',
      description: 'Export in any format or resolution you need, from social media to 8K cinema quality.'
    },
    {
      icon: <BarChart2 className="h-6 w-6" />,
      title: 'Advanced Analytics',
      description: 'Track video performance, engagement metrics, and viewer insights with detailed analytics.'
    },
    {
      icon: <Users className="h-6 w-6" />,
      title: 'Team Collaboration',
      description: 'Work together with your team in real-time. Share projects, leave comments, and manage permissions.'
    },
    {
      icon: <Clock className="h-6 w-6" />,
      title: 'Batch Processing',
      description: 'Generate multiple videos simultaneously to scale your content production effortlessly.'
    },
    {
      icon: <Settings className="h-6 w-6" />,
      title: 'API Access',
      description: 'Integrate OmniVid into your workflow with our comprehensive REST API and webhooks.'
    },
    {
      icon: <Shield className="h-6 w-6" />,
      title: 'Enterprise Security',
      description: 'Bank-level encryption, SOC 2 compliance, and SSO integration for enterprise peace of mind.'
    },
    {
      icon: <Globe className="h-6 w-6" />,
      title: 'Global CDN',
      description: 'Fast video delivery worldwide with our global content delivery network infrastructure.'
    },
    {
      icon: <Workflow className="h-6 w-6" />,
      title: 'Workflow Automation',
      description: 'Automate your video creation pipeline with triggers, templates, and scheduled rendering.'
    }
  ];

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      <main className="container mx-auto px-4 sm:px-6 lg:px-8 pt-32 pb-16">
        <div className="text-center mb-20">
          <h1 className="text-5xl font-bold tracking-tight sm:text-6xl md:text-7xl">
            Powerful features for
            <br />
            <span className="text-muted-foreground">professional creators</span>
          </h1>
          <p className="mt-6 text-lg text-muted-foreground max-w-2xl mx-auto">
            Everything you need to create, manage, and distribute stunning videos at scale.
          </p>
          <div className="mt-10">
            <Button size="lg" onClick={() => start('/app/editor')}>
              Start Creating Free
            </Button>
          </div>
        </div>

        <div className="grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-3 max-w-7xl mx-auto">
          {features.map((feature, index) => (
            <div
              key={index}
              className="group p-8 rounded-2xl border border-border bg-card hover:shadow-lg transition-all"
            >
              <div className="flex items-center justify-center w-14 h-14 mb-6 rounded-xl bg-primary text-primary-foreground">
                {feature.icon}
              </div>
              <h3 className="text-xl font-semibold mb-3">{feature.title}</h3>
              <p className="text-muted-foreground">{feature.description}</p>
            </div>
          ))}
        </div>

        <div className="mt-32 text-center">
          <div className="inline-block px-6 py-3 mb-6 rounded-full bg-muted border border-border">
            <span className="text-sm font-medium">Coming Soon</span>
          </div>
          <h2 className="text-3xl font-bold mb-6">More amazing features on the way</h2>
          <p className="text-muted-foreground max-w-2xl mx-auto mb-10">
            We are constantly innovating to bring you the best video creation experience.
            Join our community to shape the future of OmniVid.
          </p>
          <Button variant="outline" size="lg" asChild>
            <Link href="/roadmap">View Roadmap</Link>
          </Button>
        </div>
      </main>

      <Footer />
    </div>
  );
}
