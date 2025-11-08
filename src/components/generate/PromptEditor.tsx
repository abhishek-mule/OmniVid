'use client';

import { motion } from 'framer-motion';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { Lightbulb } from 'lucide-react';

interface PromptEditorProps {
  value: string;
  onChange: (value: string) => void;
}

const suggestions = [
  "A cinematic product showcase with smooth camera movements",
  "An energetic social media ad with quick cuts and vibrant colors",
  "A professional tutorial video with clear step-by-step instructions",
  "A dreamy travel montage with sunset and ocean views",
];

export function PromptEditor({ value, onChange }: PromptEditorProps) {
  return (
    <div className="space-y-4">
      <Textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Describe the video you want to create... Be as detailed as you like!"
        className="min-h-[150px] text-base resize-none border-2 focus:border-primary/50 transition-colors"
      />
      
      <div className="flex items-start gap-2">
        <Lightbulb className="w-4 h-4 text-amber-500 mt-1 flex-shrink-0" />
        <div className="flex-1">
          <p className="text-sm font-medium mb-2">Need inspiration?</p>
          <div className="flex flex-wrap gap-2">
            {suggestions.map((suggestion, index) => (
              <motion.button
                key={index}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => onChange(suggestion)}
                className="text-xs px-3 py-1.5 rounded-full bg-muted hover:bg-muted/80 text-muted-foreground hover:text-foreground transition-colors"
              >
                {suggestion}
              </motion.button>
            ))}
          </div>
        </div>
      </div>

      <div className="flex items-center justify-between text-sm text-muted-foreground">
        <span>{value.length} characters</span>
        <span>💡 Tip: Be specific for better results</span>
      </div>
    </div>
  );
}
