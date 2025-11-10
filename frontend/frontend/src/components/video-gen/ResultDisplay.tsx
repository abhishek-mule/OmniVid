'use client';

import { motion } from 'framer-motion';
import { Download, Share2, Trash2, Play, CheckCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useState } from 'react';

interface ResultDisplayProps {
  videoUrl: string;
}

export default function ResultDisplay({ videoUrl }: ResultDisplayProps) {
  const [isPlaying, setIsPlaying] = useState(false);

  const handleDownload = () => {
    const link = document.createElement('a');
    link.href = videoUrl;
    link.download = `omnivid-${Date.now()}.mp4`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: 'Check out my AI-generated video!',
          text: 'Created with OmniVid AI',
          url: videoUrl
        });
      } catch (err) {
        console.log('Share cancelled');
      }
    } else {
      // Fallback: copy to clipboard
      navigator.clipboard.writeText(videoUrl);
      alert('Link copied to clipboard!');
    }
  };

  const handleDelete = () => {
    if (confirm('Are you sure you want to delete this video?')) {
      // Handle deletion
      console.log('Video deleted');
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="rounded-2xl border border-border bg-card overflow-hidden sticky top-24"
    >
      {/* Success Header */}
      <div className="bg-gradient-to-r from-green-500/10 to-emerald-500/10 border-b border-border p-4">
        <div className="flex items-center gap-2 text-green-600">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: "spring", stiffness: 200 }}
          >
            <CheckCircle className="w-5 h-5" />
          </motion.div>
          <span className="font-semibold">Video Generated Successfully!</span>
        </div>
      </div>

      {/* Video Player */}
      <div className="relative aspect-video bg-black group">
        <video
          src={videoUrl}
          controls
          className="w-full h-full"
          onPlay={() => setIsPlaying(true)}
          onPause={() => setIsPlaying(false)}
        />
        
        {!isPlaying && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="absolute inset-0 flex items-center justify-center bg-black/50 group-hover:bg-black/30 transition-colors pointer-events-none"
          >
            <motion.div
              whileHover={{ scale: 1.1 }}
              className="w-16 h-16 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center border-2 border-white/50"
            >
              <Play className="w-8 h-8 text-white ml-1" />
            </motion.div>
          </motion.div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="p-4 space-y-3">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <Button
            size="lg"
            className="w-full"
            onClick={handleDownload}
          >
            <Download className="w-4 h-4 mr-2" />
            Download Video
          </Button>
        </motion.div>

        <div className="grid grid-cols-2 gap-3">
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <Button
              variant="outline"
              className="w-full"
              onClick={handleShare}
            >
              <Share2 className="w-4 h-4 mr-2" />
              Share
            </Button>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <Button
              variant="outline"
              className="w-full text-red-500 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-950"
              onClick={handleDelete}
            >
              <Trash2 className="w-4 h-4 mr-2" />
              Delete
            </Button>
          </motion.div>
        </div>

        {/* Video Info */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="mt-4 p-3 rounded-lg bg-muted/50 border border-border"
        >
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div>
              <div className="text-muted-foreground text-xs mb-1">Resolution</div>
              <div className="font-medium">1920x1080</div>
            </div>
            <div>
              <div className="text-muted-foreground text-xs mb-1">Duration</div>
              <div className="font-medium">15 seconds</div>
            </div>
            <div>
              <div className="text-muted-foreground text-xs mb-1">Frame Rate</div>
              <div className="font-medium">30 fps</div>
            </div>
            <div>
              <div className="text-muted-foreground text-xs mb-1">File Size</div>
              <div className="font-medium">2.4 MB</div>
            </div>
          </div>
        </motion.div>

        {/* Generate Another */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="pt-3 border-t border-border"
        >
          <button
            onClick={() => window.location.reload()}
            className="w-full text-sm text-primary hover:text-primary/80 font-medium transition-colors"
          >
            Generate Another Video →
          </button>
        </motion.div>
      </div>
    </motion.div>
  );
}
