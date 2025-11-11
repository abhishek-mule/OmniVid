'use client';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Navbar } from '@/components/navbar';
import { Sparkles, Video, Zap, Shield, ArrowRight } from 'lucide-react';
import Link from 'next/link';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-primary/5 via-background to-secondary/5">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 pt-24 pb-16">
          <div className="max-w-4xl mx-auto text-center">
            <div className="mb-8">
              <h1 className="text-4xl sm:text-6xl font-bold tracking-tight bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
                Create Amazing Videos
                <br />
                with AI
              </h1>
              <p className="mt-6 text-xl text-muted-foreground max-w-2xl mx-auto">
                Transform your ideas into stunning videos in minutes. No editing skills required.
                Just describe what you want, and let our AI do the magic.
              </p>
            </div>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/create">
                <Button size="lg" className="h-12 px-8">
                  <Sparkles className="mr-2 h-5 w-5" />
                  Start Creating
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
              <Link href="/features">
                <Button variant="outline" size="lg" className="h-12 px-8">
                  Learn More
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 bg-muted/30">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold tracking-tight">Why Choose OmniVid?</h2>
            <p className="mt-4 text-lg text-muted-foreground">
              Everything you need to create professional videos effortlessly
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-6xl mx-auto">
            <Card>
              <CardHeader>
                <Video className="h-10 w-10 text-primary mb-2" />
                <CardTitle>AI-Powered Creation</CardTitle>
                <CardDescription>
                  Advanced AI algorithms generate high-quality videos from your text descriptions
                </CardDescription>
              </CardHeader>
            </Card>

            <Card>
              <CardHeader>
                <Zap className="h-10 w-10 text-primary mb-2" />
                <CardTitle>Lightning Fast</CardTitle>
                <CardDescription>
                  Create videos in minutes, not hours. Perfect for content creators and businesses
                </CardDescription>
              </CardHeader>
            </Card>

            <Card>
              <CardHeader>
                <Shield className="h-10 w-10 text-primary mb-2" />
                <CardTitle>Professional Quality</CardTitle>
                <CardDescription>
                  Studio-grade videos with customizable resolutions, frame rates, and styles
                </CardDescription>
              </CardHeader>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-2xl mx-auto text-center">
            <h2 className="text-3xl font-bold tracking-tight mb-4">
              Ready to Create Your First Video?
            </h2>
            <p className="text-lg text-muted-foreground mb-8">
              Join thousands of creators who trust OmniVid for their video needs
            </p>
            <Link href="/create">
              <Button size="lg" className="h-12 px-8">
                Get Started Now
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}