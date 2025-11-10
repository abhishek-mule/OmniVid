'use client';

import { useEffect, useState } from 'react';
import { GoogleReCaptchaProvider } from 'react-google-recaptcha-v3';

export const ReCaptchaProvider = ({ children }: { children: React.ReactNode }) => {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return <>{children}</>;
  }

  return (
    <GoogleReCaptchaProvider reCaptchaKey={process.env.NEXT_PUBLIC_RECAPTCHA_SITE_KEY || ''}>
      {children}
    </GoogleReCaptchaProvider>
  );
};

export const useReCaptcha = () => {
  const [recaptcha, setRecaptcha] = useState<any>(null);

  useEffect(() => {
    const loadReCaptcha = async () => {
      const { GoogleReCaptcha } = await import('react-google-recaptcha-v3');
      setRecaptcha(GoogleReCaptcha);
    };
    
    loadReCaptcha();
  }, []);

  return recaptcha;
};
