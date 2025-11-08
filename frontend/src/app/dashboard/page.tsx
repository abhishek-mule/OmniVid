'use client';

import { useState, useMemo, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Plus } from 'lucide-react';
import { Navbar } from '@/components/navbar';
import { StatsCards } from '@/components/dashboard/stats-cards';
import { VideoCard } from '@/components/dashboard/video-card';
import { Filters } from '@/components/dashboard/filters';
import { Pagination } from '@/components/dashboard/pagination';
import { motion, AnimatePresence } from 'framer-motion';

// Mock data - replace with actual API calls
type Video = {
  id: string;
  title: string;
  description: string;
  duration: string;
  resolution: string;
  thumbnail: string | null;
  createdAt: string;
  size: string;
  format: string;
  tags: string[];
};

const MOCK_VIDEOS: Video[] = [
  {
    id: '1',
    title: 'Product Demo Video',
    description: 'A showcase of our latest product features and capabilities',
    duration: '2:34',
    resolution: '4K',
    thumbnail: null,
    createdAt: '2 hours ago',
    size: '45.7 MB',
    format: 'MP4',
    tags: ['product', 'demo', 'features']
  },
  {
    id: '2',
    title: 'Marketing Campaign - Summer Sale',
    description: 'Promotional video for the upcoming summer sale event',
    duration: '1:45',
    resolution: '1080p',
    thumbnail: null,
    createdAt: '5 hours ago',
    size: '32.1 MB',
    format: 'MP4',
    tags: ['marketing', 'sale', 'promotion']
  },
  {
    id: '3',
    title: 'Tutorial Series - Getting Started',
    description: 'Learn how to get started with our platform',
    duration: '5:12',
    resolution: '720p',
    thumbnail: null,
    createdAt: '1 day ago',
    size: '78.3 MB',
    format: 'MP4',
    tags: ['tutorial', 'getting started', 'guide']
  },
  {
    id: '4',
    title: 'Customer Testimonial - Acme Corp',
    description: 'Hear what our customers have to say about our services',
    duration: '3:21',
    resolution: '4K',
    thumbnail: null,
    createdAt: '2 days ago',
    size: '62.5 MB',
    format: 'MP4',
    tags: ['testimonial', 'customer', 'review']
  },
  {
    id: '5',
    title: 'Behind the Scenes - Office Tour',
    description: 'Take a look inside our creative workspace',
    duration: '4:15',
    resolution: '1080p',
    thumbnail: null,
    createdAt: '3 days ago',
    size: '85.2 MB',
    format: 'MP4',
    tags: ['behind the scenes', 'office', 'culture']
  },
  {
    id: '6',
    title: 'How to Use Advanced Features',
    description: 'A detailed guide on using advanced platform features',
    duration: '7:42',
    resolution: '1080p',
    thumbnail: null,
    createdAt: '1 week ago',
    size: '112.8 MB',
    format: 'MP4',
    tags: ['tutorial', 'advanced', 'features']
  }
];

