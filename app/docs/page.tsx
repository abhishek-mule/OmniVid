'use client';

import { BookOpen, Code, Video, Zap, MessageSquare, FileText, ChevronRight } from 'lucide-react';
import Link from 'next/link';

type DocSection = {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  color: string;
};

const docsSections: DocSection[] = [
  {
    id: 'getting-started',
    title: 'Getting Started',
    description: 'Learn how to quickly set up and start using OmniVid',
    icon: <Zap className="w-6 h-6" />,
    color: 'from-yellow-500 to-orange-500',
  },
  {
    id: 'api-reference',
    title: 'API Reference',
    description: 'Complete documentation of the OmniVid API',
    icon: <Code className="w-6 h-6" />,
    color: 'from-blue-500 to-indigo-500',
  },
  {
    id: 'video-guides',
    title: 'Video Tutorials',
    description: 'Step-by-step video tutorials for all features',
    icon: <Video className="w-6 h-6" />,
    color: 'from-red-500 to-pink-500',
  },
  {
    id: 'troubleshooting',
    title: 'Troubleshooting',
    description: 'Solutions to common issues and errors',
    icon: <MessageSquare className="w-6 h-6" />,
    color: 'from-green-500 to-teal-500',
  },
  {
    id: 'examples',
    title: 'Examples',
    description: 'Sample projects and code snippets',
    icon: <FileText className="w-6 h-6" />,
    color: 'from-purple-500 to-fuchsia-500',
  },
];

export default function DocsPage() {

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        <header className="mb-12 text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-r from-cyan-500 to-blue-600 mb-4">
            <BookOpen className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-4xl font-bold text-white mb-3">OmniVid Documentation</h1>
          <p className="text-lg text-slate-400 max-w-3xl mx-auto">
            Everything you need to know about using OmniVid to create amazing videos
          </p>
        </header>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {docsSections.map((section) => (
              <Link
                key={section.id}
                href={`/docs/${section.id}`}
                className={`group relative overflow-hidden rounded-2xl bg-slate-800/50 border border-slate-700/50 p-6 hover:border-cyan-500/30 transition-all duration-300`}
              >
                <div className="absolute inset-0 bg-gradient-to-br opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                  <div className={`absolute inset-0 bg-gradient-to-br ${section.color} opacity-0 group-hover:opacity-10 transition-opacity duration-300`}></div>
                </div>
                <div className="relative z-10">
                  <div className={`w-12 h-12 rounded-xl mb-4 flex items-center justify-center bg-gradient-to-br ${section.color} text-white`}>
                    {section.icon}
                  </div>
                  <h3 className="text-xl font-semibold text-white mb-2">{section.title}</h3>
                  <p className="text-slate-400 mb-4">{section.description}</p>
                  <div className="flex items-center text-cyan-400 group-hover:text-cyan-300 transition-colors">
                    <span className="text-sm font-medium">Learn more</span>
                    <ChevronRight className="w-4 h-4 ml-1 transition-transform group-hover:translate-x-1" />
                  </div>
                </div>
              </Link>
            ))}
          </div>

          <div className="mt-16 bg-slate-800/50 border border-slate-700/50 rounded-2xl p-8">
            <div className="max-w-3xl mx-auto text-center">
              <h2 className="text-2xl font-bold text-white mb-4">Can't find what you're looking for?</h2>
              <p className="text-slate-400 mb-6">
                Our documentation is constantly being updated. If you can't find what you need, please reach out to our support team.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <a
                  href="mailto:support@omnivid.com"
                  className="px-6 py-3 bg-gradient-to-r from-cyan-500 to-blue-600 text-white rounded-lg font-medium hover:shadow-lg hover:shadow-cyan-500/20 transition-all"
                >
                  Contact Support
                </a>
                <a
                  href="https://github.com/your-org/omnivid/issues"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-6 py-3 border border-slate-700 text-slate-300 rounded-lg font-medium hover:bg-slate-700/50 transition-colors"
                >
                  Open an Issue
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
  );
}
