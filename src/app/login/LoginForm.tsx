'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import styles from './login.module.css';

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
            src="https://1.bp.blogspot.com/-3he0CGCSWHA/XyqopZcixRI/AAAAAAAAVM8/Mdfk_mPQa0Ydb7IAH0Iir8F4Ge7xxF0ygCLcBGAsYHQ/s0/logo.png" 
            width="150" 
            alt="brand-logo" 
          />
        </div>
        <p className={styles.socialLoginText}>Login using social media to get quick access</p>
        
        <div className={styles.socialButtons}>
          <a href="#" className={`${styles.socialButton} ${styles.facebookButton}`}>
            <i className="fa fa-facebook"></i>
            <span>Sign in with Facebook</span>
          </a>
          
          <a href="#" className={`${styles.socialButton} ${styles.twitterButton}`}>
            <i className="fa fa-twitter"></i>
            <span>Sign in with Twitter</span>
          </a>
          
          <a href="#" className={`${styles.socialButton} ${styles.googleButton}`}>
            <i className="fa fa-google"></i>
            <span>Sign in with Google</span>
          </a>
        </div>
      </div>
      
      {/* Right Panel - Login Form */}
      <div className={styles.authPanelRight}>
        <div className={styles.authHeader}>
          <h2 className={styles.authTitle}>Login to your account</h2>
          <p className={styles.authSubtitle}>
            Don't have an account?{' '}
            <Link href="/signup" className={styles.authLink}>
              Sign Up Free!
            </Link>
          </p>
        </div>
        
        <form onSubmit={handleSubmit} className={styles.loginForm}>
          {error && <div className={styles.errorMessage}>{error}</div>}
          
          <div className={styles.formGroup}>
            <input
              type="email"
              className={styles.formControl}
              placeholder="Email address"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          
          <div className={styles.formGroup}>
            <div className={styles.passwordWrapper}>
              <input
                type={showPassword ? 'text' : 'password'}
                className={styles.formControl}
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
              <button
                type="button"
                className={styles.togglePassword}
                onClick={togglePasswordVisibility}
                tabIndex={-1}
              >
                <i className={`fa ${showPassword ? 'fa-eye' : 'fa-eye-slash'}`}></i>
              </button>
            </div>
          </div>
          
          <div className={styles.rememberRow}>
            <label className={styles.checkboxLabel}>
              <input
                type="checkbox"
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
              />
              <span>Remember me</span>
            </label>
            
            <a href="#" className={styles.forgotPassword}>
              Forgot password?
            </a>
          </div>
          
          <button
            type="submit"
            className={styles.submitButton}
            disabled={isLoading}
          >
            {isLoading ? 'Logging in...' : 'Login with email'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default LoginForm;
