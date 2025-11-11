'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { 
  Video, 
  Image as ImageIcon, 
  Music, 
  FileText, 
  Clock, 
  TrendingUp, 
  Users, 
  Zap, 
  ArrowUpRight, 
  Plus,
  Clock3,
  CheckCircle2,
  AlertCircle,
  PlayCircle
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';

type Project = {
  id: string;
  name: string;
  type: 'video' | 'image' | 'audio' | 'document';
  lastEdited: string;
  status: 'draft' | 'processing' | 'completed' | 'error';
  progress?: number;
};

type Activity = {
  id: string;
  type: 'created' | 'updated' | 'deleted' | 'processed' | 'shared';
  project: string;
  time: string;
  user: string;
};

const DashboardPage = () => {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);
  const [recentProjects, setRecentProjects] = useState<Project[]>([]);
  const [recentActivity, setRecentActivity] = useState<Activity[]>([]);
  const [storageUsage, setStorageUsage] = useState(0);
  const [apiUsage, setApiUsage] = useState(0);

  useEffect(() => {
    // Simulate loading data
    const loadData = async () => {
      setIsLoading(true);
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 800));
      
      // Mock data
      setRecentProjects([
        {
          id: '1',
          name: 'Product Launch Video',
          type: 'video',
          lastEdited: '2 hours ago',
          status: 'processing',
          progress: 65
        },
        {
          id: '2',
          name: 'Social Media Banner',
          type: 'image',
          lastEdited: '1 day ago',
          status: 'completed'
        },
        {
          id: '3',
          name: 'Podcast Intro',
          type: 'audio',
          lastEdited: '3 days ago',
          status: 'draft'
        },
        {
          id: '4',
          name: 'Tutorial Script',
          type: 'document',
          lastEdited: '1 week ago',
          status: 'draft'
        }
      ]);

      setRecentActivity([
        {
          id: 'a1',
          type: 'processed',
          project: 'Product Launch Video',
          time: '2 hours ago',
          user: 'You'
        },
        {
          id: 'a2',
          type: 'created',
          project: 'Social Media Banner',
          time: '1 day ago',
          user: 'You'
        },
        {
          id: 'a3',
          type: 'updated',
          project: 'Team Project',
          time: '2 days ago',
          user: 'Alex Johnson'
        },
        {
          id: 'a4',
          type: 'shared',
          project: 'Q3 Report',
          time: '3 days ago',
          user: 'You'
        }
      ]);

      setStorageUsage(45); // 45% of storage used
      setApiUsage(78); // 78% of API limit used
      
      setIsLoading(false);
    };

    loadData();
  }, []);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'processing':
        return <Clock3 className="w-4 h-4 text-amber-400" />;
      case 'completed':
        return <CheckCircle2 className="w-4 h-4 text-green-500" />;
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      default:
        return <FileText className="w-4 h-4 text-slate-400" />;
    }
  };

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'created':
        return <Plus className="w-4 h-4 text-green-500" />;
      case 'updated':
        return <ArrowUpRight className="w-4 h-4 text-blue-500" />;
      case 'deleted':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      case 'processed':
        return <PlayCircle className="w-4 h-4 text-purple-500" />;
      case 'shared':
        return <Users className="w-4 h-4 text-cyan-500" />;
      default:
        return <FileText className="w-4 h-4 text-slate-400" />;
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'video':
        return <Video className="w-4 h-4 text-red-500" />;
      case 'image':
        return <ImageIcon className="w-4 h-4 text-blue-500" />;
      case 'audio':
        return <Music className="w-4 h-4 text-purple-500" />;
      default:
        return <FileText className="w-4 h-4 text-slate-400" />;
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-900 p-4">
        <div className="animate-pulse flex flex-col items-center">
          <div className="w-16 h-16 bg-slate-800 rounded-full mb-4"></div>
          <div className="h-4 bg-slate-800 rounded w-48 mb-2"></div>
          <div className="h-3 bg-slate-800 rounded w-32"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900 text-white p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold">Dashboard</h1>
            <p className="text-slate-400">Welcome back! Here's what's happening with your projects.</p>
          </div>
          <div className="mt-4 md:mt-0 flex gap-3">
            <Button 
              variant="outline" 
              className="border-slate-700 text-slate-300 hover:bg-slate-800/50"
            >
              Import
            </Button>
            <Button 
              className="bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700"
              onClick={() => router.push('/generate')}
            >
              <Plus className="w-4 h-4 mr-2" />
              New Project
            </Button>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="border-slate-800 bg-slate-800/50">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-400">
                Total Projects
              </CardTitle>
              <div className="h-10 w-10 rounded-full bg-cyan-500/10 flex items-center justify-center">
                <FileText className="h-5 w-5 text-cyan-400" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">24</div>
              <p className="text-xs text-slate-400 mt-1">+12% from last month</p>
            </CardContent>
          </Card>

          <Card className="border-slate-800 bg-slate-800/50">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-400">
                Active Projects
              </CardTitle>
              <div className="h-10 w-10 rounded-full bg-purple-500/10 flex items-center justify-center">
                <Video className="h-5 w-5 text-purple-400" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">8</div>
              <p className="text-xs text-slate-400 mt-1">+2 from last week</p>
            </CardContent>
          </Card>

          <Card className="border-slate-800 bg-slate-800/50">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-400">
                Storage Used
              </CardTitle>
              <div className="h-10 w-10 rounded-full bg-blue-500/10 flex items-center justify-center">
                <TrendingUp className="h-5 w-5 text-blue-400" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{storageUsage}%</div>
              <div className="mt-2">
                <Progress value={storageUsage} className="h-2 bg-slate-700" />
              </div>
              <p className="text-xs text-slate-400 mt-1">14.2 GB of 30 GB used</p>
            </CardContent>
          </Card>

          <Card className="border-slate-800 bg-slate-800/50">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-400">
                API Usage
              </CardTitle>
              <div className="h-10 w-10 rounded-full bg-green-500/10 flex items-center justify-center">
                <Zap className="h-5 w-5 text-green-400" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{apiUsage}%</div>
              <div className="mt-2">
                <Progress value={apiUsage} className="h-2 bg-slate-700" />
              </div>
              <p className="text-xs text-slate-400 mt-1">78 of 100 requests used</p>
            </CardContent>
          </Card>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Recent Projects */}
          <div className="lg:col-span-2">
            <Card className="border-slate-800 bg-slate-800/50 h-full">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg">Recent Projects</CardTitle>
                  <Button variant="ghost" size="sm" className="text-cyan-400 hover:bg-slate-700/50">
                    View All
                  </Button>
                </div>
                <CardDescription>Your most recently edited projects</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {recentProjects.map((project) => (
                    <div 
                      key={project.id}
                      className="flex items-center justify-between p-4 rounded-lg hover:bg-slate-700/30 transition-colors cursor-pointer"
                      onClick={() => router.push(`/editor/${project.id}`)}
                    >
                      <div className="flex items-center space-x-4">
                        <div className="p-2 rounded-lg bg-slate-700/50">
                          {getTypeIcon(project.type)}
                        </div>
                        <div>
                          <h3 className="font-medium">{project.name}</h3>
                          <div className="flex items-center text-sm text-slate-400 mt-1">
                            <Clock className="w-3.5 h-3.5 mr-1" />
                            <span>{project.lastEdited}</span>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center">
                        {project.status === 'processing' && project.progress !== undefined ? (
                          <div className="flex items-center space-x-2">
                            <span className="text-sm text-amber-400">{project.progress}%</span>
                            <div className="w-20">
                              <Progress value={project.progress} className="h-1.5 bg-slate-700" />
                            </div>
                          </div>
                        ) : (
                          <div className="flex items-center text-sm text-slate-400">
                            {getStatusIcon(project.status)}
                            <span className="ml-1 capitalize">{project.status}</span>
                          </div>
                        )}
                        <Button variant="ghost" size="icon" className="ml-2 text-slate-400 hover:text-white">
                          <ArrowUpRight className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Recent Activity */}
          <div>
            <Card className="border-slate-800 bg-slate-800/50 h-full">
              <CardHeader>
                <CardTitle className="text-lg">Recent Activity</CardTitle>
                <CardDescription>Latest actions in your workspace</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  {recentActivity.map((activity) => (
                    <div key={activity.id} className="flex space-x-3">
                      <div className="flex-shrink-0 mt-0.5">
                        <div className="h-8 w-8 rounded-full bg-slate-700 flex items-center justify-center">
                          {getActivityIcon(activity.type)}
                        </div>
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium">
                          <span className="text-cyan-400">{activity.user}</span>{' '}
                          {activity.type} "{activity.project}"
                        </p>
                        <p className="text-xs text-slate-400 mt-0.5">{activity.time}</p>
                      </div>
                    </div>
                  ))}
                </div>
                <Button 
                  variant="ghost" 
                  size="sm" 
                  className="mt-6 w-full text-cyan-400 hover:bg-slate-700/50"
                >
                  View All Activity
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="mt-8">
          <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <Button 
              variant="outline" 
              className="h-24 flex flex-col items-center justify-center border-slate-800 bg-slate-800/30 hover:bg-slate-800/50"
              onClick={() => router.push('/generate?type=video')}
            >
              <Video className="w-6 h-6 mb-2 text-red-400" />
              <span>New Video</span>
            </Button>
            <Button 
              variant="outline" 
              className="h-24 flex flex-col items-center justify-center border-slate-800 bg-slate-800/30 hover:bg-slate-800/50"
              onClick={() => router.push('/generate?type=image')}
            >
              <ImageIcon className="w-6 h-6 mb-2 text-blue-400" />
              <span>New Image</span>
            </Button>
            <Button 
              variant="outline" 
              className="h-24 flex flex-col items-center justify-center border-slate-800 bg-slate-800/30 hover:bg-slate-800/50"
              onClick={() => router.push('/generate?type=audio')}
            >
              <Music className="w-6 h-6 mb-2 text-purple-400" />
              <span>New Audio</span>
            </Button>
            <Button 
              variant="outline" 
              className="h-24 flex flex-col items-center justify-center border-slate-800 bg-slate-800/30 hover:bg-slate-800/50"
              onClick={() => router.push('/templates')}
            >
              <FileText className="w-6 h-6 mb-2 text-green-400" />
              <span>From Template</span>
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
