'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Sparkles,
  Menu,
  X,
  Video,
  Edit,
  BarChart3,
  Settings,
  User,
  LogOut
} from "lucide-react";

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: BarChart3 },
  { name: 'Create', href: '/create', icon: Video },
  { name: 'Generate', href: '/generate', icon: Sparkles },
  { name: 'Editor', href: '/editor', icon: Edit },
  { name: 'Features', href: '/features', icon: Sparkles },
  { name: 'Pricing', href: '/pricing', icon: BarChart3 },
  { name: 'Docs', href: '/docs', icon: Settings },
];

function Navbar() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const pathname = usePathname();

  return (
    <nav className="glass border-b border-white/10 sticky top-0 z-50 premium-shadow">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center space-x-2 group">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center group-hover:animate-glow">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <span className="font-bold text-xl text-gradient">OmniVid</span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-1">
            {navigation.map((item) => (
              <Link
                key={item.name}
                href={item.href}
                className={`px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                  pathname === item.href
                    ? 'glass-strong text-foreground'
                    : 'text-muted-foreground hover:text-foreground hover:glass-hover'
                }`}
              >
                {item.name}
              </Link>
            ))}
          </div>

          {/* User Actions */}
          <div className="hidden md:flex items-center space-x-3">
            <Badge variant="secondary" className="glass px-3 py-1">
              Free Trial
            </Badge>
            <Button variant="outline" size="sm" className="glass-hover">
              <User className="w-4 h-4 mr-2" />
              Profile
            </Button>
            <Button size="sm" className="gradient-primary text-white">
              Upgrade
            </Button>
          </div>

          {/* Mobile menu button */}
          <button
            className="md:hidden p-2 rounded-lg glass-hover"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <div className="md:hidden py-4 border-t border-white/10 animate-slide-up">
            <div className="space-y-2">
              {navigation.map((item) => (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`block px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                    pathname === item.href
                      ? 'glass-strong text-foreground'
                      : 'text-muted-foreground hover:text-foreground hover:glass-hover'
                  }`}
                  onClick={() => setMobileMenuOpen(false)}
                >
                  <div className="flex items-center space-x-2">
                    <item.icon className="w-4 h-4" />
                    <span>{item.name}</span>
                  </div>
                </Link>
              ))}
              <div className="pt-4 border-t border-white/10 space-y-2">
                <Button variant="outline" className="w-full justify-start glass-hover">
                  <User className="w-4 h-4 mr-2" />
                  Profile
                </Button>
                <Button variant="outline" className="w-full justify-start glass-hover">
                  <LogOut className="w-4 h-4 mr-2" />
                  Sign Out
                </Button>
                <Button className="w-full gradient-primary text-white">
                  Upgrade to Pro
                </Button>
              </div>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}

export default Navbar;
