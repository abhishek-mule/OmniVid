import { Suspense } from 'react';
import dynamic from 'next/dynamic';
import { Inter } from 'next/font/google';
import Loading from './loading';
import ErrorBoundary from '@/components/ErrorBoundary';
import styles from './login.module.css';

// Lazy load the LoginForm component
const LoginForm = dynamic(() => import('./components/LoginForm'), { 
  ssr: false,
  loading: () => <div>Loading form...</div> 
});

const inter = Inter({ subsets: ['latin'] });

export default function LoginPage() {
  return (
    <div className={`${styles.body} ${inter.className}`}>
      <ErrorBoundary fallback={<div>Failed to load login form</div>}>
        <Suspense fallback={<Loading />}>
          <div className={styles.authContainer}>
            <LoginForm />
          </div>
          
          {/* Background Animations */}
          <BackgroundAnimations />
        </Suspense>
      </ErrorBoundary>
    </div>
  );
}

// BackgroundAnimations component moved to a separate client component
function BackgroundAnimations() {
  return (
    <>
      <div className={styles.dustParticle}>
        <svg 
          width="100%" 
          height="100%" 
          viewBox="0 0 885 455" 
          preserveAspectRatio="xMidYMid meet"
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            zIndex: 1,
            pointerEvents: 'none',
            opacity: 0.8
          }}
        >
          {typeof window !== 'undefined' && generateDustParticles(30)}
        </svg>
      </div>

      <div className={styles.snell}>
        <svg 
          width="300" 
          height="400" 
          viewBox="0 0 400 400" 
          style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            zIndex: 2,
            opacity: 0.3,
            pointerEvents: 'none',
            animation: 'float 15s ease-in-out infinite',
            filter: 'blur(1px)'
          }}
        >
          <path 
            d="M100,50 C150,150 50,250 100,350 C150,450 250,450 300,350 C350,250 250,150 300,50 C350,-50 50,-50 100,50 Z" 
            fill="#4f77ff" 
            fillOpacity="0.1"
            style={{
              animation: 'pulse 8s ease-in-out infinite'
            }}
          />
        </svg>
      </div>
    </>
  );
}

// Utility function for generating dust particles
function generateDustParticles(count: number) {
  const particles = [];
  const viewBoxWidth = 885;
  const viewBoxHeight = 455;
  
  for (let i = 0; i < count; i++) {
    const cx = Math.random() * viewBoxWidth;
    const cy = Math.random() * viewBoxHeight;
    const size = 2 + Math.random() * 4;
    const opacity = 0.3 + Math.random() * 0.7;
    const delay = Math.random() * 5;
    const duration = 3 + Math.random() * 4;
    
    particles.push(
      <circle 
        key={`dust-${i}`}
        cx={cx}
        cy={cy}
        r={size / 2}
        fill="#F4CD39"
        fillOpacity={opacity}
        style={{
          animation: `float ${duration}s ease-in-out ${delay}s infinite`,
          transformOrigin: 'center center'
        }}
      />
    );
  }
  
  return particles;
}
