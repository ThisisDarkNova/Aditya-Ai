import type { Metadata } from 'next';
import { Inter, Playfair_Display } from 'next/font/google';
import './globals.css';
import LenisProvider from '@/components/LenisProvider';

import Navigation from '@/components/Navigation';

const inter = Inter({ 
  subsets: ['latin'],
  variable: '--font-inter',
});

const playfair = Playfair_Display({
  subsets: ['latin'],
  variable: '--font-playfair',
});

export const metadata: Metadata = {
  title: 'Aditya | The Sentient OS',
  description: 'The ultimate luxury integration engine by DarkNova.',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} ${playfair.variable} dark`}>
      <body className="antialiased">
        <LenisProvider>
          <Navigation />
          {children}
        </LenisProvider>
      </body>
    </html>
  );
}
