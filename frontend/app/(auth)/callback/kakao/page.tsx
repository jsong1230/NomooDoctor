'use client';

/**
 * 카카오 OAuth 콜백 페이지
 * 인증 코드와 state를 처리하여 로그인/회원가입 수행
 */

import { Suspense, useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Loader2 } from 'lucide-react';

function KakaoCallbackContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const code = searchParams.get('code');
    const state = searchParams.get('state');
    const errorParam = searchParams.get('error');

    // 에러 처리
    if (errorParam) {
      setError(`카카오 로그인에 실패했습니다: ${errorParam}`);
      setTimeout(() => {
        router.push('/login');
      }, 3000);
      return;
    }

    // 필수 파라미터 확인
    if (!code) {
      setError('인증 코드가 없습니다.');
      setTimeout(() => {
        router.push('/login');
      }, 3000);
      return;
    }

    // 카카오 OAuth 로그인 처리 (백엔드 API 호출)
    // 백엔드가 완료되면 실제 API 연동으로 교체
    handleKakaoLogin(code, state);
  }, [searchParams, router]);

  const handleKakaoLogin = async (code: string, state: string | null) => {
    try {
      // 백엔드 API 호출 (현재는 Mock)
      // const response = await axios.post('/api/v1/auth/kakao/callback', { code, state });

      // 임시: 로그인 성공 시뮬레이션
      // TODO: 백엔드 완료 후 실제 API 연동
      router.push('/dashboard');
    } catch (err: any) {
      const errorCode = err.response?.data?.code;
      const errorMessage = err.response?.data?.detail || '로그인에 실패했습니다';

      setError(errorMessage);

      // 에러와 함께 로그인 페이지로 리다이렉트
      if (errorCode) {
        router.push(`/login?error=${errorCode}`);
      } else {
        setTimeout(() => {
          router.push('/login');
        }, 3000);
      }
    }
  };

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px]">
        <div className="p-4 bg-error-50 border border-error-200 rounded-lg text-center max-w-md">
          <h3 className="font-semibold text-error-900 mb-2">
            로그인 실패
          </h3>
          <p className="text-sm text-error-800">{error}</p>
          <p className="text-xs text-error-700 mt-3">
            잠시 후 로그인 페이지로 이동합니다...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-[400px]">
      <Loader2 className="w-12 h-12 text-primary-600 animate-spin mb-4" />
      <p className="text-slate-600">로그인 처리 중...</p>
    </div>
  );
}

export default function KakaoCallbackPage() {
  return (
    <Suspense fallback={
      <div className="flex flex-col items-center justify-center min-h-[400px]">
        <Loader2 className="w-12 h-12 text-primary-600 animate-spin mb-4" />
        <p className="text-slate-600">로딩 중...</p>
      </div>
    }>
      <KakaoCallbackContent />
    </Suspense>
  );
}
