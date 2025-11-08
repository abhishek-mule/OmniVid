'use client';

import { motion } from 'framer-motion';
import { Video, Clock, TrendingUp, Users, Play, Download, MoreVertical } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import Link from 'next/link';

const stats = [
  {
    label: 'Total Videos',
    value: '24',
    change: '+12%',
    icon: Video,
    gradient: 'from-violet-500 to-purple-500',
  },
  {
    label: 'Watch Time',
    value: '156h',
    change: '+23%',
    icon: Clock,
    gradient: 'from-cyan-500 to-blue-500',
  },
  {
    label: 'Total Views',
    value: '12.5K',
    change: '+18%',
    icon: TrendingUp,
    gradient: 'from-pink-500 to-rose-500',
  },
  {
    label: 'Engagement',
    value: '8.2%',
    change: '+5%',
    icon: Users,
    gradient: 'from-amber-500 to-orange-500',
  },
];

const recentVideos = [
  {
    id: '1',
    title: 'Product Launch Video',
    status: 'completed',
    duration: '2:34',
    views: '1.2K',
    createdAt: '2 hours ago',
    thumbnail: 'gradient-to-br from-violet-500 to-purple-600',
  },
  {
    id: '2',
    title: 'Marketing Campaign',
    status: 'processing',
    duration: '1:45',
    views: '—',
    createdAt: '5 hours ago',
    thumbnail: 'gradient-to-br from-cyan-500 to-blue-600',
  },
  {
    id: '3',
    title: 'Tutorial Series - Part 1',
    status: 'completed',
    duration: '5:12',
    views: '3.4K',
    createdAt: '1 day ago',
    thumbnail: 'gradient-to-br from-pink-500 to-rose-600',
  },
];

export function DashboardOverview() {
  return (
    <div className="space-y-8">
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            whileHover={{ y: -4 }}
            className="relative group"
          >
            <div className="relative p-6 rounded-2xl border border-border bg-card backdrop-blur-sm transition-all duration-300 hover:border-primary/50 hover:shadow-xl hover:shadow-primary/10">
              {/* Icon */}
              <div className={`inline-flex p-3 rounded-xl bg-gradient-to-br ${stat.gradient} mb-4`}>
                <stat.icon className="w-6 h-6 text-white" />
              </div>

              {/* Stats */}
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">{stat.label}</p>
                <div className="flex items-end gap-2">
                  <h3 className="text-3xl font-bold">{stat.value}</h3>
                  <span className="text-sm font-medium text-green-500 mb-1">{stat.change}</span>
                </div>
              </div>

              {/* Hover glow */}
              <div className={`absolute inset-0 rounded-2xl bg-gradient-to-br ${stat.gradient} opacity-0 group-hover:opacity-5 transition-opacity duration-300 -z-10`} />
            </div>
          </motion.div>
        ))}
      </div>

      {/* Recent Videos */}
      <div>
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold">Recent Videos</h2>
          <Button variant="outline" asChild>
            <Link href="/dashboard/videos">View All</Link>
          </Button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {recentVideos.map((video, index) => (
            <motion.div
              key={video.id}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.1 }}
              whileHover={{ scale: 1.02 }}
              className="group relative cursor-pointer"
            >
              <div className="relative overflow-hidden rounded-2xl border border-border bg-card backdrop-blur-sm">
                {/* Thumbnail */}
                <div className={`relative aspect-video bg-${video.thumbnail} flex items-center justify-center`}>
                  <motion.div
                    whileHover={{ scale: 1.1 }}
                    className="w-12 h-12 rounded-full bg-white/20 backdrop-blur-md flex items-center justify-center border border-white/30 group-hover:bg-white/30 transition-all"
                  >
                    <Play className="w-6 h-6 text-white ml-0.5" />
                  </motion.div>

                  {/* Status badge */}
                  <div className="absolute top-3 left-3">
                    <Badge
                      variant={video.status === 'completed' ? 'default' : 'secondary'}
                      className="capitalize"
                    >
                      {video.status}
                    </Badge>
                  </div>

                  {/* Duration */}
                  <div className="absolute bottom-3 right-3 px-2 py-1 rounded-md bg-black/60 backdrop-blur-sm text-white text-xs font-medium">
                    {video.duration}
                  </div>
                </div>

                {/* Info */}
                <div className="p-4">
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      <h3 className="font-semibold truncate">{video.title}</h3>
                      <div className="flex items-center gap-3 mt-2 text-sm text-muted-foreground">
                        <span>{video.views} views</span>
                        <span>•</span>
                        <span>{video.createdAt}</span>
                      </div>
                    </div>
                    <Button variant="ghost" size="icon" className="flex-shrink-0">
                      <MoreVertical className="w-4 h-4" />
                    </Button>
                  </div>

                  {/* Actions */}
                  {video.status === 'completed' && (
                    <div className="flex gap-2 mt-4">
                      <Button variant="outline" size="sm" className="flex-1">
                        <Play className="w-3 h-3 mr-1" />
                        Play
                      </Button>
                      <Button variant="outline" size="sm" className="flex-1">
                        <Download className="w-3 h-3 mr-1" />
                        Download
                      </Button>
                    </div>
                  )}
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}
