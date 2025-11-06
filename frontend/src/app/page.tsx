'use client';

import { Button } from '@/components/ui/button';
import { ArrowRight, Video, Sparkles, Zap, BarChart2, Play, Clock, Users } from 'lucide-react';
import Link from 'next/link';
import { Navbar } from '@/components/navbar';
import { Footer } from '@/components/footer';
<<<<<<< Updated upstream
<<<<<<< Updated upstream
=======
import CreativeSlider from '@/components/CreativeSlider';
>>>>>>> Stashed changes
=======
import CreativeSlider from '@/components/CreativeSlider';
>>>>>>> Stashed changes

export default function Home() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      {/* Hero Section */}
      <section className="relative overflow-hidden pt-32 pb-16 sm:pt-40 sm:pb-24 lg:pt-48 lg:pb-32">
        <div className="container px-4 mx-auto max-w-7xl sm:px-6 lg:px-8">
          <div className="text-center">
<<<<<<< Updated upstream
<<<<<<< Updated upstream
            <div className="inline-flex items-center gap-2 px-3 py-1 mb-6 text-sm rounded-full bg-muted border border-border">
              <Sparkles className="w-3 h-3" />
              <span>AI-Powered Video Generation</span>
            </div>
            <h1 className="text-5xl font-bold tracking-tight text-foreground sm:text-6xl md:text-7xl lg:text-8xl">
              Create Videos
              <br />
              <span className="text-muted-foreground">in Minutes</span>
            </h1>
            <p className="max-w-2xl mx-auto mt-8 text-lg leading-relaxed text-muted-foreground">
              Transform ideas into professional videos with AI. No editing experience required.
              Just describe what you want, and watch your vision come to life.
            </p>
            <div className="flex flex-col items-center justify-center mt-10 gap-4 sm:flex-row">
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
            <p className="mt-6 text-sm text-muted-foreground">
              No credit card required. Start creating instantly.
            </p>
          </div>
        </div>
        <div className="relative px-4 mx-auto mt-20 max-w-6xl sm:px-6 lg:px-8">
          <div className="relative overflow-hidden rounded-2xl border border-border bg-card shadow-2xl">
            <div className="relative aspect-[16/9] bg-gradient-to-br from-muted/50 to-muted flex items-center justify-center">
              <div className="text-center p-8">
                <div className="inline-flex items-center justify-center w-20 h-20 mb-4 rounded-2xl bg-primary/10">
                  <Video className="w-10 h-10 text-primary" />
                </div>
                <p className="text-base text-muted-foreground">Demo video preview</p>
=======
            <CreativeSlider />
              <div className="inline-flex items-center gap-2 px-3 py-1 mb-6 text-sm rounded-full bg-muted border border-border">
                <Sparkles className="w-3 h-3" />
                <span>AI-Powered Video Generation</span>
>>>>>>> Stashed changes
              </div>
              <h1 className="text-5xl font-bold tracking-tight text-foreground sm:text-6xl md:text-7xl lg:text-8xl">
                Create Videos
                <br />
                <span className="text-muted-foreground">in Minutes</span>
              </h1>
              <p className="max-w-2xl mx-auto mt-8 text-lg leading-relaxed text-muted-foreground">
                Transform ideas into professional videos with AI. No editing experience required.
                Just describe what you want, and watch your vision come to life.
              </p>
              <div className="flex flex-col items-center justify-center mt-10 gap-4 sm:flex-row">
                <Button size="lg" className="h-12 px-8" asChild>
                  <Link href="/generate" className="flex items-center gap-2">
                    Get Started Free <ArrowRight className="w-4 h-4" />
                  </Link>
                </Button>
                <Button variant="outline" size="lg" className="h-12 px-8" asChild>
                  <Link href="#demo" className="flex items-center gap-2">
                    <Play className="w-4 h-4" /> Watch Demo
                  </Link>
                </Button>
              </div>
              <p className="mt-6 text-sm text-muted-foreground">
                No credit card required. Start creating instantly.
              </p>
            </div>
          </div>
<<<<<<< Updated upstream
        </div>

        <div className="container px-4 mx-auto mt-20 max-w-7xl sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-3">
            <div className="flex items-center gap-4 p-6 rounded-xl border border-border bg-card">
              <Clock className="w-10 h-10 text-primary" />
              <div>
                <div className="text-2xl font-bold">10x Faster</div>
                <div className="text-sm text-muted-foreground">Video creation speed</div>
              </div>
            </div>
            <div className="flex items-center gap-4 p-6 rounded-xl border border-border bg-card">
              <Users className="w-10 h-10 text-primary" />
              <div>
                <div className="text-2xl font-bold">50K+</div>
                <div className="text-sm text-muted-foreground">Active creators</div>
              </div>
            </div>
            <div className="flex items-center gap-4 p-6 rounded-xl border border-border bg-card">
              <Video className="w-10 h-10 text-primary" />
              <div>
                <div className="text-2xl font-bold">1M+</div>
                <div className="text-sm text-muted-foreground">Videos generated</div>
