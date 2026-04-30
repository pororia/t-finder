'use client';
import { useState, useCallback, useRef, useEffect } from 'react';
import Link from 'next/link';
import { Plus, X } from 'lucide-react';
import { ToiletMap } from '@/components/map/GoogleMapComponent';
import { MapSearchBar } from '@/components/map/MapSearchBar';
import { CurrentLocationButton } from '@/components/map/CurrentLocationButton';
import { ToiletCard } from '@/components/toilet/ToiletCard';
import { BottomNav } from '@/components/common/BottomNav';
import { useGeolocation } from '@/hooks/useGeolocation';
import { useInBoundsToilets } from '@/hooks/useToilets';
import type { ToiletNearby } from '@/types/toilet';

const DEFAULT_CENTER = { lat: 37.5960, lng: 126.8265 }; // 고양시 행주산성 일대 (Gyeonggi 데이터 있음)

export default function HomePage() {
  const { location } = useGeolocation();
  const center = location || DEFAULT_CENTER;

  const [bounds, setBounds] = useState<{ minLat: number; minLng: number; maxLat: number; maxLng: number } | null>(null);
  const [selectedToilet, setSelectedToilet] = useState<ToiletNearby | null>(null);
  const [listOpen, setListOpen] = useState(false);
  const [mapCenter, setMapCenter] = useState(center);
  const selectedRef = useRef<HTMLDivElement>(null);

  const { data: toilets = [] } = useInBoundsToilets(
    bounds?.minLat, bounds?.minLng, bounds?.maxLat, bounds?.maxLng
  );

  const handleMarkerClick = useCallback((toilet: ToiletNearby) => {
    setSelectedToilet(toilet);
    setListOpen(true);
  }, []);

  const handleMapClick = useCallback(() => {
    setListOpen(false);
    setSelectedToilet(null);
  }, []);

  const handleClose = useCallback(() => {
    setListOpen(false);
    setSelectedToilet(null);
  }, []);

  const handleLocate = useCallback((loc: { lat: number; lng: number }) => {
    setMapCenter(loc);
  }, []);

  useEffect(() => {
    if (listOpen && selectedRef.current) {
      selectedRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  }, [listOpen, selectedToilet]);

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
          onMarkerClick={handleMarkerClick}
          onBoundsChange={setBounds}
          onMapClick={handleMapClick}
          selectedMarker={selectedToilet?.id}
        />
      </div>

      {/* 하단 리스트 패널 */}
      {listOpen && (
        <div className="absolute bottom-16 left-0 right-0 z-20 bg-white rounded-t-2xl shadow-xl flex flex-col max-h-[60vh]">
          {/* 헤더 */}
          <div className="flex items-center justify-between px-4 py-3 border-b flex-shrink-0">
            <div className="w-10 h-1 bg-gray-300 rounded-full absolute left-1/2 -translate-x-1/2 top-2" />
            <span className="font-semibold text-gray-800 mt-1">
              주변 화장실{' '}
              <span className="text-blue-600">{toilets.length}개</span>
            </span>
            <button
              onClick={handleClose}
              className="p-1.5 rounded-full hover:bg-gray-100 transition-colors"
              aria-label="닫기"
            >
              <X className="w-5 h-5 text-gray-500" />
            </button>
          </div>

          {/* 리스트 */}
          <div className="overflow-y-auto flex-1 p-3 space-y-2">
            {toilets.length === 0 ? (
              <p className="text-center text-gray-400 py-8">이 지역에 화장실 정보가 없습니다.</p>
            ) : (
              toilets.map((toilet: ToiletNearby) => (
                <div
                  key={toilet.id}
                  ref={toilet.id === selectedToilet?.id ? selectedRef : null}
                  className={
                    toilet.id === selectedToilet?.id
                      ? 'ring-2 ring-blue-500 rounded-xl'
                      : ''
                  }
                >
                  <ToiletCard toilet={toilet} showDistance={false} />
                </div>
              ))
            )}
          </div>
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
