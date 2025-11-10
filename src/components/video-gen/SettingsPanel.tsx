'use client';

import { motion } from 'framer-motion';
import { Settings, Lock, Crown } from 'lucide-react';

interface SettingsPanelProps {
  settings: {
    resolution: string;
    fps: number;
    duration: number;
    quality: string;
  };
  onChange: (settings: any) => void;
  disabled?: boolean;
}

const resolutionOptions = [
  { value: '720p', label: '720p HD', free: true },
  { value: '1080p', label: '1080p Full HD', free: true },
  { value: '2k', label: '2K', free: false },
  { value: '4k', label: '4K Ultra HD', free: false }
];

const fpsOptions = [24, 30, 60];

const qualityPresets = [
  { value: 'fast', label: 'Fast', description: 'Quick render, good quality' },
  { value: 'balanced', label: 'Balanced', description: 'Optimal speed & quality' },
  { value: 'best', label: 'Best', description: 'Highest quality, slower' }
];

export default function SettingsPanel({ settings, onChange, disabled }: SettingsPanelProps) {
  const updateSetting = (key: string, value: any) => {
    onChange({ ...settings, [key]: value });
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
      className="rounded-2xl border border-border bg-card p-6"
    >
      <div className="flex items-center gap-2 mb-6">
        <Settings className="w-5 h-5 text-primary" />
        <h2 className="text-xl font-semibold">Video Settings</h2>
      </div>

      <div className="space-y-6">
        {/* Resolution Selector */}
        <div>
          <label className="block text-sm font-medium mb-3">
            Resolution
          </label>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            {resolutionOptions.map((option) => (
              <motion.button
                key={option.value}
                whileHover={{ scale: disabled ? 1 : 1.02 }}
                whileTap={{ scale: disabled ? 1 : 0.98 }}
                onClick={() => !disabled && option.free && updateSetting('resolution', option.value)}
                disabled={disabled || !option.free}
                className={`relative px-4 py-3 rounded-lg border transition-all ${
                  settings.resolution === option.value
                    ? 'border-primary bg-primary/10 text-primary'
                    : 'border-border bg-background hover:border-primary/50'
                } ${!option.free ? 'opacity-60' : ''} disabled:cursor-not-allowed`}
              >
                <div className="flex flex-col items-center gap-1">
                  <span className="font-medium text-sm">{option.label}</span>
                  {!option.free && (
                    <div className="flex items-center gap-1 text-xs text-orange-500">
                      <Crown className="w-3 h-3" />
                      <span>Pro</span>
                    </div>
                  )}
                </div>
                {!option.free && (
                  <Lock className="absolute top-2 right-2 w-3 h-3 text-muted-foreground" />
                )}
              </motion.button>
            ))}
          </div>
        </div>

        {/* FPS Selector */}
        <div>
          <label className="block text-sm font-medium mb-3">
            Frame Rate (FPS)
          </label>
          <div className="grid grid-cols-3 gap-2">
            {fpsOptions.map((fps) => (
              <motion.button
                key={fps}
                whileHover={{ scale: disabled ? 1 : 1.02 }}
                whileTap={{ scale: disabled ? 1 : 0.98 }}
                onClick={() => !disabled && updateSetting('fps', fps)}
                disabled={disabled}
                className={`px-4 py-3 rounded-lg border transition-all ${
                  settings.fps === fps
                    ? 'border-primary bg-primary/10 text-primary'
                    : 'border-border bg-background hover:border-primary/50'
                } disabled:cursor-not-allowed disabled:opacity-50`}
              >
                <span className="font-medium">{fps} fps</span>
              </motion.button>
            ))}
          </div>
        </div>

        {/* Duration Slider */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <label className="text-sm font-medium">
              Duration
            </label>
            <span className="text-sm font-bold text-primary">
              {settings.duration}s
            </span>
          </div>
          <div className="relative">
            <input
              type="range"
              min="5"
              max="60"
              step="5"
              value={settings.duration}
              onChange={(e) => updateSetting('duration', parseInt(e.target.value))}
              disabled={disabled}
              className="w-full h-2 bg-muted rounded-lg appearance-none cursor-pointer disabled:cursor-not-allowed disabled:opacity-50
                [&::-webkit-slider-thumb]:appearance-none
                [&::-webkit-slider-thumb]:w-5
                [&::-webkit-slider-thumb]:h-5
                [&::-webkit-slider-thumb]:rounded-full
                [&::-webkit-slider-thumb]:bg-primary
                [&::-webkit-slider-thumb]:cursor-pointer
                [&::-webkit-slider-thumb]:transition-all
                [&::-webkit-slider-thumb]:hover:scale-110
                [&::-webkit-slider-thumb]:shadow-lg
                [&::-moz-range-thumb]:w-5
                [&::-moz-range-thumb]:h-5
                [&::-moz-range-thumb]:rounded-full
                [&::-moz-range-thumb]:bg-primary
                [&::-moz-range-thumb]:border-0
                [&::-moz-range-thumb]:cursor-pointer"
            />
            <div className="flex justify-between mt-2 text-xs text-muted-foreground">
              <span>5s</span>
              <span>30s</span>
              <span>60s</span>
            </div>
          </div>
        </div>

        {/* Quality Preset */}
        <div>
          <label className="block text-sm font-medium mb-3">
            Quality Preset
          </label>
          <div className="space-y-2">
            {qualityPresets.map((preset) => (
              <motion.button
                key={preset.value}
                whileHover={{ scale: disabled ? 1 : 1.01 }}
                whileTap={{ scale: disabled ? 1 : 0.99 }}
                onClick={() => !disabled && updateSetting('quality', preset.value)}
                disabled={disabled}
                className={`w-full px-4 py-3 rounded-lg border transition-all text-left ${
                  settings.quality === preset.value
                    ? 'border-primary bg-primary/10'
                    : 'border-border bg-background hover:border-primary/50'
                } disabled:cursor-not-allowed disabled:opacity-50`}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className={`font-medium ${settings.quality === preset.value ? 'text-primary' : ''}`}>
                      {preset.label}
                    </div>
                    <div className="text-xs text-muted-foreground mt-0.5">
                      {preset.description}
                    </div>
                  </div>
                  {settings.quality === preset.value && (
                    <motion.div
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      className="w-5 h-5 rounded-full bg-primary flex items-center justify-center"
                    >
                      <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                      </svg>
                    </motion.div>
                  )}
                </div>
              </motion.button>
            ))}
          </div>
        </div>

        {/* Estimated Render Time */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="rounded-lg bg-muted/50 border border-border p-4"
        >
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Estimated render time:</span>
            <span className="font-bold text-primary">
              {Math.ceil((settings.duration / 10) * (settings.quality === 'best' ? 2 : settings.quality === 'fast' ? 0.5 : 1))} min
            </span>
          </div>
        </motion.div>
      </div>
    </motion.div>
  );
}
