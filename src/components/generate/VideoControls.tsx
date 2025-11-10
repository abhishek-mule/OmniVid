'use client';

import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import { motion } from 'framer-motion';

interface VideoSettings {
  resolution: '720p' | '1080p' | '2k' | '4k';
  fps: 24 | 30 | 60;
  duration: number;
  quality: 'fast' | 'balanced' | 'best';
}

interface VideoControlsProps {
  settings: VideoSettings;
  onChange: (settings: VideoSettings) => void;
}

export function VideoControls({ settings, onChange }: VideoControlsProps) {
  const resolutions = ['720p', '1080p', '2k', '4k'] as const;
  const fpsOptions = [24, 30, 60] as const;
  const qualityOptions = [
    { value: 'fast', label: 'Fast', desc: 'Quick generation' },
    { value: 'balanced', label: 'Balanced', desc: 'Good quality & speed' },
    { value: 'best', label: 'Best', desc: 'Highest quality' },
  ] as const;

  return (
    <div className="space-y-8">
      {/* Resolution */}
      <div className="space-y-3">
        <Label className="text-base font-semibold">Resolution</Label>
        <div className="grid grid-cols-4 gap-2">
          {resolutions.map((res) => (
            <motion.button
              key={res}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => onChange({ ...settings, resolution: res })}
              className={`px-4 py-3 rounded-lg border-2 transition-all ${
                settings.resolution === res
                  ? 'border-primary bg-primary/10 text-primary font-semibold'
                  : 'border-border hover:border-primary/50'
              }`}
            >
              {res}
            </motion.button>
          ))}
        </div>
      </div>

      {/* FPS */}
      <div className="space-y-3">
        <Label className="text-base font-semibold">Frame Rate (FPS)</Label>
        <div className="grid grid-cols-3 gap-2">
          {fpsOptions.map((fps) => (
            <motion.button
              key={fps}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => onChange({ ...settings, fps })}
              className={`px-4 py-3 rounded-lg border-2 transition-all ${
                settings.fps === fps
                  ? 'border-primary bg-primary/10 text-primary font-semibold'
                  : 'border-border hover:border-primary/50'
              }`}
            >
              {fps} fps
            </motion.button>
          ))}
        </div>
      </div>

      {/* Duration */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <Label className="text-base font-semibold">Duration</Label>
          <span className="text-sm font-medium text-primary">{settings.duration}s</span>
        </div>
        <Slider
          value={[settings.duration]}
          onValueChange={([duration]) => onChange({ ...settings, duration })}
          min={5}
          max={60}
          step={5}
          className="w-full"
        />
        <div className="flex justify-between text-xs text-muted-foreground">
          <span>5s</span>
          <span>60s</span>
        </div>
      </div>

      {/* Quality */}
      <div className="space-y-3">
        <Label className="text-base font-semibold">Quality</Label>
        <div className="grid grid-cols-3 gap-2">
          {qualityOptions.map((option) => (
            <motion.button
              key={option.value}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => onChange({ ...settings, quality: option.value })}
              className={`px-4 py-4 rounded-lg border-2 transition-all text-left ${
                settings.quality === option.value
                  ? 'border-primary bg-primary/10'
                  : 'border-border hover:border-primary/50'
              }`}
            >
              <div className={`font-semibold ${settings.quality === option.value ? 'text-primary' : ''}`}>
                {option.label}
              </div>
              <div className="text-xs text-muted-foreground mt-1">
                {option.desc}
              </div>
            </motion.button>
          ))}
        </div>
      </div>

      {/* Estimated time */}
      <div className="p-4 rounded-lg bg-muted/50 border border-border">
        <div className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground">Estimated generation time:</span>
          <span className="font-semibold">
            {settings.quality === 'fast' ? '2-3' : settings.quality === 'balanced' ? '4-6' : '8-10'} minutes
          </span>
        </div>
      </div>
    </div>
  );
}
