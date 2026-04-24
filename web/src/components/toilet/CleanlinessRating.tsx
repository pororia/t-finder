'use client';
import { Star } from 'lucide-react';

interface Props {
  value: number;
  onChange?: (value: number) => void;
  readOnly?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

const sizeClasses = { sm: 'w-4 h-4', md: 'w-6 h-6', lg: 'w-8 h-8' };

export function CleanlinessRating({ value, onChange, readOnly = false, size = 'md' }: Props) {
  const sizeClass = sizeClasses[size];

  return (
    <div className="flex gap-1">
      {[1, 2, 3, 4, 5].map((n) => (
        <button
          key={n}
          type="button"
          disabled={readOnly}
          onClick={() => !readOnly && onChange?.(n)}
          className={readOnly ? 'cursor-default' : 'cursor-pointer hover:scale-110 transition-transform'}
        >
          <Star
            className={sizeClass}
            fill={n <= value ? '#FBBF24' : 'none'}
            stroke={n <= value ? '#FBBF24' : '#D1D5DB'}
          />
        </button>
      ))}
    </div>
  );
}
