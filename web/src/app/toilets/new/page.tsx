'use client';
import { useState, useCallback, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { GoogleMap, useJsApiLoader, Marker } from '@react-google-maps/api';
import toast from 'react-hot-toast';
import { ToiletForm } from '@/components/toilet/ToiletForm';
import { Header } from '@/components/common/Header';
import { BottomNav } from '@/components/common/BottomNav';
import { createToilet } from '@/lib/api/toilets';
import { useAuthStore } from '@/store/authStore';

const libraries: ['places'] = ['places'];
const DEFAULT_CENTER = { lat: 37.5665, lng: 126.9780 };

export default function NewToiletPage() {
  const router = useRouter();
  const { user } = useAuthStore();
  const [selectedLocation, setSelectedLocation] = useState<{ lat: number; lng: number } | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const { isLoaded } = useJsApiLoader({
    googleMapsApiKey: process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY || '',
    libraries,
  });

  useEffect(() => {
    if (!user) router.push('/login');
  }, [user, router]);

  if (!user) return null;

  const handleSubmit = async (data: Parameters<typeof createToilet>[0]) => {
    if (!selectedLocation) {
      toast.error('지도에서 위치를 선택해주세요.');
      return;
    }
    setIsLoading(true);
    try {
      const result = await createToilet({ ...data, location: selectedLocation });
      toast.success('화장실이 등록되었습니다!');
      router.push(`/toilets/${result.id}`);
    } catch {
      toast.error('등록에 실패했습니다. 다시 시도해주세요.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      <Header />
      <main className="max-w-2xl mx-auto">
        {/* 지도 위치 선택 */}
        <div className="h-64 bg-gray-200">
          {isLoaded ? (
            <GoogleMap
              mapContainerStyle={{ width: '100%', height: '100%' }}
              center={selectedLocation || DEFAULT_CENTER}
              zoom={15}
              onClick={(e) => {
                if (e.latLng) setSelectedLocation({ lat: e.latLng.lat(), lng: e.latLng.lng() });
              }}
              options={{ disableDefaultUI: true, zoomControl: true }}
            >
              {selectedLocation && <Marker position={selectedLocation} />}
            </GoogleMap>
          ) : (
            <div className="h-full flex items-center justify-center text-gray-500">지도 로딩 중...</div>
          )}
        </div>
        {!selectedLocation && (
          <div className="bg-amber-50 border-b border-amber-200 px-4 py-2 text-sm text-amber-700 text-center">
            지도를 클릭해서 화장실 위치를 선택하세요
          </div>
        )}

        <div className="px-4 py-6">
          <h1 className="text-xl font-bold text-gray-900 mb-6">화장실 등록</h1>
          <ToiletForm onSubmit={handleSubmit} isLoading={isLoading} selectedLocation={selectedLocation || undefined} />
        </div>
      </main>
      <BottomNav />
    </div>
  );
}
