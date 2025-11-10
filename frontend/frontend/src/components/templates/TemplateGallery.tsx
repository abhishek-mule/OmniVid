'use client';

import { motion } from 'framer-motion';
import { Play, Star, Download } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

interface TemplateGalleryProps {
  category: string;
  style: string;
  searchQuery: string;
}

const templates = [
  {
    id: '1',
    name: 'Modern Product Showcase',
    category: 'marketing',
    style: 'modern',
    rating: 4.8,
    downloads: '12.5K',
    gradient: 'from-violet-500 to-purple-600',
    tags: ['Product', 'Commercial', 'Sleek'],
  },
  {
    id: '2',
    name: 'Cinematic Travel Vlog',
    category: 'entertainment',
    style: 'cinematic',
    rating: 4.9,
    downloads: '18.2K',
    gradient: 'from-cyan-500 to-blue-600',
    tags: ['Travel', 'Vlog', 'Cinematic'],
  },
  {
    id: '3',
    name: 'Corporate Presentation',
    category: 'business',
    style: 'corporate',
    rating: 4.7,
    downloads: '9.8K',
    gradient: 'from-slate-500 to-slate-700',
    tags: ['Business', 'Professional', 'Clean'],
  },
  {
    id: '4',
    name: 'Social Media Ad',
    category: 'marketing',
    style: 'vibrant',
    rating: 4.6,
    downloads: '15.3K',
    gradient: 'from-pink-500 to-rose-600',
    tags: ['Social', 'Ad', 'Energetic'],
  },
  {
    id: '5',
    name: 'Educational Tutorial',
    category: 'education',
    style: 'minimal',
    rating: 4.8,
    downloads: '11.1K',
    gradient: 'from-green-500 to-emerald-600',
    tags: ['Tutorial', 'Education', 'Clear'],
  },
  {
    id: '6',
    name: 'Event Highlights',
    category: 'entertainment',
    style: 'vibrant',
    rating: 4.9,
    downloads: '20.5K',
    gradient: 'from-amber-500 to-orange-600',
    tags: ['Event', 'Highlights', 'Dynamic'],
  },
  {
    id: '7',
    name: 'Tech Product Demo',
    category: 'technology',
    style: 'modern',
    rating: 4.7,
    downloads: '13.7K',
    gradient: 'from-indigo-500 to-purple-600',
    tags: ['Tech', 'Demo', 'Futuristic'],
  },
  {
    id: '8',
    name: 'Fashion Lookbook',
    category: 'lifestyle',
    style: 'creative',
    rating: 4.8,
    downloads: '16.9K',
    gradient: 'from-fuchsia-500 to-pink-600',
    tags: ['Fashion', 'Style', 'Artistic'],
  },
];

export function TemplateGallery({ category, style, searchQuery }: TemplateGalleryProps) {
  const filteredTemplates = templates.filter(template => {
    const matchesCategory = category === 'all' || template.category === category;
    const matchesStyle = style === 'all' || template.style === style;
    const matchesSearch = searchQuery === '' || 
      template.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      template.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));
    
    return matchesCategory && matchesStyle && matchesSearch;
  });

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
      {filteredTemplates.map((template, index) => (
        <motion.div
          key={template.id}
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: index * 0.05 }}
          whileHover={{ scale: 1.02 }}
          className="group relative cursor-pointer"
        >
          <div className="relative overflow-hidden rounded-2xl border border-border bg-card backdrop-blur-sm transition-all duration-300 hover:border-primary/50 hover:shadow-xl hover:shadow-primary/10">
            {/* Template Preview */}
            <div className={`relative aspect-video bg-gradient-to-br ${template.gradient} flex items-center justify-center`}>
              <motion.div
                whileHover={{ scale: 1.1 }}
                className="w-16 h-16 rounded-full bg-white/20 backdrop-blur-md flex items-center justify-center border border-white/30 group-hover:bg-white/30 transition-all"
              >
                <Play className="w-8 h-8 text-white ml-1" />
              </motion.div>

              {/* Rating badge */}
              <div className="absolute top-3 right-3 px-2 py-1 rounded-lg bg-black/60 backdrop-blur-sm flex items-center gap-1">
                <Star className="w-3 h-3 text-yellow-400 fill-yellow-400" />
                <span className="text-white text-xs font-medium">{template.rating}</span>
              </div>
            </div>

            {/* Template Info */}
            <div className="p-5">
              <h3 className="font-semibold text-lg mb-2">{template.name}</h3>
              
              {/* Tags */}
              <div className="flex flex-wrap gap-1.5 mb-3">
                {template.tags.map(tag => (
                  <Badge key={tag} variant="secondary" className="text-xs">
                    {tag}
                  </Badge>
                ))}
              </div>

              {/* Stats */}
              <div className="flex items-center justify-between text-sm text-muted-foreground mb-4">
                <div className="flex items-center gap-1">
                  <Download className="w-3.5 h-3.5" />
                  <span>{template.downloads}</span>
                </div>
                <span className="capitalize">{template.category}</span>
              </div>

              {/* Actions */}
              <div className="flex gap-2">
                <Button variant="outline" size="sm" className="flex-1">
                  Preview
                </Button>
                <Button size="sm" className="flex-1 bg-gradient-to-r from-violet-600 to-fuchsia-600 hover:from-violet-700 hover:to-fuchsia-700">
                  Use Template
                </Button>
              </div>
            </div>

            {/* Hover glow */}
            <div className={`absolute inset-0 rounded-2xl bg-gradient-to-br ${template.gradient} opacity-0 group-hover:opacity-5 transition-opacity duration-300 -z-10`} />
          </div>
        </motion.div>
      ))}

      {filteredTemplates.length === 0 && (
        <div className="col-span-full text-center py-20">
          <p className="text-xl text-muted-foreground">No templates found matching your criteria</p>
          <p className="text-sm text-muted-foreground mt-2">Try adjusting your filters or search query</p>
        </div>
      )}
    </div>
  );
}
