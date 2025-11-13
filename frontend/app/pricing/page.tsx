import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Check, Star, Zap, Crown, Sparkles } from "lucide-react";

const plans = [
  {
    name: 'Starter',
    price: 29,
    period: 'month',
    icon: Sparkles,
    gradient: 'from-blue-500 to-cyan-500',
    features: [
      '10 video generations/month',
      '720p resolution',
      'Basic editing tools',
      '5GB cloud storage',
      'Email support',
      'Standard templates'
    ]
  },
  {
    name: 'Professional',
    price: 99,
    period: 'month',
    featured: true,
    icon: Zap,
    gradient: 'from-emerald-500 to-teal-500',
    badge: 'Most Popular',
    features: [
      '50 video generations/month',
      '1080p resolution',
      'Advanced editing tools',
      '50GB cloud storage',
      'Priority support',
      'API access',
      'Watermark-free exports',
      'Premium templates',
      'Team collaboration'
    ]
  },
  {
    name: 'Enterprise',
    price: 'Custom',
    period: 'month',
    icon: Crown,
    gradient: 'from-purple-500 to-pink-500',
    features: [
      'Unlimited generations',
      '4K resolution',
      'All Professional features',
      'Custom storage',
      'Dedicated support',
      'SSO & SAML',
      'Custom integrations',
      'On-premise options',
      'White-label solution'
    ]
  }
];

export default function PricingPage() {
  return (
    <div className="min-h-screen gradient-bg">
      {/* Hero Section */}
      <section className="relative py-20 overflow-hidden">
        <div className="absolute inset-0 hero-gradient"></div>
        <div className="container relative z-10">
          <div className="text-center max-w-4xl mx-auto animate-fade-in">
            <Badge variant="secondary" className="mb-4 glass px-4 py-2">
              <Star className="w-4 h-4 mr-2" />
              Transparent Pricing
            </Badge>
            <h1 className="text-5xl md:text-7xl font-bold mb-6 text-gradient">
              Choose Your Plan
            </h1>
            <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
              Start free and scale as you grow. No hidden fees, cancel anytime.
            </p>
          </div>
        </div>
      </section>

      {/* Pricing Cards */}
      <section className="py-20">
        <div className="container">
          <div className="grid gap-8 md:grid-cols-3 max-w-7xl mx-auto">
            {plans.map((plan, index) => (
              <Card
                key={plan.name}
                className={`relative glass-card group hover:scale-105 transition-all duration-300 animate-fade-in ${
                  plan.featured ? 'premium-shadow animate-glow' : ''
                }`}
                style={{ animationDelay: `${index * 200}ms` }}
              >
                {plan.featured && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <Badge className="glass-strong px-4 py-2 text-sm font-semibold">
                      {plan.badge}
                    </Badge>
                  </div>
                )}

                <CardHeader className="text-center pb-4">
                  <div className={`w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br ${plan.gradient} flex items-center justify-center group-hover:animate-glow`}>
                    <plan.icon className="w-8 h-8 text-white" />
                  </div>
                  <CardTitle className="text-2xl font-bold">{plan.name}</CardTitle>
                  <div className="mt-4">
                    <span className="text-5xl font-bold text-gradient">
                      {typeof plan.price === 'number' ? `$${plan.price}` : plan.price}
                    </span>
                    {typeof plan.price === 'number' && (
                      <span className="text-muted-foreground text-lg">/{plan.period}</span>
                    )}
                  </div>
                </CardHeader>

                <CardContent className="space-y-6">
                  <ul className="space-y-3">
                    {plan.features.map((feature, i) => (
                      <li key={i} className="flex items-start">
                        <Check className="w-5 h-5 text-emerald-500 mr-3 mt-0.5 flex-shrink-0" />
                        <span className="text-sm leading-relaxed">{feature}</span>
                      </li>
                    ))}
                  </ul>

                  <Button
                    className={`w-full ${
                      plan.featured
                        ? 'gradient-primary text-white hover:opacity-90'
                        : 'glass-hover'
                    }`}
                    size="lg"
                  >
                    {plan.name === 'Enterprise' ? 'Contact Sales' : 'Get Started'}
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-20">
        <div className="container">
          <div className="text-center mb-16 animate-slide-up">
            <h2 className="text-4xl font-bold mb-4">Frequently Asked Questions</h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Everything you need to know about our pricing and features.
            </p>
          </div>

          <div className="max-w-4xl mx-auto space-y-6">
            {[
              {
                question: "Can I change plans anytime?",
                answer: "Yes, you can upgrade or downgrade your plan at any time. Changes take effect immediately."
              },
              {
                question: "What happens to my videos if I cancel?",
                answer: "Your videos remain accessible for 30 days after cancellation. Download them before then."
              },
              {
                question: "Do you offer refunds?",
                answer: "We offer a 30-day money-back guarantee for all paid plans."
              },
              {
                question: "Is there a free trial?",
                answer: "Yes, start with our free plan or contact us for an extended trial."
              }
            ].map((faq, index) => (
              <Card key={index} className="glass-card animate-fade-in" style={{ animationDelay: `${index * 100}ms` }}>
                <CardContent className="p-6">
                  <h3 className="font-semibold text-lg mb-2">{faq.question}</h3>
                  <p className="text-muted-foreground">{faq.answer}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20">
        <div className="container">
          <div className="glass-card max-w-4xl mx-auto text-center p-12 animate-slide-up">
            <h2 className="text-4xl font-bold mb-4">Ready to Get Started?</h2>
            <p className="text-xl text-muted-foreground mb-8">
              Join thousands of creators who trust OmniVid for their video production needs.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button size="lg" className="gradient-primary text-white">
                Start Free Trial
              </Button>
              <Button size="lg" variant="outline" className="glass-hover">
                Schedule Demo
              </Button>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
