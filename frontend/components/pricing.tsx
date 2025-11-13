'use client';

import { motion } from 'framer-motion';
import { Check, Sparkles, Zap, Crown } from 'lucide-react';
import { Button } from '@/components/ui/button';

const plans = [
  {
    name: 'Starter',
    price: '29',
    icon: Zap,
    description: 'Perfect for individuals and small projects',
    features: [
      '10 videos per month',
      'HD quality exports',
      'Basic AI templates',
      'Email support',
      '5GB storage',
    ],
    gradient: 'from-emerald-500 to-teal-500',
    popular: false,
  },
  {
    name: 'Pro',
    price: '79',
    icon: Sparkles,
    description: 'Best for professionals and growing teams',
    features: [
      '50 videos per month',
      '4K quality exports',
      'Advanced AI templates',
      'Priority support',
      '50GB storage',
      'Custom branding',
      'API access',
    ],
    gradient: 'from-cyan-500 to-blue-500',
    popular: true,
  },
  {
    name: 'Enterprise',
    price: '199',
    icon: Crown,
    description: 'For large teams with custom needs',
    features: [
      'Unlimited videos',
      '8K quality exports',
      'Custom AI models',
      'Dedicated support',
      'Unlimited storage',
      'White-label solution',
      'Advanced API',
      'Team collaboration',
    ],
    gradient: 'from-teal-500 to-emerald-500',
    popular: false,
  },
];

export function Pricing() {
  return (
    <section id="pricing" className="relative py-24 md:py-32 overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-cyan-500/5 to-transparent dark:via-cyan-500/10" />

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16 space-y-4"
        >
          <div className="inline-flex items-center gap-2 px-4 py-2 glass rounded-full">
            <Sparkles className="w-4 h-4 text-emerald-500" />
            <span className="text-sm font-medium">Simple Pricing</span>
          </div>
          <h2 className="text-4xl sm:text-5xl md:text-6xl font-bold">
            Choose Your
            <br />
            <span className="text-gradient">Perfect Plan</span>
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Start free, upgrade when you need. All plans include core features.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {plans.map((plan, index) => (
            <motion.div
              key={plan.name}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              whileHover={{ y: -8, scale: 1.02 }}
              className={`relative ${plan.popular ? 'md:scale-105' : ''}`}
            >
              {plan.popular && (
                <div className="absolute -top-4 left-0 right-0 flex justify-center">
                  <div className="px-4 py-1 glass-strong rounded-full text-sm font-medium border border-emerald-500/50">
                    Most Popular
                  </div>
                </div>
              )}

              <div className={`absolute inset-0 bg-gradient-to-r ${plan.gradient} rounded-2xl blur-xl opacity-20 ${plan.popular ? 'opacity-30' : ''}`} />

              <div className={`relative glass-strong rounded-2xl p-8 h-full space-y-6 ${plan.popular ? 'border-emerald-500/50' : ''}`}>
                <div>
                  <div className={`w-12 h-12 rounded-xl bg-gradient-to-r ${plan.gradient} p-2.5 mb-4 shadow-lg`}>
                    <plan.icon className="w-full h-full text-white" />
                  </div>
                  <h3 className="text-2xl font-bold mb-2">{plan.name}</h3>
                  <p className="text-sm text-muted-foreground mb-4">{plan.description}</p>
                  <div className="flex items-baseline gap-1">
                    <span className="text-4xl font-bold">${plan.price}</span>
                    <span className="text-muted-foreground">/month</span>
                  </div>
                </div>

                <Button
                  className={`w-full rounded-full ${
                    plan.popular
                      ? 'gradient-primary text-white shadow-lg shadow-emerald-500/30'
                      : 'glass-strong'
                  }`}
                  size="lg"
                >
                  {plan.popular ? 'Start Free Trial' : 'Get Started'}
                </Button>

                <div className="space-y-3 pt-4">
                  {plan.features.map((feature) => (
                    <div key={feature} className="flex items-start gap-3">
                      <div className={`mt-0.5 w-5 h-5 rounded-full bg-gradient-to-r ${plan.gradient} flex items-center justify-center flex-shrink-0`}>
                        <Check className="w-3 h-3 text-white" />
                      </div>
                      <span className="text-sm">{feature}</span>
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="mt-16 text-center text-sm text-muted-foreground"
        >
          All plans include a 14-day free trial. No credit card required.
        </motion.div>
      </div>
    </section>
  );
}
