'use client';
import { useRouter } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import Image from 'next/image';
import { LogOut, MapPin } from 'lucide-react';
import toast from 'react-hot-toast';
import { useAuthStore } from '@/store/authStore';
import { logout } from '@/lib/firebase/auth';
import { getToilets } from '@/lib/api/toilets';
import { Header } from '@/components/common/Header';
import { BottomNav } from '@/components/common/BottomNav';
import { Spinner } from '@/components/common/Spinner';
import { Button } from '@/components/common/Button';
import Link from 'next/link';

export default function MyPage() {
  const router = useRouter();
  const { user, setUser } = useAuthStore();

  const { data: toiletsData, isLoading } = useQuery({
    queryKey: ['my-toilets'],
    queryFn: () => getToilets(0, 10),
    enabled: !!user,
  });

  if (!user) {
    router.push('/login');
    return null;
  }

  const handleLogout = async () => {
    await logout();
    setUser(null);
    toast.success('로그아웃되었습니다.');
    router.push('/');
  };

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      <Header />
      <main className="max-w-2xl mx-auto px-4 py-6 space-y-6">
        {/* 프로필 */}
        <div className="bg-white rounded-2xl shadow-sm p-6 flex items-center gap-4">
          {user.profile_image_url ? (
            <Image src={user.profile_image_url} alt={user.nickname} width={64} height={64} className="rounded-full" />
          ) : (
            <div className="w-16 h-16 rounded-full bg-[#1F4E79] flex items-center justify-center text-white text-2xl font-bold">
              {user.nickname[0]}
            </div>
          )}
          <div className="flex-1">
            <h2 className="text-xl font-bold text-gray-900">{user.nickname}</h2>
            <p className="text-sm text-gray-500">{user.email}</p>
          </div>
        </div>

        {/* 내가 등록한 화장실 */}
        <div>
          <div className="flex items-center gap-2 mb-3">
            <MapPin className="w-5 h-5 text-[#1F4E79]" />
            <h3 className="font-bold text-gray-900">최근 등록한 화장실</h3>
          </div>
          {isLoading ? (
            <div className="flex justify-center py-4"><Spinner /></div>
          ) : (
            <div className="space-y-2">
              {(toiletsData?.results || []).slice(0, 5).map((t: { id: string; address: string; name: string | null; cleanliness: number }) => (
                <Link
                  key={t.id}
                  href={`/toilets/${t.id}`}
                  className="block bg-white rounded-xl p-4 shadow-sm border hover:shadow-md transition-shadow"
                >
                  <p className="font-medium text-gray-900">{t.name || t.address}</p>
                  {t.name && <p className="text-sm text-gray-500 mt-0.5">{t.address}</p>}
                  <p className="text-xs text-amber-500 mt-1">{'★'.repeat(t.cleanliness)}</p>
                </Link>
              ))}
              {(toiletsData?.results || []).length === 0 && (
                <p className="text-gray-500 text-sm py-4 text-center">등록한 화장실이 없습니다.</p>
              )}
            </div>
          )}
        </div>

        {/* 로그아웃 */}
        <Button variant="ghost" onClick={handleLogout} fullWidth className="flex items-center justify-center gap-2 border border-gray-200 rounded-xl">
          <LogOut className="w-4 h-4" />
          로그아웃
        </Button>
      </main>
      <BottomNav />
    </div>
  );
}
