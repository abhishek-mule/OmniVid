'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  BarChart3,
  Video,
  Clock,
  TrendingUp,
  Users,
  Play,
  Edit,
  Download,
  Star,
  Activity
} from "lucide-react";

const stats = [
  { title: 'Total Videos', value: '24', icon: Video, change: '+12%' },
  { title: 'Watch Time', value: '2.4h', icon: Clock, change: '+8%' },
  { title: 'Projects', value: '8', icon: Edit, change: '+3' },
  { title: 'Storage Used', value: '2.1GB', icon: BarChart3, change: '+15%' }
];

const recentVideos = [
  { title: 'Product Demo', duration: '1:30', status: 'completed', views: 124 },
  { title: 'Tutorial Video', duration: '3:45', status: 'processing', views: 0 },
  { title: 'Marketing Clip', duration: '0:45', status: 'completed', views: 89 },
  { title: 'Social Media Post', duration: '0:15', status: 'draft', views: 0 }
];

export default function DashboardPage() {
  return (
    <div className="min-h-screen gradient-bg">
      <div className="container py-10">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="mb-8 animate-fade-in">
            <h1 className="text-4xl font-bold mb-2 text-gradient">Dashboard</h1>
            <p className="text-muted-foreground">Welcome back! Here's your video creation overview.</p>
          </div>

          {/* Stats Grid */}
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4 mb-8">
            {stats.map((stat, index) => (
              <Card key={stat.title} className="glass-card animate-fade-in" style={{ animationDelay: `${index * 100}ms` }}>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">{stat.title}</p>
                      <p className="text-3xl font-bold text-gradient">{stat.value}</p>
                    </div>
                    <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center">
                      <stat.icon className="w-6 h-6 text-white" />
                    </div>
                  </div>
                  <div className="mt-4 flex items-center text-sm">
                    <TrendingUp className="w-4 h-4 text-emerald-500 mr-1" />
                    <span className="text-emerald-500">{stat.change}</span>
                    <span className="text-muted-foreground ml-1">from last month</span>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          <div className="grid gap-8 lg:grid-cols-3">
            {/* Recent Videos */}
            <Card className="glass-card lg:col-span-2">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Video className="w-5 h-5" />
                  Recent Videos
                </CardTitle>
                <CardDescription>Your latest video projects</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {recentVideos.map((video, index) => (
                    <div key={index} className="flex items-center justify-between p-4 glass rounded-lg hover:scale-102 transition-transform cursor-pointer">
                      <div className="flex items-center gap-4">
                        <div className="w-16 h-10 bg-muted rounded flex items-center justify-center">
                          <Play className="w-4 h-4 text-muted-foreground" />
                        </div>
                        <div>
                          <h3 className="font-medium">{video.title}</h3>
                          <p className="text-sm text-muted-foreground">{video.duration}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-4">
                        <Badge variant={
                          video.status === 'completed' ? 'default' :
                          video.status === 'processing' ? 'secondary' : 'outline'
                        }>
                          {video.status}
                        </Badge>
                        {video.views > 0 && (
                          <span className="text-sm text-muted-foreground">{video.views} views</span>
                        )}
                        <Button variant="ghost" size="sm">
                          <Edit className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="mt-6">
                  <Button className="w-full gradient-primary text-white">
                    Create New Video
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Activity & Quick Actions */}
            <div className="space-y-6">
              <Card className="glass-card">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Activity className="w-5 h-5" />
                    Quick Actions
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <Button className="w-full justify-start glass-hover" variant="outline">
                    <Video className="w-4 h-4 mr-2" />
                    Generate Video
                  </Button>
                  <Button className="w-full justify-start glass-hover" variant="outline">
                    <Edit className="w-4 h-4 mr-2" />
                    Open Editor
                  </Button>
                  <Button className="w-full justify-start glass-hover" variant="outline">
                    <Download className="w-4 h-4 mr-2" />
                    Export Project
                  </Button>
                </CardContent>
              </Card>

              <Card className="glass-card">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Star className="w-5 h-5" />
                    Usage This Month
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>Videos Generated</span>
                        <span>18/50</span>
                      </div>
                      <div className="w-full bg-muted rounded-full h-2">
                        <div className="bg-gradient-to-r from-emerald-500 to-teal-500 h-2 rounded-full" style={{ width: '36%' }}></div>
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>Storage Used</span>
                        <span>2.1GB/10GB</span>
                      </div>
                      <div className="w-full bg-muted rounded-full h-2">
                        <div className="bg-gradient-to-r from-blue-500 to-cyan-500 h-2 rounded-full" style={{ width: '21%' }}></div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}