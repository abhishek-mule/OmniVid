'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Navbar } from '@/components/navbar';
import { Footer } from '@/components/footer';
import { TemplateGallery } from '@/components/templates/TemplateGallery';
import { TemplateFilters } from '@/components/templates/TemplateFilters';

export default function TemplatesPage() {
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedStyle, setSelectedStyle] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      
      <div className="container mx-auto px-4 py-16 max-w-7xl">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <h1 className="text-5xl font-bold mb-4">
            <span className="bg-gradient-to-r from-violet-600 to-fuchsia-600 bg-clip-text text-transparent">
              Template Gallery
            </span>
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Choose from hundreds of professionally designed templates to kickstart your video creation
          </p>
        </motion.div>

        {/* Filters */}
        <TemplateFilters
          selectedCategory={selectedCategory}
          selectedStyle={selectedStyle}
          searchQuery={searchQuery}
          onCategoryChange={setSelectedCategory}
          onStyleChange={setSelectedStyle}
          onSearchChange={setSearchQuery}
        />

        {/* Gallery */}
        <TemplateGallery
          category={selectedCategory}
          style={selectedStyle}
          searchQuery={searchQuery}
        />
      </div>

      <Footer />
    </div>
  );
}
