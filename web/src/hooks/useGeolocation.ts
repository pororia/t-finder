'use client';
import { useState, useEffect } from 'react';
import { useLocationStore } from '@/store/locationStore';

export function useGeolocation() {
  const { location, setLocation } = useLocationStore();
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const getCurrentLocation = () => {
    setLoading(true);
    if (!navigator.geolocation) {
      setError('Geolocation을 지원하지 않는 브라우저입니다.');
      setLoading(false);
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setLocation({ lat: pos.coords.latitude, lng: pos.coords.longitude });
        setLoading(false);
      },
      (err) => {
        setError(err.message);
        setLoading(false);
      },
      { enableHighAccuracy: true, timeout: 10000 }
    );
  };

  useEffect(() => {
    getCurrentLocation();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return { location, error, loading, refetch: getCurrentLocation };
}
