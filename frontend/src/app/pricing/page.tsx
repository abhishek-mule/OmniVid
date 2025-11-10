'use client';

import { Button } from '@/components/ui/button';
import { Check } from 'lucide-react';
import Link from 'next/link';
import { Navbar } from '@/components/navbar';
import { Footer } from '@/components/footer';
import { useGetStarted } from '@/hooks/useGetStarted';

export default function Pricing() {
  const { start } = useGetStarted();
  const plans = [
    {
      name: 'Free',
      price: '0',
      description: 'Perfect for trying out OmniVid',
      features: [
        '5 videos per month',
        'Up to 720p resolution',
        'Basic templates',
        'Community support',
        '1GB storage'
      ],
      cta: 'Get Started',
      href: '/app/editor',
      popular: false
    },
    {
      name: 'Pro',
      price: '29',
      description: 'For professional creators',
      features: [
        '50 videos per month',
        'Up to 4K resolution',
        'Premium templates',
        'Priority support',
        '50GB storage',
        'Custom branding',
        'Advanced analytics'
      ],
      cta: 'Start Free Trial',
      href: '/app/editor',
      popular: true
    },
    {
      name: 'Enterprise',
      price: '99',
      description: 'For teams and businesses',
      features: [
        'Unlimited videos',
        'Up to 8K resolution',
        'Custom templates',
        'Dedicated support',
        'Unlimited storage',
        'White-label solution',
        'Advanced analytics',
        'API access',
        'Team collaboration'
      ],
      cta: 'Contact Sales',
      href: '/contact',
      popular: false
    }
  ];

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      <main className="container mx-auto px-4 sm:px-6 lg:px-8 pt-32 pb-16">
        <div className="text-center mb-16">
          <h1 className="text-4xl font-bold tracking-tight sm:text-5xl md:text-6xl">
            Simple, transparent pricing
          </h1>
          <p className="mt-6 text-lg text-muted-foreground max-w-2xl mx-auto">
            Choose the perfect plan for your needs. Upgrade, downgrade, or cancel anytime.
          </p>
        </div>

        <div className="grid grid-cols-1 gap-8 lg:grid-cols-3 max-w-7xl mx-auto">
          {plans.map((plan) => (
            <div
              key={plan.name}
              className={`relative rounded-2xl border ${
                plan.popular
                  ? 'border-primary shadow-xl scale-105'
                  : 'border-border'
              } bg-card p-8`}
            >
              {plan.popular && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                  <span className="inline-flex items-center rounded-full bg-primary px-4 py-1 text-sm font-medium text-primary-foreground">
                    Most Popular
                  </span>
                </div>
              )}

              <div className="mb-8">
                <h3 className="text-2xl font-bold">{plan.name}</h3>
                <p className="mt-2 text-sm text-muted-foreground">{plan.description}</p>
                <div className="mt-6">
                  <span className="text-5xl font-bold">${plan.price}</span>
                  <span className="text-muted-foreground">/month</span>
                </div>
              </div>

              <ul className="space-y-4 mb-8">
                {plan.features.map((feature) => (
                  <li key={feature} className="flex items-start gap-3">
                    <Check className="h-5 w-5 text-primary flex-shrink-0 mt-0.5" />
                    <span className="text-sm">{feature}</span>
                  </li>
                ))}
              </ul>

              {plan.href === '/contact' ? (
                <Button
                  className="w-full"
                  variant={plan.popular ? 'default' : 'outline'}
                  asChild
                >
                  <Link href={plan.href}>{plan.cta}</Link>
                </Button>
              ) : (
                <Button
                  className="w-full"
                  variant={plan.popular ? 'default' : 'outline'}
                  onClick={() => start('/app/editor')}
                >
                  {plan.cta}
                </Button>
              )}
            </div>
          ))}
        </div>

        <div className="mt-16 text-center">
          <p className="text-muted-foreground">
            All plans include a 14-day free trial. No credit card required.
          </p>
        </div>
      </main>

      <Footer />
    </div>
  );
}
