'use client';

import { motion } from 'framer-motion';
import { Play, Download, Trash2, Share2, MoreVertical } from 'lucide-react';
import Image from 'next/image';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

type VideoCardProps = {
  id: string;
  title: string;
  thumbnail?: string | null;
  duration: string;
  resolution: string;
  createdAt: string;
  onPlay: (id: string) => void;
  onDownload: (id: string) => void;
  onDelete: (id: string) => void;
  onShare: (id: string) => void;
};

export function VideoCard({
  id,
  title,
  thumbnail,
  duration,
  resolution,
  createdAt,
  onPlay,
  onDownload,
  onDelete,
  onShare,
}: VideoCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="group relative overflow-hidden rounded-xl border border-border/50 bg-card shadow-sm transition-all hover:shadow-md"
    >
      {/* Thumbnail with play button overlay */}
      <div className="relative aspect-video w-full overflow-hidden bg-muted">
        {thumbnail ? (
          <Image
            src={thumbnail}
            alt={title}
            fill
            className="object-cover transition-transform duration-300 group-hover:scale-105"
            sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
          />
        ) : (
          <div className="flex h-full items-center justify-center bg-gradient-to-br from-primary/10 to-primary/5">
            <Play className="h-10 w-10 text-primary/50" />
          </div>
        )}
        
        {/* Duration badge */}
        <Badge variant="secondary" className="absolute bottom-2 right-2">
          {duration}
        </Badge>
        
        {/* Play button overlay */}
        <button
          onClick={() => onPlay(id)}
          className="absolute inset-0 flex items-center justify-center bg-black/50 opacity-0 transition-opacity group-hover:opacity-100"
          aria-label={`Play ${title}`}
        >
          <div className="flex h-14 w-14 items-center justify-center rounded-full bg-white/90 text-primary">
            <Play className="h-6 w-6 fill-current" />
          </div>
        </button>
      </div>

      {/* Video info */}
      <div className="p-4">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h3 className="line-clamp-1 font-medium">{title}</h3>
            <p className="mt-1 text-sm text-muted-foreground">{createdAt}</p>
          </div>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8 rounded-full text-muted-foreground hover:bg-muted"
              >
                <MoreVertical className="h-4 w-4" />
                <span className="sr-only">More options</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-40">
              <DropdownMenuItem onClick={() => onDownload(id)}>
                <Download className="mr-2 h-4 w-4" />
                <span>Download</span>
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => onShare(id)}>
                <Share2 className="mr-2 h-4 w-4" />
                <span>Share</span>
              </DropdownMenuItem>
              <DropdownMenuItem
                className="text-destructive focus:text-destructive"
                onClick={() => onDelete(id)}
              >
                <Trash2 className="mr-2 h-4 w-4" />
                <span>Delete</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
        
        <div className="mt-3 flex items-center justify-between">
          <Badge variant="outline" className="text-xs">
            {resolution}
          </Badge>
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              className="h-8"
              onClick={() => onDownload(id)}
            >
              <Download className="mr-1.5 h-3.5 w-3.5" />
              <span>Download</span>
            </Button>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
