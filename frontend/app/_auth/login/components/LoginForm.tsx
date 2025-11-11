'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import styles from '../login.module.css';

const LoginForm = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      const formData = new FormData();
      formData.append('email', email);
      formData.append('password', password);

      const response = await fetch('/api/login', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Login failed');
      }

      // Redirect to dashboard on successful login
      router.push('/dashboard');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred during login');
    } finally {
      setIsLoading(false);
    }
  };

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  return (
    <div className={styles.authPanel}>
      {/* Left Panel - Social Login */}
      <div className={styles.authPanelLeft}>
        <div className={styles.brandLogo}>
          <img 
            src="/images/logo.png" 
            width="150" 
            alt="brand-logo" 
            onError={(e) => {
              const target = e.target as HTMLImageElement;
              target.src = 'https://via.placeholder.com/150x50?text=Logo';
            }}
          />
        </div>
        <p className={styles.socialLoginText}>Login using social media to get quick access</p>
        
        <div className={styles.socialButtons}>
          <a href="/api/auth/signin/facebook" className={`${styles.socialButton} ${styles.facebookButton}`}>
            <i className="fa fa-facebook" aria-hidden="true"></i>
            <span>Sign in with Facebook</span>
          </a>
          
          <a href="/api/auth/signin/twitter" className={`${styles.socialButton} ${styles.twitterButton}`}>
            <i className="fa fa-twitter" aria-hidden="true"></i>
            <span>Sign in with Twitter</span>
          </a>
          
          <a href="/api/auth/signin/google" className={`${styles.socialButton} ${styles.googleButton}`}>
            <i className="fa fa-google" aria-hidden="true"></i>
            <span>Sign in with Google</span>
          </a>
        </div>
      </div>
      
      {/* Right Panel - Login Form */}
      <div className={styles.authPanelRight}>
        <div className={styles.authHeader}>
          <h1 className={styles.authTitle}>Login to your account</h1>
          <p className={styles.authSubtitle}>
            Don&apos;t have an account?{' '}
            <Link href="/signup" className={styles.authLink}>
              Sign Up Free!
            </Link>
          </p>
        </div>
        
        <form onSubmit={handleSubmit} className={styles.loginForm}>
          {error && (
            <div role="alert" className={styles.errorMessage}>
              {error}
            </div>
          )}
          
          <div className={styles.formGroup}>
            <label htmlFor="email" className="sr-only">Email</label>
            <input
              id="email"
              type="email"
              className={styles.formControl}
              placeholder="Email address"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              aria-required="true"
              autoComplete="username"
            />
          </div>
          
          <div className={styles.formGroup}>
            <label htmlFor="password" className="sr-only">Password</label>
            <div className={styles.passwordWrapper}>
              <input
                id="password"
                type={showPassword ? 'text' : 'password'}
                className={styles.formControl}
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                aria-required="true"
                autoComplete="current-password"
              />
              <button
                type="button"
                className={styles.togglePassword}
                onClick={togglePasswordVisibility}
                aria-label={showPassword ? 'Hide password' : 'Show password'}
                tabIndex={-1}
              >
                <i 
                  className={`fa ${showPassword ? 'fa-eye' : 'fa-eye-slash'}`}
                  aria-hidden="true"
                ></i>
              </button>
            </div>
          </div>
          
          <div className={styles.rememberRow}>
            <label className={styles.checkboxLabel}>
              <input
                type="checkbox"
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
                aria-label="Remember me"
              />
              <span>Remember me</span>
            </label>
            
            <Link href="/forgot-password" className={styles.forgotPassword}>
              Forgot password?
            </Link>
          </div>
          
          <button
            type="submit"
            className={styles.submitButton}
            disabled={isLoading}
            aria-busy={isLoading}
          >
            {isLoading ? 'Logging in...' : 'Login with email'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default LoginForm;
