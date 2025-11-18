'use client';

import { Label } from '@/components/ui/label';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu';
import { Slider } from '@/components/ui/slider';
import { ChevronDown } from 'lucide-react';

interface Settings {
  resolution: '720p' | '1080p' | '2k' | '4k';
  fps: 24 | 30 | 60;
  duration: number;
  quality: 'fast' | 'balanced' | 'best';
  engine: 'remotion' | 'ffmpeg' | 'blender' | 'manim';
}

interface SettingsPanelProps {
  settings: Settings;
  onChange: (settings: Settings) => void;
  disabled?: boolean;
}

export default function SettingsPanel({ settings, onChange, disabled }: SettingsPanelProps) {
  const updateSetting = <K extends keyof Settings>(key: K, value: Settings[K]) => {
    onChange({ ...settings, [key]: value });
  };

  return (
    <div className="space-y-4 p-4 border rounded-lg">
      <h3 className="font-medium">Video Settings</h3>

      <div className="space-y-2">
        <Label>Rendering Engine</Label>
        <DropdownMenu>
          <DropdownMenuTrigger asChild disabled={disabled}>
            <button className="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50">
              {settings.engine === 'remotion' && 'Remotion (Text/Animation)'}
              {settings.engine === 'ffmpeg' && 'FFmpeg (Video Processing)'}
              {settings.engine === 'blender' && 'Blender (3D Graphics)'}
              {settings.engine === 'manim' && 'Manim (Mathematical)'}
              <ChevronDown className="h-4 w-4 opacity-50" />
            </button>
          </DropdownMenuTrigger>
          <DropdownMenuContent>
            <DropdownMenuItem onClick={() => updateSetting('engine', 'remotion')}>
              <div className="flex flex-col">
                <span className="font-medium">Remotion</span>
                <span className="text-xs text-muted-foreground">Text animations & motion graphics</span>
              </div>
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => updateSetting('engine', 'ffmpeg')}>
              <div className="flex flex-col">
                <span className="font-medium">FFmpeg</span>
                <span className="text-xs text-muted-foreground">Video processing & composition</span>
              </div>
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => updateSetting('engine', 'blender')}>
              <div className="flex flex-col">
                <span className="font-medium">Blender</span>
                <span className="text-xs text-muted-foreground">3D graphics & animation</span>
              </div>
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => updateSetting('engine', 'manim')}>
              <div className="flex flex-col">
                <span className="font-medium">Manim</span>
                <span className="text-xs text-muted-foreground">Mathematical animations</span>
              </div>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label>Resolution</Label>
          <DropdownMenu>
            <DropdownMenuTrigger asChild disabled={disabled}>
              <button className="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50">
                {settings.resolution}
                <ChevronDown className="h-4 w-4 opacity-50" />
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent>
              <DropdownMenuItem onClick={() => updateSetting('resolution', '720p')}>720p</DropdownMenuItem>
              <DropdownMenuItem onClick={() => updateSetting('resolution', '1080p')}>1080p</DropdownMenuItem>
              <DropdownMenuItem onClick={() => updateSetting('resolution', '2k')}>2K</DropdownMenuItem>
              <DropdownMenuItem onClick={() => updateSetting('resolution', '4k')}>4K</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>

        <div className="space-y-2">
          <Label>FPS</Label>
          <DropdownMenu>
            <DropdownMenuTrigger asChild disabled={disabled}>
              <button className="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50">
                {settings.fps}
                <ChevronDown className="h-4 w-4 opacity-50" />
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent>
              <DropdownMenuItem onClick={() => updateSetting('fps', 24)}>24</DropdownMenuItem>
              <DropdownMenuItem onClick={() => updateSetting('fps', 30)}>30</DropdownMenuItem>
              <DropdownMenuItem onClick={() => updateSetting('fps', 60)}>60</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>

      <div className="space-y-2">
        <Label>Duration: {settings.duration}s</Label>
        <Slider
          value={[settings.duration]}
          onValueChange={([value]) => updateSetting('duration', value)}
          min={5}
          max={60}
          step={5}
          disabled={disabled}
        />
      </div>

      <div className="space-y-2">
        <Label>Quality</Label>
        <DropdownMenu>
          <DropdownMenuTrigger asChild disabled={disabled}>
            <button className="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50">
              {settings.quality}
              <ChevronDown className="h-4 w-4 opacity-50" />
            </button>
          </DropdownMenuTrigger>
          <DropdownMenuContent>
            <DropdownMenuItem onClick={() => updateSetting('quality', 'fast')}>Fast</DropdownMenuItem>
            <DropdownMenuItem onClick={() => updateSetting('quality', 'balanced')}>Balanced</DropdownMenuItem>
            <DropdownMenuItem onClick={() => updateSetting('quality', 'best')}>Best</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </div>
  );
}
