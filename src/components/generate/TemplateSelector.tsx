'use client';

import { motion } from 'framer-motion';
import { CheckCircle2 } from 'lucide-react';

interface TemplateSelectorProps {
  selected: string | null;
  onSelect: (id: string) => void;
}

const templates = [
  {
    id: 'modern',
    name: 'Modern Minimal',
    description: 'Clean and professional',
    gradient: 'from-slate-500 to-slate-700',
  },
  {
    id: 'vibrant',
    name: 'Vibrant Energy',
    description: 'Bold and colorful',
    gradient: 'from-pink-500 to-orange-500',
  },
  {
    id: 'cinematic',
    name: 'Cinematic',
    description: 'Movie-like quality',
    gradient: 'from-indigo-500 to-purple-600',
  },
  {
    id: 'corporate',
    name: 'Corporate',
    description: 'Professional business',
    gradient: 'from-blue-500 to-cyan-600',
  },
  {
    id: 'creative',
    name: 'Creative',
    description: 'Artistic and unique',
    gradient: 'from-violet-500 to-fuchsia-600',
  },
  {
    id: 'minimal',
    name: 'Minimal',
    description: 'Simple and elegant',
    gradient: 'from-gray-400 to-gray-600',
  },
];

export function TemplateSelector({ selected, onSelect }: TemplateSelectorProps) {
  return (
    <div className="space-y-4">
      <p className="text-sm text-muted-foreground">
        Choose a template to style your video
      </p>
      
      <div className="grid grid-cols-2 gap-4">
        {templates.map((template, index) => (
          <motion.button
            key={template.id}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: index * 0.05 }}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => onSelect(template.id)}
            className={`relative p-4 rounded-lg border-2 transition-all text-left ${
              selected === template.id
                ? 'border-primary bg-primary/5'
                : 'border-border hover:border-primary/50'
            }`}
          >
            {/* Template preview */}
            <div className={`aspect-video rounded-md bg-gradient-to-br ${template.gradient} mb-3`} />
            
            {/* Template info */}
            <div>
              <h4 className="font-semibold text-sm">{template.name}</h4>
              <p className="text-xs text-muted-foreground mt-1">{template.description}</p>
            </div>

            {/* Selected indicator */}
            {selected === template.id && (
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                className="absolute top-2 right-2 w-6 h-6 rounded-full bg-primary flex items-center justify-center"
              >
                <CheckCircle2 className="w-4 h-4 text-white" />
              </motion.div>
            )}
          </motion.button>
        ))}
      </div>
    </div>
  );
}
