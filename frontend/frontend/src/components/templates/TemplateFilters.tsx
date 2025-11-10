'use client';

import { motion } from 'framer-motion';
import { Search } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';

interface TemplateFiltersProps {
  selectedCategory: string;
  selectedStyle: string;
  searchQuery: string;
  onCategoryChange: (category: string) => void;
  onStyleChange: (style: string) => void;
  onSearchChange: (query: string) => void;
}

const categories = [
  { id: 'all', label: 'All' },
  { id: 'marketing', label: 'Marketing' },
  { id: 'business', label: 'Business' },
  { id: 'education', label: 'Education' },
  { id: 'entertainment', label: 'Entertainment' },
  { id: 'technology', label: 'Technology' },
  { id: 'lifestyle', label: 'Lifestyle' },
];

const styles = [
  { id: 'all', label: 'All Styles' },
  { id: 'modern', label: 'Modern' },
  { id: 'cinematic', label: 'Cinematic' },
  { id: 'corporate', label: 'Corporate' },
  { id: 'vibrant', label: 'Vibrant' },
  { id: 'minimal', label: 'Minimal' },
  { id: 'creative', label: 'Creative' },
];

export function TemplateFilters({
  selectedCategory,
  selectedStyle,
  searchQuery,
  onCategoryChange,
  onStyleChange,
  onSearchChange,
}: TemplateFiltersProps) {
  return (
    <div className="space-y-6 mb-12">
      {/* Search */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="relative max-w-2xl mx-auto"
      >
        <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
        <Input
          type="text"
          placeholder="Search templates..."
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          className="pl-12 h-12 text-base border-2 focus:border-primary/50"
        />
      </motion.div>

      {/* Category Filters */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <h3 className="text-sm font-semibold mb-3">Category</h3>
        <div className="flex flex-wrap gap-2">
          {categories.map((category) => (
            <motion.button
              key={category.id}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => onCategoryChange(category.id)}
              className={`px-4 py-2 rounded-lg border-2 transition-all ${
                selectedCategory === category.id
                  ? 'border-primary bg-primary/10 text-primary font-semibold'
                  : 'border-border hover:border-primary/50'
              }`}
            >
              {category.label}
            </motion.button>
          ))}
        </div>
      </motion.div>

      {/* Style Filters */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <h3 className="text-sm font-semibold mb-3">Style</h3>
        <div className="flex flex-wrap gap-2">
          {styles.map((style) => (
            <motion.button
              key={style.id}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => onStyleChange(style.id)}
              className={`px-4 py-2 rounded-lg border-2 transition-all ${
                selectedStyle === style.id
                  ? 'border-primary bg-primary/10 text-primary font-semibold'
                  : 'border-border hover:border-primary/50'
              }`}
            >
              {style.label}
            </motion.button>
          ))}
        </div>
      </motion.div>
    </div>
  );
}
