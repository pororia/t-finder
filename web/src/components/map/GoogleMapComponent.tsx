'use client';
import { GoogleMap, useJsApiLoader, Marker } from '@react-google-maps/api';
import { useState, useCallback } from 'react';
import type { ToiletNearby } from '@/types/toilet';

interface Props {
  center: { lat: number; lng: number };
  toilets: ToiletNearby[];
  onMarkerClick: (toilet: ToiletNearby) => void;
  onBoundsChange?: (bounds: { minLat: number; minLng: number; maxLat: number; maxLng: number }) => void;
  onMapClick?: (location: { lat: number; lng: number }) => void;
  selectedMarker?: string | null;
}

const libraries: ['places'] = ['places'];

function getMarkerIconUrl(cleanliness: number): string {
  if (cleanliness >= 4) return 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(`
    <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 40 40">
      <circle cx="20" cy="20" r="18" fill="#22c55e" stroke="white" stroke-width="2"/>
      <text x="20" y="26" text-anchor="middle" font-size="16" font-weight="bold" fill="white">${cleanliness}</text>
    </svg>`);
  if (cleanliness >= 3) return 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(`
    <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 40 40">
      <circle cx="20" cy="20" r="18" fill="#f59e0b" stroke="white" stroke-width="2"/>
      <text x="20" y="26" text-anchor="middle" font-size="16" font-weight="bold" fill="white">${cleanliness}</text>
    </svg>`);
  return 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(`
    <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 40 40">
      <circle cx="20" cy="20" r="18" fill="#ef4444" stroke="white" stroke-width="2"/>
      <text x="20" y="26" text-anchor="middle" font-size="16" font-weight="bold" fill="white">${cleanliness}</text>
    </svg>`);
}

export function ToiletMap({ center, toilets, onMarkerClick, onBoundsChange, onMapClick, selectedMarker }: Props) {
  const { isLoaded } = useJsApiLoader({
    googleMapsApiKey: process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY || '',
    libraries,
  });

  const [map, setMap] = useState<google.maps.Map | null>(null);
  const onLoad = useCallback((m: google.maps.Map) => setMap(m), []);

  if (!isLoaded) {
    return (
      <div className="h-full flex items-center justify-center bg-gray-100">
        <div className="text-center text-gray-500">
          <div className="text-4xl mb-2">🗺️</div>
          <p>지도 로딩 중...</p>
        </div>
      </div>
    );
  }

  return (
    <GoogleMap
      mapContainerStyle={{ width: '100%', height: '100%' }}
      center={center}
      zoom={15}
      onLoad={onLoad}
      onClick={(e) => {
        if (e.latLng) onMapClick?.({ lat: e.latLng.lat(), lng: e.latLng.lng() });
      }}
      onIdle={() => {
        if (map && onBoundsChange) {
          const bounds = map.getBounds();
          if (bounds) {
            const ne = bounds.getNorthEast();
            const sw = bounds.getSouthWest();
            onBoundsChange({ minLat: sw.lat(), minLng: sw.lng(), maxLat: ne.lat(), maxLng: ne.lng() });
          }
        }
      }}
      options={{ disableDefaultUI: true, zoomControl: true, gestureHandling: 'greedy' }}
    >
      {toilets.map((toilet) => (
        <Marker
          key={toilet.id}
          position={{ lat: toilet.location.lat, lng: toilet.location.lng }}
          onClick={() => onMarkerClick(toilet)}
          icon={{
            url: getMarkerIconUrl(toilet.cleanliness),
            scaledSize: new google.maps.Size(selectedMarker === toilet.id ? 48 : 40, selectedMarker === toilet.id ? 48 : 40),
          }}
        />
      ))}
    </GoogleMap>
  );
}
