import { ThemeProvider } from '@/components/home/theme-provider';
import { siteConfig } from '@/lib/site';
import type { Metadata, Viewport } from 'next';
import { Geist, Geist_Mono } from 'next/font/google';
import './globals.css';
import { Providers } from './providers';
import { Toaster } from '@/components/ui/sonner';
import Script from 'next/script';
<<<<<<< HEAD
import React from 'react';
=======
import { PostHogIdentify } from '@/components/posthog-identify';
import '@/lib/polyfills'; // Load polyfills early
>>>>>>> 573e711f397489d19d556d9f0b21f4393f363dfc

const geistSans = Geist({
  variable: '--font-geist-sans',
  subsets: ['latin'],
});

const geistMono = Geist_Mono({
  variable: '--font-geist-mono',
  subsets: ['latin'],
});

export const viewport: Viewport = {
  themeColor: 'black',
};

export const metadata: Metadata = {
  metadataBase: new URL(siteConfig.url),
  title: {
    default: siteConfig.name,
    template: `%s - ${siteConfig.name}`,
  },
  description:
    'Kortix is a fully open source AI assistant that helps you accomplish real-world tasks with ease. Through natural conversation, Kortix becomes your digital companion for research, data analysis, and everyday challenges.',
  keywords: [
    'AI',
    'artificial intelligence',
    'browser automation',
    'web scraping',
    'file management',
    'AI assistant',
    'open source',
    'research',
    'data analysis',
  ],
  authors: [{ name: 'Kortix Team', url: 'https://suna.so' }],
  creator:
    'Kortix Team',
  publisher:
    'Kortix Team',
  category: 'Technology',
  applicationName: 'Suna',
  formatDetection: {
    telephone: false,
    email: false,
    address: false,
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
    },
  },
  openGraph: {
    title: 'Suna - Open Source Generalist AI Worker',
    description:
      'Suna is a fully open source AI assistant that helps you accomplish real-world tasks with ease through natural conversation.',
    url: siteConfig.url,
    siteName: 'Suna',
    images: [
      {
        url: '/banner.png',
        width: 1200,
        height: 630,
        alt: 'Suna - Open Source Generalist AI Worker',
        type: 'image/png',
      },
    ],
    locale: 'en_US',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Suna - Open Source Generalist AI Worker',
    description:
      'Suna is a fully open source AI assistant that helps you accomplish real-world tasks with ease through natural conversation.',
    creator: '@kortixai',
    site: '@kortixai',
    images: [
      {
        url: '/banner.png',
        width: 1200,
        height: 630,
        alt: 'Suna - Open Source Generalist AI Worker',
      },
    ],
  },
  icons: {
    icon: [{ url: '/favicon.png', sizes: 'any' }],
    shortcut: '/favicon.png',
  },
  // manifest: "/manifest.json",
  alternates: {
    canonical: siteConfig.url,
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const isProduction = process.env.NODE_ENV === 'production';
  
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        {/* Google Tag Manager - Only in production */}
        {isProduction && (
          <Script id="google-tag-manager" strategy="afterInteractive">
            {`(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
            new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
            j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
            'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
            })(window,document,'script','dataLayer','GTM-PCHSN4M2');`}
          </Script>
        )}
        {isProduction && (
          <Script async src="https://cdn.tolt.io/tolt.js" data-tolt={process.env.NEXT_PUBLIC_TOLT_REFERRAL_ID}></Script>
        )}
      </head>

      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased font-sans bg-background`}
      >
        {isProduction && (
          <noscript>
            <iframe
              src="https://www.googletagmanager.com/ns.html?id=GTM-PCHSN4M2"
              height="0"
              width="0"
              style={{ display: 'none', visibility: 'hidden' }}
            />
          </noscript>
        )}
        {/* End Google Tag Manager (noscript) */}

        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <Providers>
            {children}
            <Toaster />
          </Providers>
<<<<<<< HEAD
          {/* Analytics components - Only in production */}
          {isProduction && <ProductionAnalytics />}
=======
          <Analytics />
          <GoogleAnalytics gaId="G-6ETJFB3PT3" />
          <SpeedInsights />
          <PostHogIdentify />
>>>>>>> 573e711f397489d19d556d9f0b21f4393f363dfc
        </ThemeProvider>
      </body>
    </html>
  );
}

// Production analytics component - only loads in production
function ProductionAnalytics() {
  // This component will be empty in development, preventing any analytics loading
  return null;
}
