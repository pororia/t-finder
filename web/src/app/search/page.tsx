'use client';
import { useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { Search } from 'lucide-react';
import { useSearchToilets } from '@/hooks/useToilets';
import { ToiletCard } from '@/components/toilet/ToiletCard';
import { Header } from '@/components/common/Header';
import { BottomNav } from '@/components/common/BottomNav';
import { Spinner } from '@/components/common/Spinner';
import type { ToiletNearby } from '@/types/toilet';

export default function SearchPage() {
  const searchParams = useSearchParams();
  const initialQ = searchParams.get('q') || '';
  const [query, setQuery] = useState(initialQ);
  const [searchQuery, setSearchQuery] = useState(initialQ);

  const { data: results = [], isLoading } = useSearchToilets(searchQuery);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setSearchQuery(query);
  };

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      <Header />
      <main className="max-w-2xl mx-auto px-4 py-6">
        <form onSubmit={handleSearch} className="mb-6">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="주소, 이름으로 검색"
              className="w-full pl-10 pr-4 py-3 border rounded-xl focus:outline-none focus:ring-2 focus:ring-[#1F4E79] bg-white"
              autoFocus
            />
          </div>
        </form>

        {isLoading && <div className="flex justify-center py-8"><Spinner size="lg" /></div>}

        {!isLoading && searchQuery && (
          <p className="text-sm text-gray-500 mb-4">
            &ldquo;{searchQuery}&rdquo; 검색 결과 {results.length}건
          </p>
        )}

        <div className="space-y-3">
          {results.map((toilet: ToiletNearby) => (
            <ToiletCard key={toilet.id} toilet={toilet} showDistance={false} />
          ))}
          {!isLoading && searchQuery && results.length === 0 && (
            <p className="text-center text-gray-500 py-8">검색 결과가 없습니다.</p>
          )}
        </div>
      </main>
      <BottomNav />
    </div>
  );
}
