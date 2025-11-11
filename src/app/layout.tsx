import type { Metadata, Viewport } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { ThemeProvider } from "@/components/theme-provider";
import { Toaster } from "@/components/ui/toaster-new";
import dynamic from 'next/dynamic';
import { ReCaptchaProvider } from "@/components/common/ReCaptcha";
import { AuthProvider } from "@/context/AuthContext";
import type { ReactNode } from 'react';

const inter = Inter({ subsets: ['latin'] });
const ThreeBackground = dynamic(() => import('@/components/ThreeBackground'), { ssr: false });

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
  children: ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" integrity="sha512-iecdLmaskl7CVkqkXNQ/ZH/XLlvWZOJyj7Yy7tcenmpD1ypASozpmT/E0iPtmFIB46ZmdtAc9eNBvH0H/ZpiBw==" crossOrigin="anonymous" referrerPolicy="no-referrer" />
      </head>
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
              <AuthProvider>
                {children}
                <Toaster />
              </AuthProvider>
            </ThemeProvider>
          </div>
        </ReCaptchaProvider>
      </body>
    </html>
  );
}
