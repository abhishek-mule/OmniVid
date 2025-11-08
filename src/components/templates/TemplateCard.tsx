'use client';

import { motion } from 'framer-motion';
import { Play, Star, Download, Clock, Zap } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

interface TemplateCardProps {
  id: string;
  name: string;
  description: string;
  category: string;
  style: string;
  difficulty: 'Easy' | 'Medium' | 'Hard';
  duration: string;
  rating: number;
  downloads: string;
  gradient: string;
  tags: string[];
  onSelect: (id: string) => void;
}

export function TemplateCard({
  id,
  name,
  description,
  category,
  style,
  difficulty,
  duration,
  rating,
  downloads,
  gradient,
  tags,
  onSelect,
}: TemplateCardProps) {
  const difficultyColors = {
    Easy: 'bg-green-100 text-green-800',
    Medium: 'bg-yellow-100 text-yellow-800',
    Hard: 'bg-red-100 text-red-800',
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -5, transition: { duration: 0.2 } }}
      className="group relative overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm transition-all hover:shadow-md dark:border-gray-800 dark:bg-gray-900"
    >
      {/* Thumbnail */}
      <div className="relative aspect-video overflow-hidden">
        <div
          className={`absolute inset-0 bg-gradient-to-br ${gradient} flex items-center justify-center`}
        >
          <Play className="h-12 w-12 text-white/80 transition-all group-hover:scale-110" />
        </div>
        
        {/* Difficulty Badge */}
        <div className="absolute right-2 top-2">
          <span
            className={cn(
              'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium',
              difficultyColors[difficulty]
            )}
          >
            {difficulty}
          </span>
        </div>
        
        {/* Hover Overlay */}
        <div className="absolute inset-0 flex items-center justify-center bg-black/50 opacity-0 transition-opacity group-hover:opacity-100">
          <Button
            variant="secondary"
            className="flex items-center gap-2 bg-white/90 text-gray-900 hover:bg-white"
            onClick={() => onSelect(id)}
          >
            <Play className="h-4 w-4" />
            Preview
          </Button>
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        <div className="mb-2 flex items-start justify-between">
          <h3 className="font-medium text-gray-900 dark:text-gray-100">{name}</h3>
          <div className="flex items-center text-sm text-amber-500">
            <Star className="mr-1 h-4 w-4 fill-current" />
            <span>{rating}</span>
          </div>
        </div>
        
        <p className="mb-3 text-sm text-gray-600 dark:text-gray-400 line-clamp-2">
          {description}
        </p>
        
        <div className="mb-3 flex items-center justify-between text-xs text-gray-500 dark:text-gray-500">
          <div className="flex items-center gap-2">
            <Clock className="h-3.5 w-3.5" />
            <span>{duration}</span>
          </div>
          <div className="flex items-center gap-2">
            <Download className="h-3.5 w-3.5" />
            <span>{downloads}</span>
          </div>
        </div>
        
        <div className="flex flex-wrap gap-2">
          {tags.map((tag) => (
            <Badge
              key={tag}
              variant="outline"
              className="text-xs text-gray-600 dark:text-gray-400"
            >
              {tag}
            </Badge>
          ))}
        </div>
        
        <Button 
          className="mt-4 w-full"
          onClick={() => onSelect(id)}
        >
          <Zap className="mr-2 h-4 w-4" />
          Use Template
        </Button>
      </div>
    </motion.div>
  );
}
