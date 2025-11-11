import { LogOut, User as UserIcon, Video } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

export default function Header() {
  const { profile, signOut } = useAuth();

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-slate-900/80 backdrop-blur-xl border-b border-slate-800">
      <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Video className="w-8 h-8 text-cyan-400" strokeWidth={1.5} />
          <div>
            <h1 className="text-xl font-bold text-white">OmniVid</h1>
            <p className="text-xs text-slate-400">AI Video Editor</p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-3 px-4 py-2 bg-slate-800/50 border border-slate-700 rounded-full">
            <UserIcon className="w-4 h-4 text-slate-400" />
            <div>
              <p className="text-sm text-white font-medium">
                {profile?.full_name || 'User'}
              </p>
              <p className="text-xs text-slate-400">{profile?.email}</p>
            </div>
          </div>

          <button
            onClick={signOut}
            className="p-2 bg-slate-800/50 border border-slate-700 rounded-full text-slate-400 hover:text-white hover:border-red-500/50 hover:bg-slate-800 transition-all"
            title="Sign out"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </header>
  );
}
