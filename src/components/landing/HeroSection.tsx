'use client';

import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { ArrowRight, CheckCircle2 } from 'lucide-react';
import Link from 'next/link';
import Image from 'next/image';
import { useGetStarted } from '@/hooks/useGetStarted';

export function HeroSection() {
  const { start } = useGetStarted();
  return (
    <section className="relative overflow-hidden py-20 sm:py-24">
      {/* Background effects */}
      <div className="absolute inset-0 bg-gradient-to-br from-violet-600/10 via-fuchsia-500/10 to-pink-600/10" />
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(120,119,198,0.2),rgba(255,255,255,0))]" />

      <div className="container relative z-10 px-4 mx-auto max-w-7xl sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-16 items-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center lg:text-left"
          >
            <div className="inline-flex items-center gap-2 px-4 py-2 mb-6 rounded-full bg-primary/10 border border-primary/20">
              <CheckCircle2 className="w-4 h-4 text-primary" />
              <span className="text-sm font-medium">No credit card required</span>
            </div>

            <h1 className="text-4xl md:text-6xl font-bold tracking-tight mb-6">
              <span className="bg-gradient-to-r from-violet-600 via-fuchsia-500 to-pink-600 bg-clip-text text-transparent">
                Instantly create stunning videos from text
              </span>
            </h1>

            <p className="text-lg text-muted-foreground mb-8 max-w-xl">
              OmniVid turns your ideas into professional-quality videos in seconds. Perfect for social media, marketing, education, and more.
            </p>

            <div className="flex flex-col sm:flex-row items-center gap-4">
              <Button
                size="lg"
                className="h-14 px-10 text-lg font-semibold bg-gradient-to-r from-violet-600 to-fuchsia-600 hover:from-violet-700 hover:to-fuchsia-700 shadow-lg shadow-violet-500/50 transition-all hover:shadow-xl hover:shadow-violet-500/60 hover:scale-105"
                onClick={() => start('/app/editor')}
              >
                <span className="flex items-center gap-2">
                  Start Free Trial
                  <ArrowRight className="w-5 h-5" />
                </span>
              </Button>
              <Button variant="outline" size="lg" className="h-14 px-10 text-lg font-semibold" asChild>
                <Link href="/templates">Explore Templates</Link>
              </Button>
            </div>

            <div className="mt-8 flex items-center justify-center lg:justify-start gap-8 text-muted-foreground">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-primary" />
                <span>Free forever plan</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-primary" />
                <span>Cancel anytime</span>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="relative"
          >
            <div className="relative aspect-video rounded-2xl overflow-hidden border border-border bg-card">
              <Image
                src="/images/hero-preview.jpg"
                alt="OmniVid Editor Preview"
                fill
                className="object-cover"
                priority
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/30 to-transparent" />
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
