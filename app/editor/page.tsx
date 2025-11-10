"use client";
import dynamic from 'next/dynamic';
import { Suspense } from 'react';
import { Skeleton } from '@/components/ui/skeleton';

// Dynamically import the editor component with no SSR
const VideoEditor = dynamic(
  () => import('@/components/editor/VideoEditor'),
  { 
    ssr: false,
    loading: () => (
      <div className="w-full h-screen flex items-center justify-center">
        <Skeleton className="w-full h-full" />
      </div>
    )
  }
);

export default function EditorRoute() {
  return (
    <div className="min-h-screen bg-background">
      <Suspense fallback={
        <div className="w-full h-screen flex items-center justify-center">
          <Skeleton className="w-full h-full" />
        </div>
      }>
        <VideoEditor />
      </Suspense>
    </div>
  );
}