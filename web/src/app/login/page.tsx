import { MapPin } from 'lucide-react';
import { GoogleLoginButton } from '@/components/auth/GoogleLoginButton';

export default function LoginPage() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-[#1F4E79] to-[#2E75B6] p-6">
      <div className="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-sm text-center">
        <div className="flex items-center justify-center gap-2 mb-2">
          <MapPin className="w-8 h-8 text-[#1F4E79]" />
          <h1 className="text-3xl font-bold text-[#1F4E79]">T-Finder</h1>
        </div>
        <p className="text-gray-500 mb-8 text-sm">주변 화장실을 빠르게 찾아보세요</p>
        <GoogleLoginButton />
        <p className="mt-6 text-xs text-gray-400">
          로그인하면 화장실 등록 및 리뷰 작성이 가능합니다.
        </p>
      </div>
    </div>
  );
}