=======
            <CreativeSlider />
              <div className="inline-flex items-center gap-2 px-3 py-1 mb-6 text-sm rounded-full bg-muted border border-border">
                <Sparkles className="w-3 h-3" />
                <span>AI-Powered Video Generation</span>
>>>>>>> Stashed changes
              </div>
              <h1 className="text-5xl font-bold tracking-tight text-foreground sm:text-6xl md:text-7xl lg:text-8xl">
                Create Videos
                <br />
                <span className="text-muted-foreground">in Minutes</span>
              </h1>
              <p className="max-w-2xl mx-auto mt-8 text-lg leading-relaxed text-muted-foreground">
                Transform ideas into professional videos with AI. No editing experience required.
                Just describe what you want, and watch your vision come to life.
              </p>
              <div className="flex flex-col items-center justify-center mt-10 gap-4 sm:flex-row">
                <Button size="lg" className="h-12 px-8" asChild>
                  <Link href="/generate" className="flex items-center gap-2">
                    Get Started Free <ArrowRight className="w-4 h-4" />
                  </Link>
                </Button>
                <Button variant="outline" size="lg" className="h-12 px-8" asChild>
                  <Link href="#demo" className="flex items-center gap-2">
                    <Play className="w-4 h-4" /> Watch Demo
                  </Link>
                </Button>
              </div>
              <p className="mt-6 text-sm text-muted-foreground">
                No credit card required. Start creating instantly.
              </p>
            </div>
          </div>
