'use client';
import { ReactNode } from 'react';

interface Props {
  children: ReactNode;
  onClick?: () => void;
  type?: 'button' | 'submit' | 'reset';
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  className?: string;
  fullWidth?: boolean;
}

const variants = {
  primary: 'bg-[#1F4E79] text-white hover:bg-[#2E75B6] disabled:bg-gray-400',
  secondary: 'bg-white text-[#1F4E79] border border-[#1F4E79] hover:bg-blue-50',
  danger: 'bg-red-500 text-white hover:bg-red-600 disabled:bg-gray-400',
  ghost: 'bg-transparent text-gray-600 hover:bg-gray-100',
};

const sizes = { sm: 'px-3 py-1.5 text-sm', md: 'px-4 py-2', lg: 'px-6 py-3 text-lg' };

export function Button({
  children, onClick, type = 'button', variant = 'primary',
  size = 'md', disabled, loading, className = '', fullWidth,
}: Props) {
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled || loading}
      className={`
        rounded-lg font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2
        ${variants[variant]} ${sizes[size]} ${fullWidth ? 'w-full' : ''} ${className}
        ${disabled || loading ? 'cursor-not-allowed opacity-60' : 'cursor-pointer'}
      `}
    >
      {loading ? (
        <span className="flex items-center justify-center gap-2">
          <span className="inline-block w-4 h-4 animate-spin rounded-full border-2 border-white border-r-transparent" />
          처리 중...
        </span>
      ) : children}
    </button>
  );
}
