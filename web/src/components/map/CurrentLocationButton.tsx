'use client';
import { MapPin } from 'lucide-react';
import { useGeolocation } from '@/hooks/useGeolocation';
import { Spinner } from '@/components/common/Spinner';

interface Props {
  onLocate?: (location: { lat: number; lng: number }) => void;
}

export function CurrentLocationButton({ onLocate }: Props) {
  const { loading, refetch, location } = useGeolocation();

  const handleClick = () => {
    refetch();
    if (location) onLocate?.(location);
  };

  return (
    <button
      onClick={handleClick}
      className="bg-white rounded-full p-3 shadow-lg border hover:bg-gray-50 transition-colors"
      aria-label="현재 위치"
    >
      {loading ? <Spinner size="sm" className="text-[#1F4E79]" /> : <MapPin className="w-5 h-5 text-[#1F4E79]" />}
    </button>
  );
}
