'use client';
import Link from 'next/link';
import Image from 'next/image';
import { MapPin, Lock, Accessibility, DollarSign } from 'lucide-react';
import { CleanlinessRating } from './CleanlinessRating';
import { formatDistance } from '@/lib/utils/distance';
import { formatPaymentType } from '@/lib/utils/format';
import type { Toilet, ToiletNearby } from '@/types/toilet';

interface Props {
  toilet: Toilet | ToiletNearby;
  showDistance?: boolean;
}

export function ToiletCard({ toilet, showDistance = true }: Props) {
  return (
    <Link href={`/toilets/${toilet.id}`} className="block bg-white rounded-xl shadow-sm border hover:shadow-md transition-shadow p-4">
      <div className="flex gap-3">
        {'thumbnail_url' in toilet && toilet.thumbnail_url ? (
          <div className="relative w-20 h-20 flex-shrink-0 rounded-lg overflow-hidden">
            <Image src={toilet.thumbnail_url} alt="화장실 사진" fill className="object-cover" />
          </div>
        ) : (
          <div className="w-20 h-20 flex-shrink-0 rounded-lg bg-gray-100 flex items-center justify-center text-3xl">
            🚻
          </div>
        )}
        <div className="flex-1 min-w-0">
          {'name' in toilet && toilet.name && (
            <p className="font-semibold text-gray-900 truncate">{toilet.name}</p>
          )}
          <p className={`truncate ${'name' in toilet && toilet.name ? 'text-sm text-gray-500' : 'font-semibold text-gray-900'}`}>{toilet.address}</p>
          <div className="mt-1">
            <CleanlinessRating value={toilet.cleanliness} readOnly size="sm" />
          </div>
          <div className="flex flex-wrap gap-2 mt-2">
            {toilet.is_accessible && (
              <span className="flex items-center gap-1 text-xs text-blue-600 bg-blue-50 px-2 py-0.5 rounded-full">
                <Accessibility className="w-3 h-3" /> 장애인
              </span>
            )}
            {toilet.has_password && (
              <span className="flex items-center gap-1 text-xs text-orange-600 bg-orange-50 px-2 py-0.5 rounded-full">
                <Lock className="w-3 h-3" /> 비밀번호
              </span>
            )}
            <span className="flex items-center gap-1 text-xs text-green-600 bg-green-50 px-2 py-0.5 rounded-full">
              <DollarSign className="w-3 h-3" /> {formatPaymentType(toilet.payment_type, toilet.cost)}
            </span>
          </div>
          {showDistance && 'distance_m' in toilet && toilet.distance_m != null && (
            <p className="mt-1 text-sm text-gray-500 flex items-center gap-1">
              <MapPin className="w-3 h-3" />
              {formatDistance(toilet.distance_m)}
            </p>
          )}
        </div>
      </div>
    </Link>
  );
}
