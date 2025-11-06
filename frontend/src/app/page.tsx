'use client';

import { HeroSection } from '@/components/landing/HeroSection';
import { FeaturesSection } from '@/components/landing/FeaturesSection';
import { HowItWorksSection } from '@/components/landing/HowItWorksSection';
import { ShowcaseSection } from '@/components/landing/ShowcaseSection';
import { CTASection } from '@/components/landing/CTASection';
import { Navbar } from '@/components/navbar';
import { Footer } from '@/components/footer';

export default function Home() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <HeroSection />
      <FeaturesSection />
      <HowItWorksSection />
      <ShowcaseSection />
      <CTASection />
      <Footer />
    </div>
  );
}
