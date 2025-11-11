'use client';

import { motion } from 'framer-motion';
import { Video, HardDrive, Clock, Zap } from 'lucide-react';
import { cn } from '@/lib/utils';

type StatCardProps = {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  trend?: {
    value: string;
    isPositive: boolean;
  };
  className?: string;
};

const StatCard = ({ title, value, icon, trend, className }: StatCardProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={cn(
        'bg-card rounded-xl p-6 shadow-sm border border-border/50',
        'transition-all hover:shadow-md',
        className
      )}
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-muted-foreground">{title}</p>
          <div className="mt-2 flex items-baseline gap-2">
            <h3 className="text-2xl font-bold">{value}</h3>
            {trend && (
              <span
                className={cn(
                  'text-xs font-medium px-2 py-0.5 rounded-full',
                  trend.isPositive
                    ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
                    : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
                )}
              >
                {trend.isPositive ? '↑' : '↓'} {trend.value}
              </span>
            )}
          </div>
        </div>
        <div className="p-2 rounded-lg bg-primary/10 text-primary">
          {icon}
        </div>
      </div>
    </motion.div>
  );
};

type StatsCardsProps = {
  stats: {
    totalVideos: number;
    storageUsed: string;
    videosThisMonth: number;
    apiCalls: number;
  };
};

export function StatsCards({ stats }: StatsCardsProps) {
  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <StatCard
        title="Total Videos"
        value={stats.totalVideos}
        icon={<Video className="h-5 w-5" />}
        trend={{ value: '12%', isPositive: true }}
      />
      <StatCard
        title="Storage Used"
        value={stats.storageUsed}
        icon={<HardDrive className="h-5 w-5" />}
      />
      <StatCard
        title="Videos This Month"
        value={stats.videosThisMonth}
        icon={<Clock className="h-5 w-5" />}
        trend={{ value: '5%', isPositive: true }}
      />
      <StatCard
        title="API Calls"
        value={stats.apiCalls}
        icon={<Zap className="h-5 w-5" />}
        trend={{ value: '8%', isPositive: false }}
      />
    </div>
  );
}
