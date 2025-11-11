'use client';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Navbar } from '@/components/navbar';
import { Badge } from '@/components/ui/badge';
import { Check, Star, ArrowRight } from 'lucide-react';
import Link from 'next/link';

export default function PricingPage() {
  const plans = [
    {
      name: 'Starter',
      price: '$9',
      period: 'month',
      description: 'Perfect for individuals and small projects',
      features: [
        '5 video generations per month',
        'HD resolution (1080p)',
        'Basic templates',
        'Email support',
        'Watermark on videos'
      ],
      popular: false,
      buttonText: 'Start Free Trial'
    },
    {
      name: 'Pro',
      price: '$29',
      period: 'month',
      description: 'Ideal for content creators and businesses',
      features: [
        '50 video generations per month',
        '4K resolution support',
        'Premium templates',
        'Priority support',
        'No watermark',
        'Custom branding',
        'Advanced editing tools'
      ],
      popular: true,
      buttonText: 'Start Pro Trial'
    },
    {
      name: 'Enterprise',
      price: '$99',
      period: 'month',
      description: 'For teams and large organizations',
      features: [
        'Unlimited video generations',
        'All resolutions up to 8K',
        'Custom templates',
        'Dedicated support manager',
        'API access',
        'Team collaboration',
        'Advanced analytics',
        'Custom integrations'
      ],
      popular: false,
      buttonText: 'Contact Sales'
    }
  ];

  const faqs = [
    {
      question: 'Can I change my plan anytime?',
      answer: 'Yes, you can upgrade or downgrade your plan at any time. Changes take effect immediately.'
    },
    {
      question: 'What video formats are supported?',
      answer: 'We support MP4, MOV, and WebM formats in various resolutions from 720p to 8K.'
    },
    {
      question: 'Is there a free trial?',
      answer: 'Yes, all plans come with a 7-day free trial. No credit card required to start.'
    },
    {
      question: 'Can I cancel anytime?',
      answer: 'Absolutely. Cancel your subscription at any time with no penalties or hidden fees.'
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
                Simple, Transparent
                <br />
                <span className="bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
                  Pricing
                </span>
              </h1>
              <p className="mt-6 text-xl text-muted-foreground max-w-2xl mx-auto">
                Choose the perfect plan for your video creation needs. Start free and scale as you grow.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Cards */}
      <section className="py-16">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-7xl mx-auto">
            {plans.map((plan, index) => (
              <Card key={index} className={`relative ${plan.popular ? 'border-primary shadow-lg scale-105' : ''}`}>
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <Badge className="bg-primary text-primary-foreground px-4 py-1">
                      <Star className="w-4 h-4 mr-1" />
                      Most Popular
                    </Badge>
                  </div>
                )}

                <CardHeader className="text-center">
                  <CardTitle className="text-2xl">{plan.name}</CardTitle>
                  <div className="mt-4">
                    <span className="text-4xl font-bold">{plan.price}</span>
                    <span className="text-muted-foreground">/{plan.period}</span>
                  </div>
                  <CardDescription className="mt-2">
                    {plan.description}
                  </CardDescription>
                </CardHeader>

                <CardContent>
                  <ul className="space-y-3 mb-6">
                    {plan.features.map((feature, featureIndex) => (
                      <li key={featureIndex} className="flex items-center">
                        <Check className="h-5 w-5 text-primary mr-3 flex-shrink-0" />
                        <span className="text-sm">{feature}</span>
                      </li>
                    ))}
                  </ul>

                  <Link href={plan.name === 'Enterprise' ? '/contact' : '/signup'} className="w-full">
                    <Button
                      className={`w-full ${plan.popular ? '' : 'variant-outline'}`}
                      variant={plan.popular ? 'default' : 'outline'}
                    >
                      {plan.buttonText}
                      <ArrowRight className="ml-2 h-4 w-4" />
                    </Button>
                  </Link>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-16 bg-muted/30">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold tracking-tight">Frequently Asked Questions</h2>
            <p className="mt-4 text-lg text-muted-foreground">
              Everything you need to know about our pricing
            </p>
          </div>

          <div className="max-w-3xl mx-auto space-y-6">
            {faqs.map((faq, index) => (
              <Card key={index}>
                <CardHeader>
                  <CardTitle className="text-lg">{faq.question}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground">{faq.answer}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-2xl mx-auto text-center">
            <h2 className="text-3xl font-bold tracking-tight mb-4">
              Ready to Start Creating Amazing Videos?
            </h2>
            <p className="text-lg text-muted-foreground mb-8">
              Join thousands of creators who trust OmniVid for their video needs
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/create">
                <Button size="lg" className="h-12 px-8">
                  Start Free Trial
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
    </div>
  );
}