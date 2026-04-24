'use client';
import { useParams } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { getToiletHistory } from '@/lib/api/toilets';
import { HistoryList } from '@/components/toilet/HistoryList';
import { Header } from '@/components/common/Header';
import { BottomNav } from '@/components/common/BottomNav';
import { Spinner } from '@/components/common/Spinner';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';

export default function ToiletHistoryPage() {
  const params = useParams();
  const toiletId = params.id as string;

  const { data: history = [], isLoading } = useQuery({
    queryKey: ['toilet', toiletId, 'history'],
    queryFn: () => getToiletHistory(toiletId),
  });

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      <Header />
      <main className="max-w-2xl mx-auto px-4 py-6">
        <div className="flex items-center gap-3 mb-6">
          <Link href={`/toilets/${toiletId}`} className="p-2 rounded-full hover:bg-gray-100">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <h1 className="text-xl font-bold">변경 이력</h1>
        </div>

        {isLoading ? (
          <div className="flex justify-center py-12"><Spinner size="lg" /></div>
        ) : (
          <HistoryList history={history} />
        )}
      </main>
      <BottomNav />
    </div>
  );
}
