'use client';
import { useQuery } from '@tanstack/react-query';
import { getNearbyToilets, getToilet, searchToilets, getInBoundsToilets } from '@/lib/api/toilets';

export function useNearbyToilets(lat?: number, lng?: number, radius = 1000) {
  return useQuery({
    queryKey: ['toilets', 'nearby', lat, lng, radius],
    queryFn: () => getNearbyToilets(lat!, lng!, radius),
    enabled: !!lat && !!lng,
    staleTime: 60 * 1000,
  });
}

export function useToiletDetail(id: string) {
  return useQuery({
    queryKey: ['toilet', id],
    queryFn: () => getToilet(id),
    enabled: !!id,
  });
}

export function useSearchToilets(q: string) {
  return useQuery({
    queryKey: ['toilets', 'search', q],
    queryFn: () => searchToilets(q),
    enabled: q.length >= 2,
    staleTime: 30 * 1000,
  });
}

export function useInBoundsToilets(
  minLat?: number,
  minLng?: number,
  maxLat?: number,
  maxLng?: number
) {
  return useQuery({
    queryKey: ['toilets', 'bounds', minLat, minLng, maxLat, maxLng],
    queryFn: () => getInBoundsToilets(minLat!, minLng!, maxLat!, maxLng!),
    enabled: !!(minLat && minLng && maxLat && maxLng),
    staleTime: 30 * 1000,
  });
}
