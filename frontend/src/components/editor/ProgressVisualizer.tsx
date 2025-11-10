'use client';

import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Check, Sparkles, Brain, Paintbrush, Film, Zap, Clock } from 'lucide-react';
import { cn } from '@/lib/utils';

type GenerationStage = 'idle' | 'parsing' | 'generating' | 'rendering' | 'effects' | 'finalizing' | 'complete';

interface ProgressVisualizerProps {
  progress: number;
  currentStage: GenerationStage;
  className?: string;
  showTimeEstimate?: boolean;
}

const STAGES = [
  { id: 'parsing', label: 'Parsing prompt', icon: Brain, range: [0, 15] },
  { id: 'generating', label: 'Generating assets', icon: Sparkles, range: [15, 45] },
  { id: 'rendering', label: 'Rendering video', icon: Film, range: [45, 80] },
  { id: 'effects', label: 'Applying effects', icon: Paintbrush, range: [80, 95] },
  { id: 'finalizing', label: 'Finalizing', icon: Zap, range: [95, 100] },
];

export function ProgressVisualizer({
  progress = 0,
  currentStage = 'idle',
  className,
  showTimeEstimate = true,
}: ProgressVisualizerProps) {
  const [timeRemaining, setTimeRemaining] = useState<string>('');
  const [isComplete, setIsComplete] = useState(false);
  const radius = 80;
  const circumference = 2 * Math.PI * radius;
  const progressOffset = circumference - (progress / 100) * circumference;

  // Calculate time remaining based on progress
  useEffect(() => {
    if (!showTimeEstimate) return;
    
    let timeLeft = '';
    if (progress < 10) {
      timeLeft = '2-3 minutes';
    } else if (progress < 30) {
      timeLeft = '1-2 minutes';
    } else if (progress < 70) {
      timeLeft = '30-60 seconds';
    } else if (progress < 95) {
      timeLeft = '10-30 seconds';
    } else if (progress < 100) {
      timeLeft = 'Almost done...';
    } else {
      timeLeft = 'Complete!';
    }
    
    setTimeRemaining(timeLeft);
  }, [progress, showTimeEstimate]);

  // Handle completion state
  useEffect(() => {
    if (progress >= 100 && !isComplete) {
      const timer = setTimeout(() => {
        setIsComplete(true);
      }, 500);
      return () => clearTimeout(timer);
    } else if (progress < 100) {
      setIsComplete(false);
    }
  }, [progress, isComplete]);

  const getStageProgress = (stageId: string) => {
    const stage = STAGES.find(s => s.id === stageId);
    if (!stage) return 0;
    
    if (progress >= stage.range[1]) return 100;
    if (progress <= stage.range[0]) return 0;
    
    const stageProgress = ((progress - stage.range[0]) / (stage.range[1] - stage.range[0])) * 100;
    return Math.min(100, Math.max(0, stageProgress));
  };

  const isStageComplete = (stageId: string) => {
    const stage = STAGES.find(s => s.id === stageId);
    return stage ? progress >= stage.range[1] : false;
  };

  const isCurrentStage = (stageId: string) => {
    return currentStage === stageId && progress < 100;
  };

  return (
    <div className={cn("w-full max-w-md mx-auto", className)}>
      {/* Animated Progress Circle */}
      <div className="relative w-48 h-48 mx-auto mb-8">
        <svg className="w-full h-full" viewBox="0 0 200 200">
          {/* Background circle */}
          <circle
            cx="100"
            cy="100"
            r={radius}
            className="text-gray-100"
            strokeWidth="10"
            stroke="currentColor"
            fill="none"
          />
          
          {/* Progress circle */}
          <motion.circle
            cx="100"
            cy="100"
            r={radius}
            className="text-blue-500"
            strokeWidth="10"
            strokeLinecap="round"
            stroke="currentColor"
            fill="none"
            strokeDasharray={circumference}
            strokeDashoffset={progressOffset}
            initial={{ pathLength: 0 }}
            animate={{ pathLength: progress / 100 }}
            transition={{
              duration: 0.8,
              ease: [0.16, 0.77, 0.47, 0.97],
            }}
            transform="rotate(-90 100 100)"
          />
        </svg>
        
        {/* Percentage text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <AnimatePresence mode="wait">
            <motion.div
              key={`percentage-${progress}`}
              initial={{ opacity: 0, y: 5 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -5 }}
              transition={{ duration: 0.3 }}
              className="text-center"
            >
              <div className="text-3xl font-bold text-gray-900">
                {Math.round(progress)}%
              </div>
              {timeRemaining && (
                <div className="text-sm text-gray-500 flex items-center justify-center mt-1">
                  <Clock className="w-3.5 h-3.5 mr-1" />
                  {timeRemaining}
                </div>
              )}
            </motion.div>
          </AnimatePresence>
        </div>
        
        {/* Completion checkmark */}
        <AnimatePresence>
          {isComplete && (
            <motion.div
              className="absolute inset-0 flex items-center justify-center"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.2, type: 'spring' }}
            >
              <div className="w-16 h-16 rounded-full bg-green-100 flex items-center justify-center text-green-500">
                <Check className="w-8 h-8" />
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Stage Timeline */}
      <div className="space-y-4">
        {STAGES.map((stage) => {
          const stageProgress = getStageProgress(stage.id);
          const complete = isStageComplete(stage.id);
          const current = isCurrentStage(stage.id);
          const Icon = stage.icon;
          
          return (
            <div key={stage.id} className="flex items-start">
              <div className="flex flex-col items-center mr-3">
                <div className={cn(
                  "w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 relative z-10",
                  complete 
                    ? "bg-green-100 text-green-600" 
                    : current 
                      ? "bg-blue-100 text-blue-600" 
                      : "bg-gray-100 text-gray-400"
                )}>
                  {complete ? (
                    <Check className="w-4 h-4" />
                  ) : (
                    <Icon className={cn("w-4 h-4", current && "animate-pulse")} />
                  )}
                </div>
                {stage.id !== STAGES[STAGES.length - 1].id && (
                  <div className={cn(
                    "w-0.5 h-8 my-1",
                    complete ? "bg-green-100" : "bg-gray-100"
                  )} />
                )}
              </div>
              
              <div className="flex-1 pt-1">
                <div className="flex justify-between items-baseline">
                  <span className={cn(
                    "text-sm font-medium",
                    complete ? "text-green-700" : current ? "text-blue-700" : "text-gray-500"
                  )}>
                    {stage.label}
                  </span>
                  <span className="text-xs text-gray-400">
                    {complete ? 'Complete' : current ? 'In progress...' : ''}
                  </span>
                </div>
                
                {!complete && (
                  <div className="mt-1 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                    <motion.div
                      className={cn(
                        "h-full rounded-full",
                        current ? "bg-blue-500" : "bg-gray-300"
                      )}
                      initial={{ width: 0 }}
                      animate={{ width: `${stageProgress}%` }}
                      transition={{ duration: 0.5, ease: 'easeOut' }}
                    />
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
