'use client';

import Link from 'next/link';
import Image from 'next/image';
import { usePathname } from 'next/navigation';
import { motion } from 'framer-motion';

export default function Navigation() {
  const pathname = usePathname();

  const links = [
    { href: '/', label: 'Showcase' },
    { href: '/dashboard', label: 'Command Center' },
    { href: '/docs', label: 'Documentation' },
  ];

  return (
    <motion.nav 
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.8, ease: "easeOut" }}
      className="fixed top-0 left-0 w-full z-50 flex justify-center pt-4 md:pt-6 px-2 md:px-4"
    >
      <div className="glass-panel px-4 py-2 md:px-6 md:py-3 rounded-full flex items-center space-x-4 md:space-x-8 shadow-2xl shadow-black/50 overflow-x-auto no-scrollbar max-w-full">
        <Link href="/" className="flex items-center flex-shrink-0 mr-2 md:mr-4">
          <Image src="/logo.png" alt="Aditya Logo" width={32} height={32} className="rounded-full object-cover" />
        </Link>
        {links.map((link) => {
          const isActive = pathname === link.href;
          return (
            <Link 
              key={link.href} 
              href={link.href}
              className={`relative text-xs md:text-sm font-medium tracking-wide uppercase transition-colors duration-300 whitespace-nowrap ${isActive ? 'text-white' : 'text-gray-400 hover:text-gray-200'}`}
            >
              {link.label}
              {isActive && (
                <motion.div 
                  layoutId="nav-pill"
                  className="absolute -bottom-1.5 md:-bottom-2 left-1/2 -translate-x-1/2 w-1 h-1 bg-[var(--color-highlight)] rounded-full shadow-[0_0_8px_var(--color-highlight)]"
                />
              )}
            </Link>
          );
        })}
      </div>
    </motion.nav>
  );
}
