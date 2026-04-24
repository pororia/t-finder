'use client';
import { useState, useCallback } from 'react';
import Link from 'next/link';
import { Plus } from 'lucide-react';
import { ToiletMap } from '@/components/map/GoogleMapComponent';
import { MapSearchBar } from '@/components/map/MapSearchBar';
import { CurrentLocationButton } from '@/components/map/CurrentLocationButton';
import { ToiletCard } from '@/components/toilet/ToiletCard';
import { BottomNav } from '@/components/common/BottomNav';
import { useGeolocation } from '@/hooks/useGeolocation';
import { useInBoundsToilets } from '@/hooks/useToilets';
import type { ToiletNearby } from '@/types/toilet';

const DEFAULT_CENTER = { lat: 37.5665, lng: 126.9780 };

export default function HomePage() {
  const { location } = useGeolocation();
  const center = location || DEFAULT_CENTER;

  const [bounds, setBounds] = useState<{ minLat: number; minLng: number; maxLat: number; maxLng: number } | null>(null);
  const [selectedToilet, setSelectedToilet] = useState<ToiletNearby | null>(null);
  const [mapCenter, setMapCenter] = useState(center);

  const { data: toilets = [] } = useInBoundsToilets(
    bounds?.minLat, bounds?.minLng, bounds?.maxLat, bounds?.maxLng
  );

  const handleLocate = useCallback((loc: { lat: number; lng: number }) => {
    setMapCenter(loc);
  }, []);

  return (
    <div className="h-screen flex flex-col">
      {/* 상단 검색바 */}
      <div className="absolute top-4 left-4 right-4 z-30 flex gap-2">
        <MapSearchBar />
        <CurrentLocationButton onLocate={handleLocate} />
      </div>

      {/* 지도 */}
      <div className="flex-1 relative">
        <ToiletMap
          center={mapCenter}
          toilets={toilets}
          onMarkerClick={setSelectedToilet}
          onBoundsChange={setBounds}
          selectedMarker={selectedToilet?.id}
        />
      </div>

      {/* 선택된 화장실 카드 */}
      {selectedToilet && (
        <div className="absolute bottom-20 left-4 right-4 z-20 animate-in slide-in-from-bottom">
          <div onClick={() => setSelectedToilet(null)} className="absolute -top-2 right-2 bg-gray-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm cursor-pointer z-10">×</div>
          <ToiletCard toilet={selectedToilet} showDistance />
        </div>
      )}

      {/* 등록 버튼 */}
      <Link
        href="/toilets/new"
        className="absolute bottom-24 right-4 z-20 bg-[#1F4E79] text-white rounded-full p-4 shadow-lg hover:bg-[#2E75B6] transition-colors"
        aria-label="화장실 등록"
      >
        <Plus className="w-6 h-6" />
      </Link>

      <BottomNav />
    </div>
  );
}
