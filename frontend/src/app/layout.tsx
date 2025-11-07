import type { Metadata, Viewport } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { ThemeProvider } from "@/components/theme-provider";
import { Toaster } from "@/components/ui/toaster-new";
import { ReCaptchaProvider } from "@/components/common/ReCaptcha";
import dynamic from 'next/dynamic';

const CatAnimation = dynamic(() => import('@/components/CatAnimation'), {
  ssr: false,
});

const ThreeBackground = dynamic(() => import('@/components/ThreeBackground'), {
  ssr: false,
});

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  metadataBase: new URL('https://omnivid.ai'),
  title: 'OmniVid AI - AI-Powered Video Generation',
  description: 'Transform your ideas into stunning videos with AI',
  keywords: ['AI Video', 'Video Generation', 'AI Video Editor', 'OmniVid'],
  authors: [{ name: 'OmniVid Team' }],
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://omnivid.ai',
    title: 'OmniVid AI - AI-Powered Video Generation',
    description: 'Transform your ideas into stunning videos with AI',
    siteName: 'OmniVid AI',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'OmniVid AI - AI-Powered Video Generation',
    description: 'Transform your ideas into stunning videos with AI',
    creator: '@omnivid',
  },
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: 'white' },
    { media: '(prefers-color-scheme: dark)', color: 'black' },
  ],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <ReCaptchaProvider>
          <ThreeBackground />
          <div className="relative z-10">
            <ThemeProvider
              attribute="class"
              defaultTheme="system"
              enableSystem
              disableTransitionOnChange
            >
              {children}
              <Toaster />
            </ThemeProvider>
          </div>
        </ReCaptchaProvider>
      </body>
    </html>
  );
}
