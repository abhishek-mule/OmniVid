'use client';

import { Video, Twitter, Github, Linkedin, Mail } from 'lucide-react';

const footerLinks = {
  Product: ['Features', 'Pricing', 'Gallery', 'API'],
  Company: ['About', 'Blog', 'Careers', 'Press'],
  Resources: ['Documentation', 'Tutorials', 'Support', 'Community'],
  Legal: ['Privacy', 'Terms', 'Security', 'Cookies'],
};

export function Footer() {
  return (
    <footer className="relative border-t border-border/50 bg-gradient-to-b from-transparent to-emerald-500/5 dark:to-emerald-500/10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 md:py-16">
        <div className="grid grid-cols-2 md:grid-cols-5 gap-8 mb-12">
          <div className="col-span-2 md:col-span-1">
            <div className="flex items-center gap-2 mb-4 group">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-emerald-500 to-cyan-500 rounded-lg blur-md opacity-70 group-hover:opacity-100 transition-opacity" />
                <div className="relative bg-gradient-to-r from-emerald-600 to-cyan-600 p-2 rounded-lg">
                  <Video className="w-5 h-5 text-white" />
                </div>
              </div>
              <span className="text-xl font-bold text-gradient">OmniVid</span>
            </div>
            <p className="text-sm text-muted-foreground mb-4">
              AI-powered video generation for creators and businesses.
            </p>
            <div className="flex items-center gap-3">
              <a
                href="#"
                className="w-9 h-9 rounded-full glass flex items-center justify-center hover:border-emerald-500/50 transition-colors"
              >
                <Twitter className="w-4 h-4" />
              </a>
              <a
                href="#"
                className="w-9 h-9 rounded-full glass flex items-center justify-center hover:border-emerald-500/50 transition-colors"
              >
                <Github className="w-4 h-4" />
              </a>
              <a
                href="#"
                className="w-9 h-9 rounded-full glass flex items-center justify-center hover:border-emerald-500/50 transition-colors"
              >
                <Linkedin className="w-4 h-4" />
              </a>
              <a
                href="#"
                className="w-9 h-9 rounded-full glass flex items-center justify-center hover:border-emerald-500/50 transition-colors"
              >
                <Mail className="w-4 h-4" />
              </a>
            </div>
          </div>

          {Object.entries(footerLinks).map(([category, links]) => (
            <div key={category}>
              <h3 className="font-semibold mb-3">{category}</h3>
              <ul className="space-y-2">
                {links.map((link) => (
                  <li key={link}>
                    <a
                      href="#"
                      className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                    >
                      {link}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="pt-8 border-t border-border/50 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-sm text-muted-foreground">
            © 2025 OmniVid. All rights reserved.
          </p>
          <p className="text-sm text-muted-foreground">
            Built with AI technology
          </p>
        </div>
      </div>
    </footer>
  );
}
