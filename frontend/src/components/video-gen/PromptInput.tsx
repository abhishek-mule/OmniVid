'use client';

import { motion } from 'framer-motion';
import { Lightbulb, Sparkles } from 'lucide-react';

interface PromptInputProps {
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
}

const templates = [
  "A cinematic drone shot flying over a futuristic city at sunset",
  "Product showcase with smooth 360° rotation on white background",
  "Motivational quote animation with dynamic typography",
  "Nature timelapse showing clouds moving over mountains",
  "Tech startup explainer with animated infographics",
  "Social media ad with bold text and energetic transitions",
  "Minimalist logo reveal with elegant particle effects",
  "Travel vlog intro with scenic landscape transitions"
];

const aiTips = [
  "Be specific about camera movements (pan, zoom, dolly)",
  "Mention lighting conditions (golden hour, studio lit)",
  "Describe the mood and atmosphere you want",
  "Include specific colors or color schemes",
  "Mention duration and pacing preferences"
];

export default function PromptInput({ value, onChange, disabled }: PromptInputProps) {
  const characterCount = value.length;
  const maxCharacters = 500;
  const progress = (characterCount / maxCharacters) * 100;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.1 }}
      className="rounded-2xl border border-border bg-card p-6"
    >
      <div className="flex items-center gap-2 mb-4">
        <Sparkles className="w-5 h-5 text-primary" />
        <h2 className="text-xl font-semibold">Describe Your Video</h2>
      </div>

      {/* Text Area */}
      <div className="relative mb-4">
        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value.slice(0, maxCharacters))}
          disabled={disabled}
          placeholder="Describe the video you want to create... Be as detailed as possible for best results."
          className="w-full h-32 px-4 py-3 rounded-lg border border-border bg-background resize-none focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        />
        
        {/* Character Counter */}
        <div className="absolute bottom-3 right-3 flex items-center gap-2">
          <span className={`text-sm font-medium ${characterCount > maxCharacters * 0.9 ? 'text-orange-500' : 'text-muted-foreground'}`}>
            {characterCount} / {maxCharacters}
          </span>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mb-6">
        <div className="h-1.5 bg-muted rounded-full overflow-hidden">
          <motion.div
            className={`h-full rounded-full ${
              progress > 90 ? 'bg-orange-500' : progress > 50 ? 'bg-primary' : 'bg-primary/50'
            }`}
            initial={{ width: 0 }}
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.3 }}
          />
        </div>
      </div>

      {/* Quick Templates */}
      <div className="mb-6">
        <h3 className="text-sm font-medium mb-3 flex items-center gap-2">
          <Sparkles className="w-4 h-4" />
          Quick Templates
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
          {templates.map((template, index) => (
            <motion.button
              key={index}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              onClick={() => !disabled && onChange(template)}
              disabled={disabled}
              className="text-left px-3 py-2 rounded-lg border border-border bg-background hover:bg-muted hover:border-primary/50 transition-all text-sm disabled:opacity-50 disabled:cursor-not-allowed group"
            >
              <span className="line-clamp-1 group-hover:text-primary transition-colors">
                {template}
              </span>
            </motion.button>
          ))}
        </div>
      </div>

      {/* AI Tips */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4 }}
        className="rounded-lg bg-primary/5 border border-primary/20 p-4"
      >
        <div className="flex items-start gap-2 mb-2">
          <Lightbulb className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="font-medium text-sm mb-2">AI Tips for Better Results</h3>
            <ul className="space-y-1.5">
              {aiTips.map((tip, index) => (
                <li key={index} className="text-xs text-muted-foreground flex items-start gap-2">
                  <span className="text-primary mt-0.5">•</span>
                  <span>{tip}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
}
