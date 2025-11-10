'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { useEffect, useState, useMemo } from 'react';
import { TemplateCard } from './TemplateCard';
import { Skeleton } from '@/components/ui/skeleton';
import { Button } from '@/components/ui/button';
import { Search, AlertCircle } from 'lucide-react';

interface TemplateGalleryProps {
  category: string;
  style: string;
  searchQuery: string;
}

type Difficulty = 'Easy' | 'Medium' | 'Hard';

interface Template {
  id: string;
  name: string;
  description: string;
  category: string;
  style: string;
  difficulty: Difficulty;
  duration: string;
  rating: number;
  downloads: string;
  gradient: string;
  tags: string[];
}

// Mock data - replace with API call in production
const mockTemplates: Template[] = [
  {
    id: '1',
    name: 'Modern Product Showcase',
    description: 'A sleek and modern template perfect for showcasing your latest product with smooth animations.',
    category: 'marketing',
    style: 'modern',
    difficulty: 'Medium',
    duration: '1-2 min',
    rating: 4.8,
    downloads: '12.5K',
    gradient: 'from-violet-500 to-purple-600',
    tags: ['Product', 'Commercial', 'Sleek'],
  },
  {
    id: '2',
    name: 'Cinematic Travel Vlog',
    description: 'Create stunning travel vlogs with this cinematic template featuring dynamic transitions.',
    category: 'entertainment',
    style: 'cinematic',
    difficulty: 'Hard',
    duration: '3-5 min',
    rating: 4.9,
    downloads: '18.2K',
    gradient: 'from-cyan-500 to-blue-600',
    tags: ['Travel', 'Vlog', 'Cinematic'],
  },
  {
    id: '3',
    name: 'Corporate Presentation',
    description: 'Professional template designed for business presentations and company overviews.',
    category: 'business',
    style: 'corporate',
    difficulty: 'Easy',
    duration: '2-3 min',
    rating: 4.7,
    downloads: '9.8K',
    gradient: 'from-slate-500 to-slate-700',
    tags: ['Business', 'Professional', 'Clean'],
  },
  {
    id: '4',
    name: 'Social Media Ad',
    description: 'Eye-catching template optimized for social media platforms with square and vertical formats.',
    category: 'marketing',
    style: 'vibrant',
    difficulty: 'Medium',
    duration: '0:30-1:00',
    rating: 4.6,
    downloads: '15.3K',
    gradient: 'from-pink-500 to-rose-600',
    tags: ['Social', 'Ad', 'Energetic'],
  },
  {
    id: '5',
    name: 'Educational Tutorial',
    description: 'Clean and clear template designed for educational content and tutorials.',
    category: 'education',
    style: 'minimal',
    difficulty: 'Easy',
    duration: '5-10 min',
    rating: 4.8,
    downloads: '11.1K',
    gradient: 'from-green-500 to-emerald-600',
    tags: ['Tutorial', 'Education', 'Clear'],
  },
  {
    id: '6',
    name: 'Tech Product Launch',
    description: 'Perfect for showcasing new tech products with futuristic animations and transitions.',
    category: 'technology',
    style: 'modern',
    difficulty: 'Hard',
    duration: '2-3 min',
    rating: 4.9,
    downloads: '14.7K',
    gradient: 'from-blue-500 to-indigo-600',
    tags: ['Tech', 'Product', 'Innovation'],
  },
  {
    id: '7',
    name: 'Fitness Motivation',
    description: 'Energetic template designed for fitness content and workout videos.',
    category: 'lifestyle',
    style: 'vibrant',
    difficulty: 'Medium',
    duration: '1-2 min',
    rating: 4.7,
    downloads: '8.9K',
    gradient: 'from-orange-500 to-amber-600',
    tags: ['Fitness', 'Health', 'Motivation'],
  },
  {
    id: '8',
    name: 'Cooking Show',
    description: 'Beautiful template for cooking tutorials and recipe videos with a warm, inviting feel.',
    category: 'lifestyle',
    style: 'creative',
    difficulty: 'Easy',
    duration: '3-5 min',
    rating: 4.8,
    downloads: '10.2K',
    gradient: 'from-amber-500 to-yellow-600',
    tags: ['Cooking', 'Food', 'Recipe'],
  },
];

export function TemplateGallery({ category, style, searchQuery }: TemplateGalleryProps) {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Simulate API fetch
  useEffect(() => {
    const fetchTemplates = async () => {
      try {
        setIsLoading(true);
        // In a real app, you would fetch from your API:
        // const response = await fetch('/api/templates');
        // const data = await response.json();
        // setTemplates(data);
        
        // Using mock data for now
        setTimeout(() => {
          setTemplates(mockTemplates);
          setIsLoading(false);
        }, 800);
      } catch (err) {
        console.error('Error fetching templates:', err);
        setError('Failed to load templates. Please try again later.');
        setIsLoading(false);
      }
    };

    fetchTemplates();
  }, []);

  // Filter templates based on category, style, and search query
  const filteredTemplates = useMemo(() => {
    return templates.filter((template) => {
      const matchesCategory = category === 'all' || template.category === category;
      const matchesStyle = style === 'all' || template.style === style;
      const matchesSearch = 
        searchQuery === '' || 
        template.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        template.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        template.tags.some(tag => 
          tag.toLowerCase().includes(searchQuery.toLowerCase())
        );
      
      return matchesCategory && matchesStyle && matchesSearch;
    });
  }, [templates, category, style, searchQuery]);

  const handleTemplateSelect = (templateId: string) => {
    // Handle template selection (e.g., navigate to editor with template)
    console.log('Selected template:', templateId);
    // router.push(`/editor?template=${templateId}`);
  };

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {[...Array(8)].map((_, i) => (
          <div key={i} className="space-y-3">
            <Skeleton className="h-48 w-full rounded-xl" />
            <Skeleton className="h-4 w-3/4" />
            <Skeleton className="h-4 w-1/2" />
          </div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="text-red-500 mb-4">
          <AlertCircle className="h-12 w-12 mx-auto" />
        </div>
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
          Something went wrong
        </h3>
        <p className="text-gray-600 dark:text-gray-400 mb-4">{error}</p>
        <Button 
          onClick={() => window.location.reload()} 
          variant="outline"
          className="mx-auto"
        >
          Try again
        </Button>
      </div>
    );
  }

  if (filteredTemplates.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-gray-400 mb-4">
          <Search className="h-12 w-12 mx-auto" />
        </div>
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
          No templates found
        </h3>
        <p className="text-gray-600 dark:text-gray-400">
          Try adjusting your search or filter criteria
        </p>
      </div>
    );
  }

  return (
    <AnimatePresence>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {filteredTemplates.map((template, index) => (
          <motion.div
            key={template.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
            layout
          >
            <TemplateCard
              {...template}
              onSelect={handleTemplateSelect}
            />
          </motion.div>
        ))}
      </div>
    </AnimatePresence>
  );
}
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