export default function Dashboard() {
  // State for filters and pagination
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('newest');
  const [filterBy, setFilterBy] = useState('all');
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 8;

  // Mock user stats
  const userStats = {
    totalVideos: 24,
    storageUsed: '1.2 GB',
    videosThisMonth: 8,
    apiCalls: 142
  };

  // Filter and sort videos
  const filteredVideos = useMemo(() => {
    let result = [...MOCK_VIDEOS];

    // Apply search
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      result = result.filter(
        (video) =>
          video.title.toLowerCase().includes(query) ||
          video.description.toLowerCase().includes(query) ||
          video.tags.some((tag) => tag.toLowerCase().includes(query))
      );
    }

    // Apply filters
    if (filterBy !== 'all') {
      result = result.filter((video) => {
        if (filterBy === '4k') return video.resolution === '4K';
        if (filterBy === 'hd') return video.resolution === '1080p';
        if (filterBy === 'sd') return video.resolution === '720p';
        
        // Date filters (simplified for demo)
        if (filterBy === 'today') return video.createdAt.includes('hour') || video.createdAt.includes('today');
        if (filterBy === 'week') return !video.createdAt.includes('month') && !video.createdAt.includes('year');
        if (filterBy === 'month') return !video.createdAt.includes('year');
        
        return true;
      });
    }

    // Apply sorting
    result.sort((a, b) => {
      if (sortBy === 'newest') return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime();
      if (sortBy === 'oldest') return new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime();
      if (sortBy === 'title-asc') return a.title.localeCompare(b.title);
      if (sortBy === 'title-desc') return b.title.localeCompare(a.title);
      return 0;
    });

    return result;
  }, [searchQuery, sortBy, filterBy]);

  // Pagination
  const totalPages = Math.ceil(filteredVideos.length / itemsPerPage);
  const paginatedVideos = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage;
    return filteredVideos.slice(startIndex, startIndex + itemsPerPage);
  }, [filteredVideos, currentPage, itemsPerPage]);

  // Handlers
  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleClearFilters = () => {
    setSearchQuery('');
    setSortBy('newest');
    setFilterBy('all');
    setCurrentPage(1);
  };

  // Video actions
  const handlePlayVideo = (id: string) => {
    console.log('Playing video:', id);
    // Implement video playback
  };

  const handleDownloadVideo = (id: string) => {
    console.log('Downloading video:', id);
    // Implement download
  };

  const handleDeleteVideo = (id: string) => {
    console.log('Deleting video:', id);
    // Implement delete with confirmation
    // setVideos(videos.filter(video => video.id !== id));
  };

  const handleShareVideo = (id: string) => {
    console.log('Sharing video:', id);
    // Implement share functionality
  };

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      <main className="container mx-auto px-4 sm:px-6 lg:px-8 pt-24 pb-16">
        <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
            <p className="mt-2 text-muted-foreground">
              Welcome back! Here's an overview of your video projects
            </p>
          </div>
          <Button className="gap-2">
            <Plus className="h-4 w-4" />
            New Video
          </Button>
        </div>

        {/* Stats Cards */}
        <div className="mb-8">
          <StatsCards stats={userStats} />
        </div>

        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4 mb-12">
          <div className="p-6 rounded-xl border border-border bg-card">
            <div className="flex items-center gap-4">
              <div className="p-3 rounded-lg bg-primary/10">
                <Video className="h-6 w-6 text-primary" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Total Videos</p>
                <p className="text-2xl font-bold">24</p>
              </div>
            </div>
          </div>

          <div className="p-6 rounded-xl border border-border bg-card">
            <div className="flex items-center gap-4">
              <div className="p-3 rounded-lg bg-primary/10">
                <Clock className="h-6 w-6 text-primary" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">In Progress</p>
                <p className="text-2xl font-bold">3</p>
              </div>
            </div>
          </div>

          <div className="p-6 rounded-xl border border-border bg-card">
            <div className="flex items-center gap-4">
              <div className="p-3 rounded-lg bg-primary/10">
                <Download className="h-6 w-6 text-primary" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Downloads</p>
                <p className="text-2xl font-bold">156</p>
              </div>
            </div>
          </div>

          <div className="p-6 rounded-xl border border-border bg-card">
            <div className="flex items-center gap-4">
              <div className="p-3 rounded-lg bg-primary/10">
                <Play className="h-6 w-6 text-primary" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Total Views</p>
                <p className="text-2xl font-bold">2.4K</p>
              </div>
            </div>
          </div>
        </div>

        <div>
          <h2 className="text-xl font-semibold mb-6">Recent Videos</h2>
          {/* Filters */}
          <div className="mb-6">
            <Filters
              searchQuery={searchQuery}
              onSearchChange={setSearchQuery}
              sortBy={sortBy}
              onSortChange={setSortBy}
              filterBy={filterBy}
              onFilterChange={setFilterBy}
              onClearFilters={handleClearFilters}
            />
          </div>

          {/* Video Grid */}
          {filteredVideos.length > 0 ? (
            <>
              <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                <AnimatePresence>
                  {paginatedVideos.map((video) => (
                    <VideoCard
                      key={video.id}
                      id={video.id}
                      title={video.title}
                      thumbnail={video.thumbnail}
                      duration={video.duration}
                      resolution={video.resolution}
                      createdAt={video.createdAt}
                      onPlay={handlePlayVideo}
                      onDownload={handleDownloadVideo}
                      onDelete={handleDeleteVideo}
                      onShare={handleShareVideo}
                    />
                  ))}
                </AnimatePresence>
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="mt-8">
                  <Pagination
                    currentPage={currentPage}
                    totalPages={totalPages}
                    onPageChange={handlePageChange}
                  />
                </div>
              )}
            </>
          ) : (
            <div className="flex flex-col items-center justify-center rounded-lg border border-dashed border-border p-12 text-center">
              <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-muted">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="24"
                  height="24"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  className="h-6 w-6 text-muted-foreground"
                >
                  <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
                  <polyline points="14 2 14 8 20 8" />
                </svg>
              </div>
              <h3 className="mt-4 text-lg font-medium">No videos found</h3>
              <p className="mt-2 text-sm text-muted-foreground">
                Try adjusting your search or filter criteria
              </p>
              <Button className="mt-4" onClick={handleClearFilters}>
                Clear filters
              </Button>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
