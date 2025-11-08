"use client";
import React from "react";
import dynamic from "next/dynamic";
import { ThemeProvider } from "@/components/theme-provider";
import { Toaster } from "@/components/ui/toaster-new";
import { ReCaptchaProvider } from "@/components/common/ReCaptcha";
import { AuthProvider } from "@/context/AuthContext";

const ThreeBackground = dynamic(() => import("@/components/ThreeBackground"), {
  ssr: false,
});

export default function LayoutClient({ children }: { children: React.ReactNode }) {
  return (
    <ReCaptchaProvider>
      <ThreeBackground />
      <div className="relative z-10">
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem disableTransitionOnChange>
          <AuthProvider>
            {children}
            <Toaster />
          </AuthProvider>
        </ThemeProvider>
      </div>
    </ReCaptchaProvider>
  );
}