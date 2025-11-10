'use client';

import { motion } from 'framer-motion';
import { FileText, Film, Package, CheckCircle2, Clock } from 'lucide-react';

interface ProgressVisualizationProps {
  progress: number;
  currentStage: string;
}

const stages = [
  {
    name: 'Parsing',
    icon: FileText,
    description: 'Analyzing your prompt',
    color: 'text-blue-500',
    bgColor: 'bg-blue-500/10'
  },
  {
    name: 'Rendering',
    icon: Film,
    description: 'Creating video frames',
    color: 'text-purple-500',
    bgColor: 'bg-purple-500/10'
  },
  {
    name: 'Encoding',
    icon: Package,
    description: 'Compressing video',
    color: 'text-orange-500',
    bgColor: 'bg-orange-500/10'
  },
  {
    name: 'Finalizing',
    icon: CheckCircle2,
    description: 'Preparing download',
    color: 'text-green-500',
    bgColor: 'bg-green-500/10'
  }
];

export default function ProgressVisualization({ progress, currentStage }: ProgressVisualizationProps) {
  const currentStageIndex = stages.findIndex(s => s.name === currentStage);
  const estimatedTimeRemaining = Math.ceil((100 - progress) / 10);

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="rounded-2xl border border-border bg-card p-6 sticky top-24"
    >
      <h2 className="text-xl font-semibold mb-6 text-center">
        Generating Video
      </h2>

      {/* Circular Progress */}
      <div className="relative w-48 h-48 mx-auto mb-8">
        {/* Background circle */}
        <svg className="w-full h-full transform -rotate-90">
          <circle
            cx="96"
            cy="96"
            r="88"
            stroke="currentColor"
            strokeWidth="8"
            fill="none"
            className="text-muted"
          />
          {/* Progress circle */}
          <motion.circle
            cx="96"
            cy="96"
            r="88"
            stroke="currentColor"
            strokeWidth="8"
            fill="none"
            strokeLinecap="round"
            className="text-primary"
            initial={{ strokeDasharray: "0 552" }}
            animate={{ strokeDasharray: `${(progress / 100) * 552} 552` }}
            transition={{ duration: 0.5, ease: "easeInOut" }}
          />
        </svg>

        {/* Center content */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <motion.div
            key={progress}
            initial={{ scale: 1.2, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="text-4xl font-bold text-primary"
          >
            {progress}%
          </motion.div>
          <div className="text-sm text-muted-foreground mt-1">
            {currentStage}
          </div>
        </div>

        {/* Animated ring */}
        <motion.div
          className="absolute inset-0 rounded-full border-2 border-primary/20"
          animate={{
            scale: [1, 1.1, 1],
            opacity: [0.5, 0.2, 0.5]
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
      </div>

      {/* Stage Breakdown */}
      <div className="space-y-3 mb-6">
        {stages.map((stage, index) => {
          const isActive = stage.name === currentStage;
          const isCompleted = index < currentStageIndex;
          const Icon = stage.icon;

          return (
            <motion.div
              key={stage.name}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className={`flex items-center gap-3 p-3 rounded-lg border transition-all ${
                isActive
                  ? `${stage.bgColor} border-current ${stage.color}`
                  : isCompleted
                  ? 'bg-green-500/10 border-green-500/50 text-green-500'
                  : 'bg-muted/30 border-border text-muted-foreground'
              }`}
            >
              {/* Icon */}
              <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                isActive ? stage.bgColor : isCompleted ? 'bg-green-500/20' : 'bg-muted'
              }`}>
                {isCompleted ? (
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ type: "spring", stiffness: 200 }}
                  >
                    <CheckCircle2 className="w-5 h-5 text-green-500" />
                  </motion.div>
                ) : (
                  <Icon className={`w-5 h-5 ${isActive ? stage.color : 'text-muted-foreground'}`} />
                )}
              </div>

              {/* Content */}
              <div className="flex-1">
                <div className="font-medium text-sm">{stage.name}</div>
                <div className="text-xs opacity-70">{stage.description}</div>
              </div>

              {/* Status indicator */}
              {isActive && (
                <motion.div
                  className={`w-2 h-2 rounded-full ${stage.color.replace('text-', 'bg-')}`}
                  animate={{
                    scale: [1, 1.5, 1],
                    opacity: [1, 0.5, 1]
                  }}
                  transition={{
                    duration: 1.5,
                    repeat: Infinity,
                    ease: "easeInOut"
                  }}
                />
              )}
            </motion.div>
          );
        })}
      </div>

      {/* ETA */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
        className="flex items-center justify-between p-4 rounded-lg bg-primary/5 border border-primary/20"
      >
        <div className="flex items-center gap-2">
          <Clock className="w-4 h-4 text-primary" />
          <span className="text-sm font-medium">Estimated time remaining</span>
        </div>
        <motion.span
          key={estimatedTimeRemaining}
          initial={{ scale: 1.2 }}
          animate={{ scale: 1 }}
          className="text-sm font-bold text-primary"
        >
          ~{estimatedTimeRemaining} min
        </motion.span>
      </motion.div>

      {/* Processing message */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.6 }}
        className="mt-4 text-center text-xs text-muted-foreground"
      >
        <motion.span
          animate={{ opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 2, repeat: Infinity }}
        >
          Please don't close this window...
        </motion.span>
      </motion.div>
    </motion.div>
  );
}
