'use client';

import { Button } from '@/components/ui/button';
import { ArrowRight, Video, Sparkles, Zap, BarChart2, Play, Clock, Users } from 'lucide-react';
import Link from 'next/link';
import { Navbar } from '@/components/navbar';
import { Footer } from '@/components/footer';
import CreativeSlider from '@/components/CreativeSlider';

export default function Home() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      {/* Hero Section */}
      <section className="relative overflow-hidden pt-32 pb-16 sm:pt-40 sm:pb-24 lg:pt-48 lg:pb-32">
        <div className="container px-4 mx-auto max-w-7xl sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="relative px-4 mx-auto mt-20 max-w-6xl sm:px-6 lg:px-8">
              <div className="relative overflow-hidden rounded-2xl border border-border bg-card shadow-2xl">
                <div className="relative aspect-[16/9] bg-gradient-to-br from-muted/50 to-muted flex items-center justify-center">
                  <div className="text-center p-8">
                    <h1 className="text-4xl font-bold tracking-tight text-foreground sm:text-5xl md:text-6xl lg:text-7xl">
                      Create Stunning Videos
                      <br />
                      <span className="text-primary">with AI</span>
                    </h1>
                    <p className="max-w-2xl mx-auto mt-6 text-lg leading-relaxed text-muted-foreground">
                      Transform your ideas into professional videos in minutes. No editing experience required.
                    </p>
                    <div className="flex flex-col items-center justify-center mt-8 gap-4 sm:flex-row">
                      <Button size="lg" className="h-12 px-8" asChild>
                        <Link href="/dashboard" className="flex items-center gap-2">
                          Get Started Free <ArrowRight className="w-4 h-4" />
                        </Link>
                      </Button>
                      <Button variant="outline" size="lg" className="h-12 px-8" asChild>
                        <Link href="#demo" className="flex items-center gap-2">
                          <Play className="w-4 h-4" /> Watch Demo
                        </Link>
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <p className="mt-6 text-sm text-muted-foreground">
              No credit card required. Start creating instantly.
            </p>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}
