import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Sparkles,
  Video,
  Edit,
  Users,
  Zap,
  Shield,
  Cloud,
  Smartphone,
  Globe,
  BarChart3,
  Clock,
  Star
} from "lucide-react";

const features = [
  {
    icon: Sparkles,
    title: "AI-Powered Generation",
    description: "Transform text prompts into stunning videos using advanced machine learning algorithms.",
    badge: "AI-Powered",
    gradient: "from-purple-500 to-pink-500"
  },
  {
    icon: Edit,
    title: "Professional Editor",
    description: "Intuitive drag-and-drop timeline with advanced editing tools and effects.",
    badge: "Professional",
    gradient: "from-blue-500 to-cyan-500"
  },
  {
    icon: Users,
    title: "Real-time Collaboration",
    description: "Work seamlessly with your team using live editing and commenting features.",
    badge: "Team",
    gradient: "from-green-500 to-emerald-500"
  },
  {
    icon: Zap,
    title: "Lightning Fast",
    description: "Generate videos in minutes with our optimized cloud infrastructure.",
    badge: "Fast",
    gradient: "from-yellow-500 to-orange-500"
  },
  {
    icon: Shield,
    title: "Enterprise Security",
    description: "Bank-level encryption and compliance for your sensitive content.",
    badge: "Secure",
    gradient: "from-red-500 to-rose-500"
  },
  {
    icon: Cloud,
    title: "Cloud Storage",
    description: "Unlimited storage with automatic backups and version control.",
    badge: "Cloud",
    gradient: "from-indigo-500 to-purple-500"
  },
  {
    icon: Smartphone,
    title: "Mobile Optimized",
    description: "Create and edit videos on any device with our responsive design.",
    badge: "Mobile",
    gradient: "from-teal-500 to-cyan-500"
  },
  {
    icon: Globe,
    title: "Global CDN",
    description: "Deliver content worldwide with our distributed network infrastructure.",
    badge: "Global",
    gradient: "from-emerald-500 to-teal-500"
  },
  {
    icon: BarChart3,
    title: "Analytics Dashboard",
    description: "Track performance metrics and audience engagement in real-time.",
    badge: "Analytics",
    gradient: "from-violet-500 to-purple-500"
  },
  {
    icon: Clock,
    title: "24/7 Support",
    description: "Round-the-clock customer support with dedicated account managers.",
    badge: "Support",
    gradient: "from-slate-500 to-gray-500"
  }
];

export default function FeaturesPage() {
  return (
    <div className="min-h-screen gradient-bg">
      {/* Hero Section */}
      <section className="relative py-20 overflow-hidden">
        <div className="absolute inset-0 hero-gradient"></div>
        <div className="container relative z-10">
          <div className="text-center max-w-4xl mx-auto animate-fade-in">
            <Badge variant="secondary" className="mb-4 glass px-4 py-2">
              <Star className="w-4 h-4 mr-2" />
              Premium Features
            </Badge>
            <h1 className="text-5xl md:text-7xl font-bold mb-6 text-gradient">
              Powerful Features for
              <br />
              <span className="text-foreground">Video Creation</span>
            </h1>
            <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
              Discover the comprehensive toolkit that makes OmniVid the ultimate choice for AI-powered video generation and editing.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button size="lg" className="glass-hover premium-shadow">
                Start Creating
              </Button>
              <Button size="lg" variant="outline" className="glass-hover">
                Watch Demo
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="py-20">
        <div className="container">
          <div className="text-center mb-16 animate-slide-up">
            <h2 className="text-4xl font-bold mb-4">Everything You Need</h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              From AI generation to professional editing, we provide all the tools you need to create amazing videos.
            </p>
          </div>

          <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {features.map((feature, index) => (
              <Card
                key={feature.title}
                className="glass-card group hover:scale-105 transition-all duration-300 animate-fade-in"
                style={{ animationDelay: `${index * 100}ms` }}
              >
                <CardHeader className="text-center pb-4">
                  <div className={`w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br ${feature.gradient} flex items-center justify-center group-hover:animate-glow`}>
                    <feature.icon className="w-8 h-8 text-white" />
                  </div>
                  <Badge variant="secondary" className="mb-2">
                    {feature.badge}
                  </Badge>
                  <CardTitle className="text-xl">{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-center leading-relaxed">
                    {feature.description}
                  </CardDescription>
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
            <h2 className="text-4xl font-bold mb-4">Ready to Create Amazing Videos?</h2>
            <p className="text-xl text-muted-foreground mb-8">
              Join thousands of creators who trust OmniVid for their video production needs.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button size="lg" className="gradient-primary text-white">
                Get Started Free
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
