'use client';

import { useState } from 'react';
import { createClient } from '@/lib/supabase/client';
import { toast } from 'sonner';
import { FcGoogle } from "react-icons/fc";
import { Loader2 } from 'lucide-react';

interface GoogleSignInProps {
  returnUrl?: string;
}

export default function GoogleSignIn({ returnUrl }: GoogleSignInProps) {
  const [isLoading, setIsLoading] = useState(false);
  const supabase = createClient();

<<<<<<< HEAD
  const handleGoogleSignIn = useCallback(
    async (response: GoogleSignInResponse) => {
      try {
        setIsLoading(true);
        const supabase = createClient();

        console.log('Starting Google sign in process');

        const { error } = await supabase.auth.signInWithIdToken({
          provider: 'google',
          token: response.credential,
        });

        if (error) throw error;

        console.log(
          'Google sign in successful, waiting for session...',
        );

        // Poll for session
        const checkSession = async () => {
          const { data: { session } } = await supabase.auth.getSession();
          return session;
        };

        let session = await checkSession();
        let attempts = 0;
        const maxAttempts = 10;

        while (!session && attempts < maxAttempts) {
          await new Promise(resolve => setTimeout(resolve, 500));
          session = await checkSession();
          attempts++;
        }

        if (!session) {
          throw new Error('Session not established after sign-in');
        }

        console.log('Session established, redirecting to:', returnUrl || '/dashboard');
        window.location.href = returnUrl || '/dashboard';
      } catch (error) {
        console.error('Error signing in with Google:', error);
        setIsLoading(false);
      }
    },
    [returnUrl],
  );

  useEffect(() => {
    // Assign the callback to window object so it can be called from the Google button
    window.handleGoogleSignIn = handleGoogleSignIn;

    if (window.google && googleClientId) {
      window.google.accounts.id.initialize({
        client_id: googleClientId,
        callback: handleGoogleSignIn,
        use_fedcm: true,
        context: 'signin',
        itp_support: true,
=======
  const handleGoogleSignIn = async () => {
    try {
      setIsLoading(true);
      const { error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: `${window.location.origin}/auth/callback${
            returnUrl ? `?returnUrl=${encodeURIComponent(returnUrl)}` : ''
          }`,
        },
>>>>>>> 573e711f397489d19d556d9f0b21f4393f363dfc
      });

      if (error) {
        throw error;
      }
    } catch (error: any) {
      console.error('Google sign-in error:', error);
      toast.error(error.message || 'Failed to sign in with Google');
      setIsLoading(false);
    }
  };

  return (
    <button
      onClick={handleGoogleSignIn}
      disabled={isLoading}
      className="w-full h-12 flex items-center justify-center text-sm font-medium tracking-wide rounded-full bg-background text-foreground border border-border hover:bg-accent/30 transition-all duration-200 disabled:opacity-60 disabled:cursor-not-allowed font-sans"
      type="button"
    >
      {isLoading ? (
        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
      ) : (
        <FcGoogle className="w-4 h-4 mr-2" />
      )}
      <span className="font-medium">
        {isLoading ? 'Signing in...' : 'Continue with Google'}
      </span>
    </button>
  );
}