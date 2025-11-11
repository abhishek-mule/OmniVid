'use client';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Navbar } from '@/components/navbar';
import {
  Sparkles,
  Video,
  Zap,
  Shield,
  Palette,
  Clock,
  Globe,
  Download,
  CheckCircle,
  ArrowRight
} from 'lucide-react';
import Link from 'next/link';

export default function FeaturesPage() {
  const features = [
    {
      icon: Sparkles,
      title: 'AI-Powered Creation',
      description: 'Advanced AI algorithms generate high-quality videos from your text descriptions with professional editing and effects.'
    },
    {
      icon: Video,
      title: 'Multiple Formats',
      description: 'Create videos in various resolutions from HD to 4K, with customizable aspect ratios for different platforms.'
    },
    {
      icon: Zap,
      title: 'Lightning Fast',
      description: 'Generate videos in minutes instead of hours. Perfect for content creators, marketers, and businesses on tight deadlines.'
    },
    {
      icon: Palette,
      title: 'Custom Styling',
      description: 'Choose from various visual styles, color schemes, and animation presets to match your brand identity.'
    },
    {
      icon: Clock,
      title: 'Scheduled Generation',
      description: 'Queue multiple videos for generation and receive them when ready, perfect for batch content creation.'
    },
    {
      icon: Globe,
      title: 'Multi-Platform Ready',
      description: 'Optimized output formats for YouTube, TikTok, Instagram, LinkedIn, and other social media platforms.'
    },
    {
      icon: Shield,
      title: 'Secure & Private',
      description: 'Your content is processed securely with enterprise-grade encryption and privacy protection.'
    },
    {
      icon: Download,
      title: 'Easy Export',
      description: 'Download your videos in multiple formats with one click, ready for immediate use or further editing.'
    }
  ];

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-primary/5 via-background to-secondary/5">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 pt-24 pb-16">
          <div className="max-w-4xl mx-auto text-center">
            <div className="mb-8">
              <h1 className="text-4xl sm:text-6xl font-bold tracking-tight">
                Powerful Features for
                <br />
                <span className="bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
                  Video Creation
                </span>
              </h1>
              <p className="mt-6 text-xl text-muted-foreground max-w-2xl mx-auto">
                Everything you need to create stunning videos with AI. From concept to completion in minutes.
              </p>
            </div>

            <Link href="/create">
              <Button size="lg" className="h-12 px-8">
                <Sparkles className="mr-2 h-5 w-5" />
                Start Creating
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="py-16">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-7xl mx-auto">
            {features.map((feature, index) => (
              <Card key={index} className="h-full">
                <CardHeader>
                  <feature.icon className="h-10 w-10 text-primary mb-4" />
                  <CardTitle className="text-xl">{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-base">
                    {feature.description}
                  </CardDescription>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-16 bg-muted/30">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold tracking-tight">How It Works</h2>
            <p className="mt-4 text-lg text-muted-foreground">
              Create amazing videos in three simple steps
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            <div className="text-center">
              <div className="w-16 h-16 bg-primary rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-primary-foreground">1</span>
              </div>
              <h3 className="text-xl font-semibold mb-2">Describe Your Video</h3>
              <p className="text-muted-foreground">
                Write a detailed description of the video you want to create, including style, duration, and key elements.
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-primary rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-primary-foreground">2</span>
              </div>
              <h3 className="text-xl font-semibold mb-2">AI Generates</h3>
              <p className="text-muted-foreground">
                Our advanced AI processes your description and creates a professional video with animations and effects.
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-primary rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-primary-foreground">3</span>
              </div>
              <h3 className="text-xl font-semibold mb-2">Download & Share</h3>
              <p className="text-muted-foreground">
                Download your video in the perfect format and share it with your audience immediately.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-2xl mx-auto text-center">
            <h2 className="text-3xl font-bold tracking-tight mb-4">
              Ready to Experience the Power of AI Video Creation?
            </h2>
            <p className="text-lg text-muted-foreground mb-8">
              Join thousands of creators who have transformed their content workflow with OmniVid
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/create">
                <Button size="lg" className="h-12 px-8">
                  Start Creating Now
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
              <Link href="/pricing">
                <Button variant="outline" size="lg" className="h-12 px-8">
                  View Pricing
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}