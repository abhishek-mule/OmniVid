'use client';

import { motion } from 'framer-motion';
import { Play, Loader2 } from 'lucide-react';

interface VideoPreviewProps {
  url: string | null;
  isGenerating: boolean;
}

export function VideoPreview({ url, isGenerating }: VideoPreviewProps) {
  return (
    <div className="relative aspect-video rounded-lg overflow-hidden bg-muted border border-border">
      {isGenerating ? (
        <div className="absolute inset-0 flex flex-col items-center justify-center bg-gradient-to-br from-violet-500/10 via-fuchsia-500/10 to-pink-500/10">
          <motion.div
            animate={{
              scale: [1, 1.2, 1],
              rotate: [0, 180, 360],
            }}
            transition={{
              duration: 3,
              repeat: Infinity,
              ease: "easeInOut",
            }}
          >
            <Loader2 className="w-12 h-12 text-primary" />
          </motion.div>
          <p className="mt-4 text-sm text-muted-foreground">Generating your video...</p>
        </div>
      ) : url ? (
        <video
          src={url}
          controls
          className="w-full h-full object-cover"
        />
      ) : (
        <div className="absolute inset-0 flex flex-col items-center justify-center bg-gradient-to-br from-muted/50 to-muted">
          <motion.div
            whileHover={{ scale: 1.1 }}
            className="w-16 h-16 rounded-full bg-primary/20 flex items-center justify-center backdrop-blur-sm border border-primary/30"
          >
            <Play className="w-8 h-8 text-primary ml-1" />
          </motion.div>
          <p className="mt-4 text-sm text-muted-foreground">Preview will appear here</p>
        </div>
      )}
    </div>
  );
}
