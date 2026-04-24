import type { Metadata } from 'next';
import { Toaster } from 'react-hot-toast';
import QueryProvider from '@/components/providers/QueryProvider';
import '@/styles/globals.css';

export const metadata: Metadata = {
  title: 'T-Finder - 화장실 찾기',
  description: '주변 화장실을 빠르게 찾아보세요. 사용자 참여형 화장실 위치 정보 서비스.',
  keywords: '화장실, 공중화장실, 위치, 지도',
  manifest: '/manifest.json',
  themeColor: '#1F4E79',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <body>
        <QueryProvider>
          {children}
          <Toaster position="top-center" />
        </QueryProvider>
      </body>
    </html>
  );
}
