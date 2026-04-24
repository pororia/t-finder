'use client';
import { useQuery } from '@tanstack/react-query';
import { getToilets } from '@/lib/api/toilets';
import { ToiletCard } from '@/components/toilet/ToiletCard';
import { Header } from '@/components/common/Header';
import { BottomNav } from '@/components/common/BottomNav';
import { Spinner } from '@/components/common/Spinner';
import type { ToiletNearby } from '@/types/toilet';

export default function ToiletsPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['toilets', 'list'],
    queryFn: () => getToilets(0, 50),
  });

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      <Header />
      <main className="max-w-2xl mx-auto px-4 py-6">
        <h1 className="text-xl font-bold text-gray-900 mb-4">화장실 목록</h1>
        {isLoading ? (
          <div className="flex justify-center py-12"><Spinner size="lg" /></div>
        ) : (
          <div className="space-y-3">
            {(data?.results || []).map((toilet: ToiletNearby) => (
              <ToiletCard key={toilet.id} toilet={toilet} showDistance={false} />
            ))}
            {(data?.results || []).length === 0 && (
              <p className="text-center text-gray-500 py-8">등록된 화장실이 없습니다.</p>
            )}
          </div>
        )}
      </main>
      <BottomNav />
    </div>
  );
}
