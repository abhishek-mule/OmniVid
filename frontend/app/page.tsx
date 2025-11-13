import Navbar from '@/components/navbar';
import { Hero } from '@/components/hero';
import { Features } from '@/components/features';
import { Gallery } from '@/components/gallery';
import { Pricing } from '@/components/pricing';
import { CTA } from '@/components/cta';
import { Footer } from '@/components/footer';

export default function Home() {
  return (
    <main className="min-h-screen">
      <Navbar />
      <Hero />
      <Features />
      <Gallery />
      <Pricing />
      <CTA />
      <Footer />
    </main>
  );
}
