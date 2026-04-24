'use client';
import { useParams, useRouter } from 'next/navigation';
import Image from 'next/image';
import Link from 'next/link';
import toast from 'react-hot-toast';
import { MapPin, Lock, Accessibility, DollarSign, Edit, Clock, Trash2 } from 'lucide-react';
import { useToiletDetail } from '@/hooks/useToilets';
import { CleanlinessRating } from '@/components/toilet/CleanlinessRating';
import { Header } from '@/components/common/Header';
import { BottomNav } from '@/components/common/BottomNav';
import { Spinner } from '@/components/common/Spinner';
import { Button } from '@/components/common/Button';
import { useAuthStore } from '@/store/authStore';
import { deleteToilet } from '@/lib/api/toilets';
import { formatDate, formatPaymentType } from '@/lib/utils/format';
import { useState } from 'react';

export default function ToiletDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { user } = useAuthStore();
  const [deleting, setDeleting] = useState(false);
  const toiletId = params.id as string;
  const { data: toilet, isLoading } = useToiletDetail(toiletId);

  if (isLoading) return (
    <div className="min-h-screen flex items-center justify-center"><Spinner size="lg" /></div>
  );
  if (!toilet) return (
    <div className="min-h-screen flex items-center justify-center text-gray-500">화장실을 찾을 수 없습니다.</div>
  );

  const isOwner = user?.id === toilet.created_by;

  const handleDelete = async () => {
    if (!confirm('정말 삭제하시겠습니까?')) return;
    setDeleting(true);
    try {
      await deleteToilet(toiletId);
      toast.success('삭제되었습니다.');
      router.push('/toilets');
    } catch {
      toast.error('삭제에 실패했습니다.');
    } finally {
      setDeleting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      <Header />
      <main className="max-w-2xl mx-auto">
        {/* 사진 캐러셀 */}
        {toilet.photos.length > 0 ? (
          <div className="relative h-64 bg-gray-200 overflow-x-auto flex">
            {toilet.photos.map((photo) => (
              <div key={photo.id} className="relative h-64 min-w-full">
                <Image src={photo.image_url} alt="화장실 사진" fill className="object-cover" />
              </div>
            ))}
          </div>
        ) : (
          <div className="h-48 bg-gray-100 flex items-center justify-center text-6xl">🚻</div>
        )}

        <div className="px-4 py-6 space-y-5">
          {/* 기본 정보 */}
          <div>
            <h1 className="text-xl font-bold text-gray-900">{toilet.name || toilet.address}</h1>
            {toilet.name && (
              <p className="text-sm text-gray-500 flex items-center gap-1 mt-1">
                <MapPin className="w-4 h-4" /> {toilet.address}
              </p>
            )}
          </div>

          {/* 평점 */}
          <div className="flex items-center gap-3">
            <CleanlinessRating value={Math.round(toilet.avg_rating || toilet.cleanliness)} readOnly size="md" />
            <span className="text-sm text-gray-500">
              {toilet.avg_rating ? toilet.avg_rating.toFixed(1) : toilet.cleanliness}/5
              {toilet.review_count > 0 && ` (${toilet.review_count}개 리뷰)`}
            </span>
          </div>

          {/* 시설 배지 */}
          <div className="flex flex-wrap gap-2">
            {toilet.is_accessible && (
              <span className="flex items-center gap-1 text-sm text-blue-600 bg-blue-50 px-3 py-1 rounded-full">
                <Accessibility className="w-4 h-4" /> 장애인 가능
              </span>
            )}
            {toilet.is_unisex && (
              <span className="text-sm text-purple-600 bg-purple-50 px-3 py-1 rounded-full">남녀 공용</span>
            )}
            {toilet.has_password && (
              <span className="flex items-center gap-1 text-sm text-orange-600 bg-orange-50 px-3 py-1 rounded-full">
                <Lock className="w-4 h-4" /> 비밀번호 있음
              </span>
            )}
            <span className="flex items-center gap-1 text-sm text-green-600 bg-green-50 px-3 py-1 rounded-full">
              <DollarSign className="w-4 h-4" /> {formatPaymentType(toilet.payment_type, toilet.cost)}
            </span>
          </div>

          {/* 비밀번호 (로그인 시) */}
          {toilet.has_password && user && toilet.password_value && (
            <div className="bg-orange-50 border border-orange-200 rounded-xl p-4">
              <p className="text-sm font-medium text-orange-700">비밀번호</p>
              <p className="text-lg font-bold text-orange-900 mt-1">{toilet.password_value}</p>
            </div>
          )}

          {/* 변기 수 */}
          {(toilet.seat_count > 0 || toilet.urinal_count > 0) && (
            <div className="bg-gray-50 rounded-xl p-4 grid grid-cols-2 gap-4 text-center">
              <div><p className="text-2xl font-bold">{toilet.seat_count}</p><p className="text-sm text-gray-500">좌변기</p></div>
              <div><p className="text-2xl font-bold">{toilet.urinal_count}</p><p className="text-sm text-gray-500">소변기</p></div>
            </div>
          )}

          {/* 설명 */}
          {toilet.description && (
            <p className="text-gray-700 bg-gray-50 rounded-xl p-4">{toilet.description}</p>
          )}

          {/* 등록일 */}
          <p className="text-xs text-gray-400">등록일: {formatDate(toilet.created_at)}</p>

          {/* 액션 버튼 */}
          <div className="flex gap-3">
            <Link
              href={`https://maps.google.com/?q=${toilet.location.lat},${toilet.location.lng}`}
              target="_blank"
              rel="noopener noreferrer"
              className="flex-1 bg-[#1F4E79] text-white rounded-xl py-3 text-center font-medium"
            >
              길 찾기
            </Link>
            {isOwner && (
              <>
                <Link
                  href={`/toilets/${toiletId}/edit`}
                  className="flex items-center gap-2 bg-gray-100 text-gray-700 rounded-xl px-4 py-3 font-medium"
                >
                  <Edit className="w-4 h-4" /> 수정
                </Link>
                <Button variant="danger" onClick={handleDelete} loading={deleting}>
                  <Trash2 className="w-4 h-4" />
                </Button>
              </>
            )}
          </div>

          {/* 이력 보기 */}
          <Link
            href={`/toilets/${toiletId}/history`}
            className="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-700"
          >
            <Clock className="w-4 h-4" /> 변경 이력 보기
          </Link>
        </div>
      </main>
      <BottomNav />
    </div>
  );
}
