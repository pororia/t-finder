'use client';
import { useParams, useRouter } from 'next/navigation';
import toast from 'react-hot-toast';
import { useToiletDetail } from '@/hooks/useToilets';
import { ToiletForm } from '@/components/toilet/ToiletForm';
import { Header } from '@/components/common/Header';
import { BottomNav } from '@/components/common/BottomNav';
import { Spinner } from '@/components/common/Spinner';
import { updateToilet } from '@/lib/api/toilets';
import { useAuthStore } from '@/store/authStore';
import { useState } from 'react';

export default function EditToiletPage() {
  const params = useParams();
  const router = useRouter();
  const { user } = useAuthStore();
  const [isLoading, setIsLoading] = useState(false);
  const toiletId = params.id as string;
  const { data: toilet, isLoading: fetching } = useToiletDetail(toiletId);

  if (fetching) return <div className="min-h-screen flex items-center justify-center"><Spinner size="lg" /></div>;
  if (!toilet || !user || user.id !== toilet.created_by) {
    router.push('/');
    return null;
  }

  const handleSubmit = async (data: Parameters<typeof updateToilet>[1]) => {
    setIsLoading(true);
    try {
      await updateToilet(toiletId, data);
      toast.success('수정되었습니다!');
      router.push(`/toilets/${toiletId}`);
    } catch {
      toast.error('수정에 실패했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      <Header />
      <main className="max-w-2xl mx-auto px-4 py-6">
        <h1 className="text-xl font-bold text-gray-900 mb-6">화장실 수정</h1>
        <ToiletForm
          defaultValues={{
            address: toilet.address,
            address_detail: toilet.address_detail ?? undefined,
            name: toilet.name ?? undefined,
            cleanliness: toilet.cleanliness,
            description: toilet.description ?? undefined,
            has_password: toilet.has_password,
            is_unisex: toilet.is_unisex,
            is_accessible: toilet.is_accessible,
            seat_count: toilet.seat_count,
            urinal_count: toilet.urinal_count,
            payment_type: toilet.payment_type,
            cost: toilet.cost ?? undefined,
            location: toilet.location,
          }}
          onSubmit={handleSubmit}
          isLoading={isLoading}
          selectedLocation={toilet.location}
        />
      </main>
      <BottomNav />
    </div>
  );
}
