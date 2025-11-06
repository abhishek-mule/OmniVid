'use client';

import { Button } from '@/components/ui/button';
import { ArrowRight, Check, Video, Sparkles, Zap, BarChart2 } from 'lucide-react';
import Link from 'next/link';

export default function Home() {
  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <section className="relative overflow-hidden pt-24 pb-16 sm:pt-32 sm:pb-24 lg:pt-40 lg:pb-32">
        <div className="container px-4 mx-auto max-w-7xl sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl font-bold tracking-tight text-foreground sm:text-5xl md:text-6xl">
              Transform Your Ideas into
              <span className="text-primary"> Stunning Videos</span>
            </h1>
            <p className="max-w-2xl mx-auto mt-6 text-lg leading-8 text-muted-foreground">
              OmniVid AI helps you create professional-quality videos in minutes with the power of artificial intelligence.
              No technical skills required.
            </p>
            <div className="flex flex-col items-center justify-center mt-10 gap-y-4 sm:flex-row sm:gap-x-6">
              <Button size="lg" asChild>
                <Link href="/dashboard" className="flex items-center">
                  Get Started <ArrowRight className="w-4 h-4 ml-2" />
                </Link>
              </Button>
              <Button variant="outline" size="lg" asChild>
                <Link href="#features">
                  Learn More
                </Link>
              </Button>
            </div>
          </div>
        </div>
        <div className="relative px-4 mx-auto mt-16 max-w-7xl sm:px-6 lg:px-8">
          <div className="overflow-hidden rounded-xl shadow-2xl ring-1 ring-black/10">
            <div className="relative aspect-[16/9] bg-muted/50 flex items-center justify-center">
              <div className="text-center p-8">
                <Video className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
                <p className="text-muted-foreground">Your video preview will appear here</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-24 bg-background">
        <div className="container px-4 mx-auto max-w-7xl sm:px-6 lg:px-8">
          <div className="max-w-3xl mx-auto text-center">
            <h2 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
              Everything you need to create amazing videos
            </h2>
            <p className="mt-4 text-lg text-muted-foreground">
              OmniVid AI combines powerful AI with an intuitive interface to make video creation accessible to everyone.
            </p>
          </div>
          <div className="grid max-w-5xl grid-cols-1 gap-8 mx-auto mt-16 sm:grid-cols-2 lg:grid-cols-3">
            {[
              {
                icon: <Sparkles className="w-6 h-6 text-primary" />,
                title: 'AI-Powered Generation',
                description: 'Generate videos from text prompts or scripts using our advanced AI models.'
              },
              {
                icon: <Zap className="w-6 h-6 text-primary" />,
                title: 'Lightning Fast',
                description: 'Create videos in minutes, not hours. Our optimized pipeline delivers results quickly.'
              },
              {
                icon: <BarChart2 className="w-6 h-6 text-primary" />,
                title: 'Data-Driven Insights',
                description: 'Get analytics on your videos to understand viewer engagement and improve content.'
              }
            ].map((feature, index) => (
              <div key={index} className="p-6 rounded-xl bg-card">
                <div className="flex items-center justify-center w-12 h-12 mx-auto mb-4 rounded-full bg-primary/10">
                  {feature.icon}
                </div>
                <h3 className="text-lg font-semibold text-center text-foreground">
                  {feature.title}
                </h3>
                <p className="mt-2 text-center text-muted-foreground">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 bg-primary/5">
        <div className="container px-4 mx-auto max-w-7xl sm:px-6 lg:px-8">
          <div className="max-w-3xl mx-auto text-center">
            <h2 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
              Ready to create amazing videos?
            </h2>
            <p className="max-w-2xl mx-auto mt-4 text-lg text-muted-foreground">
              Join thousands of creators who are already using OmniVid AI to bring their ideas to life.
            </p>
            <div className="flex flex-col items-center justify-center mt-8 space-y-3 sm:space-y-0 sm:space-x-4 sm:flex-row">
              <Button size="lg" asChild>
                <Link href="/signup">
                  Get Started for Free <ArrowRight className="w-4 h-4 ml-2" />
                </Link>
              </Button>
              <Button variant="outline" size="lg" asChild>
                <Link href="/demo">
                  Watch Demo
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
