'use client';

import { useEffect, useRef, useState } from 'react';
import dynamic from 'next/dynamic';
import Head from 'next/head';
import styles from './login.module.css';

// Import the LoginForm component with no SSR to avoid hydration issues
const LoginForm = dynamic(() => import('./LoginForm'), { ssr: false });

// Generate random dust particles
const generateDustParticles = (count: number) => {
  const particles = [];
  const viewBoxWidth = 885;
  const viewBoxHeight = 455;
  
  for (let i = 0; i < count; i++) {
    const cx = Math.random() * viewBoxWidth;
    const cy = Math.random() * viewBoxHeight;
    const size = 2 + Math.random() * 4; // Random size between 2 and 6
    const opacity = 0.3 + Math.random() * 0.7; // Random opacity between 0.3 and 1
    const delay = Math.random() * 5; // Random animation delay up to 5s
    const duration = 3 + Math.random() * 4; // Random duration between 3-7s
    
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
};

export default function LoginPage() {
  const dustParticleRef = useRef<HTMLDivElement>(null);
  const snellRef = useRef<HTMLDivElement>(null);
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  // Generate snell SVG path
  const snellPath = (
    <path 
      d="M100,50 C150,150 50,250 100,350 C150,450 250,450 300,350 C350,250 250,150 300,50 C350,-50 50,-50 100,50 Z" 
      fill="#4f77ff" 
      fillOpacity="0.1"
      style={{
        animation: 'pulse 8s ease-in-out infinite'
      }}
    />
  );

  return (
    <div className={styles.body}>
      <Head>
        <link 
          rel="stylesheet" 
          href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css" 
          integrity="sha512-Fo3rlrZj/k7ujTnHg4CGR2D7kSs0v4LLanw2qksYuRlEzO+tcaEPQogQ0KaoGN26/zrn20ImR1DfuLWnOo7aBA==" 
          crossOrigin="anonymous" 
          referrerPolicy="no-referrer" 
        />
      </Head>

      {/* Dust Particles Animation */}
      <div ref={dustParticleRef} className={styles.dustParticle}>
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
          {isMounted && generateDustParticles(30)}
        </svg>
      </div>

      {/* Snell Animation */}
      <div ref={snellRef} className={styles.snell}>
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
          {snellPath}
        </svg>
      </div>

      {/* Login Form */}
      <div className={styles.authContainer}>
        <LoginForm />
      </div>

    </div>
  );
}