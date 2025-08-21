<<<<<<< HEAD
export default function HomePage() {
  return (
    <main className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center space-y-8">
          <h1 className="text-4xl md:text-6xl font-bold text-foreground">
            Welcome to Suna AI
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            The Generalist AI Agent that can act on your behalf.
          </p>
          <div className="flex justify-center gap-4">
            <a 
              href="/dashboard" 
              className="bg-primary text-primary-foreground px-6 py-3 rounded-lg hover:bg-primary/90 transition-colors"
            >
              Get Started
            </a>
            <a 
              href="https://github.com/kortix-ai/suna" 
              className="border border-border px-6 py-3 rounded-lg hover:bg-accent transition-colors"
            >
              View on GitHub
            </a>
          </div>
        </div>
      </div>
    </main>
=======
'use client';

import { useEffect, useState } from 'react';
import { CTASection } from '@/components/home/sections/cta-section';
// import { FAQSection } from "@/components/sections/faq-section";
import { FooterSection } from '@/components/home/sections/footer-section';
import { HeroSection } from '@/components/home/sections/hero-section';
import { OpenSourceSection } from '@/components/home/sections/open-source-section';
import { PricingSection } from '@/components/home/sections/pricing-section';
import { UseCasesSection } from '@/components/home/sections/use-cases-section';
import { ModalProviders } from '@/providers/modal-providers';
import { HeroVideoSection } from '@/components/home/sections/hero-video-section';
import { BackgroundAALChecker } from '@/components/auth/background-aal-checker';
import { BentoSection } from '@/components/home/sections/bento-section';
import { CompanyShowcase } from '@/components/home/sections/company-showcase';
import { FeatureSection } from '@/components/home/sections/feature-section';
import { QuoteSection } from '@/components/home/sections/quote-section';
import { TestimonialSection } from '@/components/home/sections/testimonial-section';
import { FAQSection } from '@/components/home/sections/faq-section';
import { AgentShowcaseSection } from '@/components/home/sections/agent-showcase-section';

export default function Home() {
  return (
    <>
      <ModalProviders />
      <BackgroundAALChecker>
        <main className="flex flex-col items-center justify-center min-h-screen w-full">
          <div className="w-full divide-y divide-border">
            <HeroSection />
            <BentoSection />
            {/* <AgentShowcaseSection /> */}
            <OpenSourceSection />
            <PricingSection />
            {/* <TestimonialSection /> */}
            {/* <FAQSection /> */}
            <CTASection />
            <FooterSection />
          </div>
        </main>
      </BackgroundAALChecker>
    </>
>>>>>>> 573e711f397489d19d556d9f0b21f4393f363dfc
  );
}