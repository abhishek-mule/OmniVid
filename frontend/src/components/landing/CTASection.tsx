'use client';

import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { ArrowRight, Sparkles } from 'lucide-react';
import Link from 'next/link';

export function CTASection() {
  return (
    <section className="relative py-24 sm:py-32 overflow-hidden">
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-violet-600/10 via-fuchsia-500/10 to-pink-600/10" />
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(120,119,198,0.2),rgba(255,255,255,0))]" />

      <div className="container relative z-10 px-4 mx-auto max-w-7xl sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="relative overflow-hidden rounded-3xl border border-border bg-card/50 backdrop-blur-xl p-12 md:p-16 lg:p-20"
        >
          {/* Decorative elements */}
          <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-violet-500/20 to-transparent rounded-full blur-3xl" />
          <div className="absolute bottom-0 left-0 w-64 h-64 bg-gradient-to-tr from-fuchsia-500/20 to-transparent rounded-full blur-3xl" />

          <div className="relative text-center">
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ delay: 0.2 }}
              className="inline-flex items-center gap-2 px-4 py-2 mb-8 rounded-full bg-primary/10 border border-primary/20"
            >
              <Sparkles className="w-4 h-4 text-primary" />
              <span className="text-sm font-medium">Limited Time Offer</span>
            </motion.div>

            <h2 className="text-4xl font-bold tracking-tight sm:text-5xl md:text-6xl mb-6">
              <span className="bg-gradient-to-r from-violet-600 via-fuchsia-500 to-pink-600 bg-clip-text text-transparent">
                Ready to Create?
              </span>
            </h2>

            <p className="max-w-2xl mx-auto text-xl text-muted-foreground mb-10">
              Join thousands of creators who are already making magic with OmniVid.
              Start your free trial today—no credit card required.
            </p>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.4 }}
              className="flex flex-col sm:flex-row items-center justify-center gap-4"
            >
              <Button
                size="lg"
                className="h-14 px-10 text-lg font-semibold bg-gradient-to-r from-violet-600 to-fuchsia-600 hover:from-violet-700 hover:to-fuchsia-700 shadow-lg shadow-violet-500/50 transition-all hover:shadow-xl hover:shadow-violet-500/60 hover:scale-105"
                asChild
              >
                <Link href="/generate" className="flex items-center gap-2">
                  Get Started Free
                  <ArrowRight className="w-5 h-5" />
                </Link>
              </Button>
              <Button
                variant="outline"
                size="lg"
                className="h-14 px-10 text-lg font-semibold border-2"
                asChild
              >
                <Link href="/templates">Browse Templates</Link>
              </Button>
            </motion.div>

            <p className="mt-8 text-sm text-muted-foreground">
              🎉 Free forever plan available • 💳 No credit card required • ⚡ Cancel anytime
            </p>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
