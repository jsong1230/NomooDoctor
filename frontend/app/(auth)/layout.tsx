/**
 * 인증 페이지 레이아웃
 * 중앙 정렬 카드 레이아웃 + 로고 표시
 */

import { ReactNode } from 'react';

interface AuthLayoutProps {
  children: ReactNode;
}

export default function AuthLayout({ children }: AuthLayoutProps) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 px-4">
      <div className="w-full max-w-md">
        {/* 로고 */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-slate-900 tracking-tight">
            노무닥터
          </h1>
          <p className="text-sm text-slate-600 mt-2">
            AI 기반 노무/HR 자동화 서비스
          </p>
        </div>

        {/* 카드 */}
        <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6">
          {children}
        </div>

        {/* 하단 안내 */}
        <p className="text-center text-xs text-slate-500 mt-6">
          본 서비스를 이용하면 이용약관과 개인정보처리방침에 동의한 것으로 간주됩니다.
        </p>
      </div>
    </div>
  );
}
