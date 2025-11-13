a'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Download, Play, Loader2 } from 'lucide-react';

interface ResultDisplayProps {
  result: string | null;
  isLoading: boolean;
}

export default function ResultDisplay({ result, isLoading }: ResultDisplayProps) {
  // YouTube video ID extraction
  const youtubeVideoId = 'XXtKO3B-mcM';
  const youtubeEmbedUrl = `https://www.youtube.com/embed/${youtubeVideoId}`;

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Generating Video...</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="aspect-video bg-muted rounded-lg flex items-center justify-center">
            <Loader2 className="w-8 h-8 animate-spin text-primary" />
          </div>
          <p className="text-center text-muted-foreground">Please wait while we create your video...</p>
        </CardContent>
      </Card>
    );
  }

  if (!result) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Video Preview</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="aspect-video bg-muted rounded-lg flex items-center justify-center">
            <iframe
              src={youtubeEmbedUrl}
              title="Video Preview"
              className="w-full h-full rounded-lg"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
            />
          </div>
          <p className="text-center text-muted-foreground">Sample video preview</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Video Generated Successfully!</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="aspect-video bg-muted rounded-lg flex items-center justify-center">
          <iframe
            src={youtubeEmbedUrl}
            title="Generated Video"
            className="w-full h-full rounded-lg"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
          />
        </div>
        <p className="text-center text-muted-foreground">{result}</p>
        <div className="flex gap-2">
          <Button asChild className="flex-1">
            <a href={`https://youtu.be/${youtubeVideoId}`} target="_blank" rel="noopener noreferrer">
              <Download className="w-4 h-4 mr-2" />
              Download
            </a>
          </Button>
          <Button variant="outline" asChild>
            <a href={`https://youtu.be/${youtubeVideoId}`} target="_blank" rel="noopener noreferrer">
              <Play className="w-4 h-4 mr-2" />
              Watch on YouTube
            </a>
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}