'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Download, Play } from 'lucide-react';

interface ResultDisplayProps {
  videoUrl: string;
}

export default function ResultDisplay({ videoUrl }: ResultDisplayProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Video Generated Successfully!</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="aspect-video bg-muted rounded-lg flex items-center justify-center">
          <video
            src={videoUrl}
            controls
            className="w-full h-full rounded-lg"
          />
        </div>
        <div className="flex gap-2">
          <Button asChild className="flex-1">
            <a href={videoUrl} download>
              <Download className="w-4 h-4 mr-2" />
              Download
            </a>
          </Button>
          <Button variant="outline" asChild>
            <a href={videoUrl} target="_blank" rel="noopener noreferrer">
              <Play className="w-4 h-4 mr-2" />
              Open in New Tab
            </a>
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}