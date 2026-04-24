'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Map, List, PlusCircle, User } from 'lucide-react';

const navItems = [
  { href: '/', icon: Map, label: '지도' },
  { href: '/toilets', icon: List, label: '목록' },
  { href: '/toilets/new', icon: PlusCircle, label: '등록' },
  { href: '/my', icon: User, label: '내 정보' },
];

export function BottomNav() {
  const pathname = usePathname();

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-40 bg-white border-t safe-area-inset-bottom md:hidden">
      <div className="flex">
        {navItems.map(({ href, icon: Icon, label }) => (
          <Link
            key={href}
            href={href}
            className={`flex-1 flex flex-col items-center py-3 gap-1 text-xs transition-colors ${
              pathname === href ? 'text-[#1F4E79]' : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            <Icon className="w-5 h-5" />
            <span>{label}</span>
          </Link>
        ))}
      </div>
    </nav>
  );
}
