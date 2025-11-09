import { Github, Video } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="relative py-12 px-4 border-t border-slate-800">
      <div className="max-w-7xl mx-auto">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-3">
            <Video className="w-8 h-8 text-cyan-400" strokeWidth={1.5} />
            <div>
              <h3 className="text-xl font-bold text-white">OmniVid</h3>
              <p className="text-sm text-slate-500">AbhiAntrik AI</p>
            </div>
          </div>

          <div className="flex items-center gap-8">
            <a
              href="https://github.com/abhishek-mule/OmniVid"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 text-slate-400 hover:text-cyan-400 transition-colors"
            >
              <Github className="w-5 h-5" />
              <span className="text-sm">View on GitHub</span>
            </a>
          </div>
        </div>

        <div className="mt-8 pt-8 border-t border-slate-800">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-slate-500">
            <p>Imagine. Compile. Create.</p>
            <p>&copy; {new Date().getFullYear()} OmniVid. AI-Powered Video Generation.</p>
          </div>
        </div>
      </div>
    </footer>
  );
}