<<<<<<< Updated upstream
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-32 bg-muted/30">
        <div className="container px-4 mx-auto max-w-7xl sm:px-6 lg:px-8">
          <div className="max-w-3xl mx-auto text-center mb-16">
            <h2 className="text-4xl font-bold tracking-tight text-foreground sm:text-5xl">
              Everything you need
            </h2>
            <p className="mt-4 text-lg text-muted-foreground">
              Powerful features designed for professional video creation
            </p>
          </div>
          <div className="grid max-w-6xl grid-cols-1 gap-6 mx-auto sm:grid-cols-2 lg:grid-cols-3">
            {[
              {
                icon: <Sparkles className="w-6 h-6" />,
                title: 'AI-Powered Generation',
                description: 'Transform text prompts into professional videos with advanced AI'
              },
              {
                icon: <Zap className="w-6 h-6" />,
                title: 'Lightning Fast Rendering',
                description: 'Generate videos in minutes with our optimized pipeline'
              },
              {
                icon: <BarChart2 className="w-6 h-6" />,
                title: 'Analytics Dashboard',
                description: 'Track performance and engagement metrics in real-time'
              },
              {
                icon: <Video className="w-6 h-6" />,
                title: 'Multiple Formats',
                description: 'Export in any format or resolution you need'
              },
              {
                icon: <Users className="w-6 h-6" />,
                title: 'Team Collaboration',
                description: 'Work together with your team seamlessly'
              },
              {
                icon: <Clock className="w-6 h-6" />,
                title: 'Batch Processing',
                description: 'Generate multiple videos simultaneously'
              }
            ].map((feature, index) => (
              <div key={index} className="group p-6 rounded-xl border border-border bg-card hover:shadow-lg transition-all">
                <div className="flex items-center justify-center w-12 h-12 mb-4 rounded-lg bg-primary text-primary-foreground">
                  {feature.icon}
                </div>
                <h3 className="text-lg font-semibold mb-2 text-foreground">
                  {feature.title}
                </h3>
                <p className="text-sm text-muted-foreground">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-32 bg-background">
        <div className="container px-4 mx-auto max-w-7xl sm:px-6 lg:px-8">
          <div className="relative overflow-hidden rounded-3xl border border-border bg-card p-12 sm:p-16">
            <div className="relative z-10 max-w-3xl mx-auto text-center">
              <h2 className="text-4xl font-bold tracking-tight text-foreground sm:text-5xl">
                Start creating today
              </h2>
              <p className="mt-6 text-lg text-muted-foreground">
                Join thousands of creators using OmniVid AI to transform their ideas into stunning videos.
              </p>
              <div className="flex flex-col items-center justify-center mt-10 gap-4 sm:flex-row">
                <Button size="lg" className="h-12 px-8" asChild>
                  <Link href="/dashboard">
                    Get Started Free <ArrowRight className="w-4 h-4 ml-2" />
                  </Link>
                </Button>
                <Button variant="outline" size="lg" className="h-12 px-8" asChild>
                  <Link href="/pricing">
                    View Pricing
                  </Link>
                </Button>
              </div>
=======
          <div className="relative px-4 mx-auto mt-20 max-w-6xl sm:px-6 lg:px-8">
            <div className="relative overflow-hidden rounded-2xl border border-border bg-card shadow-2xl">
              <div className="relative aspect-[16/9] bg-gradient-to-br from-muted/50 to-muted flex items-center justify-center">
                <div className="text-center p-8">
                  <div className="inline-flex items-center justify-center w-20 h-20 mb-4 rounded-2xl bg-primary/10">
                    <Video className="w-10 h-10 text-primary" />
                  </div>
                  <p className="text-base text-muted-foreground">Demo video preview</p>
                </div>
              </div>
>>>>>>> Stashed changes
=======
          <div className="relative px-4 mx-auto mt-20 max-w-6xl sm:px-6 lg:px-8">
            <div className="relative overflow-hidden rounded-2xl border border-border bg-card shadow-2xl">
              <div className="relative aspect-[16/9] bg-gradient-to-br from-muted/50 to-muted flex items-center justify-center">
                <div className="text-center p-8">
                  <div className="inline-flex items-center justify-center w-20 h-20 mb-4 rounded-2xl bg-primary/10">
                    <Video className="w-10 h-10 text-primary" />
                  </div>
                  <p className="text-base text-muted-foreground">Demo video preview</p>
                </div>
              </div>
>>>>>>> Stashed changes
            </div>
            <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent" />
          </div>
<<<<<<< Updated upstream
<<<<<<< Updated upstream
        </div>
      </section>

      <Footer />
    </div>
  );
}
=======
=======
>>>>>>> Stashed changes

          <div className="container px-4 mx-auto mt-20 max-w-7xl sm:px-6 lg:px-8">
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-3">
              <div className="flex items-center gap-4 p-6 rounded-xl border border-border bg-card">
                <Clock className="w-10 h-10 text-primary" />
                <div>
                  <div className="text-2xl font-bold">10x Faster</div>
                  <div className="text-sm text-muted-foreground">Video creation speed</div>
                </div>
              </div>
              <div className="flex items-center gap-4 p-6 rounded-xl border border-border bg-card">
                <Users className="w-10 h-10 text-primary" />
                <div>
                  <div className="text-2xl font-bold">50K+</div>
                  <div className="text-sm text-muted-foreground">Active creators</div>
                </div>
              </div>
              <div className="flex items-center gap-4 p-6 rounded-xl border border-border bg-card">
                <Video className="w-10 h-10 text-primary" />
                <div>
                  <div className="text-2xl font-bold">1M+</div>
                  <div className="text-sm text-muted-foreground">Videos generated</div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section id="features" className="py-32 bg-muted/30">
          <div className="container px-4 mx-auto max-w-7xl sm:px-6 lg:px-8">
            <div className="max-w-3xl mx-auto text-center mb-16">
              <h2 className="text-4xl font-bold tracking-tight text-foreground sm:text-5xl">
                Everything you need
              </h2>
              <p className="mt-4 text-lg text-muted-foreground">
                Powerful features designed for professional video creation
              </p>
            </div>
            <div className="grid max-w-6xl grid-cols-1 gap-6 mx-auto sm:grid-cols-2 lg:grid-cols-3">
              {[
                {
                  icon: <Sparkles className="w-6 h-6" />,
                  title: 'AI-Powered Generation',
                  description: 'Transform text prompts into professional videos with advanced AI'
                },
                {
                  icon: <Zap className="w-6 h-6" />,
                  title: 'Lightning Fast Rendering',
                  description: 'Generate videos in minutes with our optimized pipeline'
                },
                {
                  icon: <BarChart2 className="w-6 h-6" />,
                  title: 'Analytics Dashboard',
                  description: 'Track performance and engagement metrics in real-time'
                },
                {
                  icon: <Video className="w-6 h-6" />,
                  title: 'Multiple Formats',
                  description: 'Export in any format or resolution you need'
                },
                {
                  icon: <Users className="w-6 h-6" />,
                  title: 'Team Collaboration',
                  description: 'Work together with your team seamlessly'
                },
                {
                  icon: <Clock className="w-6 h-6" />,
                  title: 'Batch Processing',
                  description: 'Generate multiple videos simultaneously'
                }
              ].map((feature, index) => (
                <div key={index} className="group p-6 rounded-xl border border-border bg-card hover:shadow-lg transition-all">
                  <div className="flex items-center justify-center w-12 h-12 mb-4 rounded-lg bg-primary text-primary-foreground">
                    {feature.icon}
                  </div>
                  <h3 className="text-lg font-semibold mb-2 text-foreground">
                    {feature.title}
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    {feature.description}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-32 bg-background">
          <div className="container px-4 mx-auto max-w-7xl sm:px-6 lg:px-8">
            <div className="relative overflow-hidden rounded-3xl border border-border bg-card p-12 sm:p-16">
              <div className="relative z-10 max-w-3xl mx-auto text-center">
                <h2 className="text-4xl font-bold tracking-tight text-foreground sm:text-5xl">
                  Start creating today
                </h2>
                <p className="mt-6 text-lg text-muted-foreground">
                  Join thousands of creators using OmniVid AI to transform their ideas into stunning videos.
                </p>
                <div className="flex flex-col items-center justify-center mt-10 gap-4 sm:flex-row">
                  <Button size="lg" className="h-12 px-8" asChild>
                    <Link href="/dashboard">
                      Get Started Free <ArrowRight className="w-4 h-4 ml-2" />
                    </Link>
                  </Button>
                  <Button variant="outline" size="lg" className="h-12 px-8" asChild>
                    <Link href="/pricing">
                      View Pricing
                    </Link>
                  </Button>
                </div>
              </div>
              <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent" />
            </div>
          </div>
        </section>

        <Footer />
      </div>
    );
  }
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
