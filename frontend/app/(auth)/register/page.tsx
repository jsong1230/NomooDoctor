'use client';

/**
 * 회원가입 페이지
 * 이름/이메일/비밀번호/전화번호 입력 폼
 */

import { RegisterForm } from '@/components/auth/register-form';
import Link from 'next/link';

export default function RegisterPage() {
  return (
    <div className="flex flex-col">
      {/* 페이지 제목 */}
      <div className="text-center mb-6">
        <h2 className="text-2xl font-semibold text-slate-900">
          계정 만들기
        </h2>
        <p className="text-sm text-slate-600 mt-1">
          노무닥터와 함께 편리한 인사관리를 시작하세요
        </p>
      </div>

      {/* 회원가입 폼 */}
      <RegisterForm />

      {/* 구분선 */}
      <div className="relative my-6">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-slate-200" />
        </div>
        <div className="relative flex justify-center text-xs uppercase">
          <span className="bg-white px-2 text-slate-500">또는</span>
        </div>
      </div>

      {/* 카카오 OAuth 회원가입 버튼 */}
      <button
        type="button"
        data-testid="kakao-login-button"
        onClick={() => {
          // 카카오 OAuth 로그인 시작 (신규 회원일 경우 회원가입 처리)
          window.location.href = '/api/v1/auth/kakao';
        }}
        className="
          w-full py-3
          bg-[#FEE500] hover:bg-[#FFE000]
          text-slate-900 font-semibold
          rounded-lg
          transition-colors duration-200
          flex items-center justify-center gap-2
        "
      >
        <svg
          width="20"
          height="20"
          viewBox="0 0 20 20"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M10 0C4.48 0 0 3.58 0 8C0 11.24 2.65 14.28 6.33 15.41C6.61 15.49 6.71 15.35 6.71 15.23C6.71 15.12 6.7 14.75 6.7 14.24C4.22 14.78 3.88 13.15 3.88 13.15C3.62 12.44 3.24 12.3 3.24 12.3C2.71 11.75 3.28 11.76 3.28 11.76C3.86 11.8 4.18 12.36 4.18 12.36C4.69 13.22 5.52 12.97 5.87 12.83C5.92 12.43 6.07 12.16 6.23 12.02C4.54 11.88 2.77 11.24 2.77 8C2.77 7.08 3.1 6.33 3.65 5.74C3.59 5.6 3.29 4.73 3.77 3.56C3.77 3.56 4.48 3.33 6.7 4.42C7.37 4.29 8.07 4.23 8.77 4.23C9.47 4.23 10.17 4.29 10.84 4.42C13.06 3.33 13.77 3.56 13.77 3.56C14.25 4.73 13.95 5.6 13.89 5.74C14.44 6.33 14.77 7.08 14.77 8C14.77 11.25 13 11.88 11.3 12.02C11.5 12.19 11.68 12.52 11.68 13.04C11.68 13.79 11.67 14.4 11.67 15.23C11.67 15.35 11.77 15.49 12.05 15.41C15.73 14.28 18.38 11.24 18.38 8C18.38 3.58 13.9 0 8.38 0H10Z"
            fill="#1E1E1E"
          />
        </svg>
        카카오로 계정 만들기
      </button>

      {/* 약관 링크 */}
      <div className="text-center mt-6 space-x-2 text-xs text-slate-500">
        <Link href="/terms" className="hover:underline">
          이용약관
        </Link>
        <span>·</span>
        <Link href="/privacy" className="hover:underline">
          개인정보처리방침
        </Link>
      </div>
    </div>
  );
}
