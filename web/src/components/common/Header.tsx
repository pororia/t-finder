'use client';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Search, User, MapPin } from 'lucide-react';
import { useAuthStore } from '@/store/authStore';
import Image from 'next/image';

export function Header() {
  const router = useRouter();
  const { user } = useAuthStore();

  return (
    <header className="sticky top-0 z-40 bg-white border-b shadow-sm">
      <div className="max-w-7xl mx-auto px-4 h-14 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2 font-bold text-[#1F4E79] text-xl">
          <MapPin className="w-6 h-6" />
          T-Finder
        </Link>
        <nav className="flex items-center gap-3">
          <button onClick={() => router.push('/search')} className="p-2 rounded-full hover:bg-gray-100" aria-label="검색">
            <Search className="w-5 h-5 text-gray-600" />
          </button>
          <button onClick={() => router.push(user ? '/my' : '/login')} className="p-2 rounded-full hover:bg-gray-100" aria-label="프로필">
            {user?.profile_image_url ? (
              <Image src={user.profile_image_url} alt={user.nickname} width={28} height={28} className="rounded-full" />
            ) : (
              <User className="w-5 h-5 text-gray-600" />
            )}
          </button>
        </nav>
      </div>
    </header>
  );
}
