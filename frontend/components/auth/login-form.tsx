'use client';

/**
 * 로그인 폼 컴포넌트
 * react-hook-form + zod 검증
 */

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useRouter } from 'next/navigation';
import { useState } from 'react';
import { Mail, Lock, Loader2 } from 'lucide-react';
import { authStore } from '@/lib/stores/auth-store';
import { authApi } from '@/lib/api/auth';
import type { LoginRequest } from '@/types/auth';

// 로그인 스키마
const loginSchema = z.object({
  email: z
    .string()
    .min(1, '이메일을 입력해주세요')
    .email('유효한 이메일 형식이 아닙니다'),
  password: z
    .string()
    .min(1, '비밀번호를 입력해주세요'),
});

type LoginFormValues = z.infer<typeof loginSchema>;

interface LoginFormProps {
  onSuccess?: () => void;
}

export function LoginForm({ onSuccess }: LoginFormProps) {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: '',
      password: '',
    },
  });

  const onSubmit = async (data: LoginFormValues) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await authApi.login(data as LoginRequest);

      // 스토어에 저장
      authStore.getState().login(
        response.user,
        response.tokens.access_token,
        response.tokens.refresh_token
      );

      // 성공 콜백 또는 대시보드로 이동
      if (onSuccess) {
        onSuccess();
      } else {
        router.push('/dashboard');
      }
    } catch (err: any) {
      // API 에러 처리
      const errorCode = err.response?.data?.code;
      const errorMessage = err.response?.data?.detail || err.message || '로그인에 실패했습니다';

      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4">
      {/* 전체 에러 메시지 */}
      {error && (
        <div
          data-testid="error-message"
          className="p-3 bg-error-50 border border-error-200 rounded-lg text-error-700 text-sm"
        >
          {error}
        </div>
      )}

      {/* 이메일 입력 */}
      <div className="flex flex-col gap-1">
        <label htmlFor="email" className="text-sm font-medium text-slate-700">
          이메일
        </label>
        <div className="relative">
          <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
          <input
            id="email"
            type="email"
            placeholder="example@company.com"
            {...register('email')}
            disabled={isLoading}
            className={`
              w-full pl-10 pr-3 py-2.5
              border rounded-lg
              text-slate-900 placeholder-slate-400
              focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent
              disabled:bg-slate-100 disabled:text-slate-500 disabled:cursor-not-allowed
              transition-shadow duration-200
              ${errors.email ? 'border-error-500' : 'border-slate-300'}
            `}
            aria-describedby={errors.email ? 'email-error' : undefined}
          />
        </div>
        {errors.email && (
          <p
            id="email-error"
            data-testid="email-error"
            className="text-sm text-error-600"
          >
            {errors.email.message}
          </p>
        )}
      </div>

      {/* 비밀번호 입력 */}
      <div className="flex flex-col gap-1">
        <div className="flex items-center justify-between">
          <label htmlFor="password" className="text-sm font-medium text-slate-700">
            비밀번호
          </label>
          <a
            href="/forgot-password"
            className="text-sm text-primary-600 hover:text-primary-700"
          >
            비밀번호 찾기
          </a>
        </div>
        <div className="relative">
          <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
          <input
            id="password"
            type="password"
            placeholder="비밀번호 입력"
            {...register('password')}
            disabled={isLoading}
            className={`
              w-full pl-10 pr-3 py-2.5
              border rounded-lg
              text-slate-900 placeholder-slate-400
              focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent
              disabled:bg-slate-100 disabled:text-slate-500 disabled:cursor-not-allowed
              transition-shadow duration-200
              ${errors.password ? 'border-error-500' : 'border-slate-300'}
            `}
            aria-describedby={errors.password ? 'password-error' : undefined}
          />
        </div>
        {errors.password && (
          <p
            id="password-error"
            data-testid="password-error"
            className="text-sm text-error-600"
          >
            {errors.password.message}
          </p>
        )}
      </div>

      {/* 제출 버튼 */}
      <button
        type="submit"
        disabled={isLoading}
        className={`
          w-full py-3
          bg-primary-600 hover:bg-primary-700 active:bg-primary-800
          text-white font-semibold
          rounded-lg
          transition-colors duration-200
          disabled:bg-slate-300 disabled:cursor-not-allowed
          flex items-center justify-center gap-2
        `}
      >
        {isLoading ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin" />
            로그인 중...
          </>
        ) : (
          '로그인'
        )}
      </button>

      {/* 회원가입 링크 */}
      <p className="text-center text-sm text-slate-600">
        계정이 없으신가요?{' '}
        <a href="/register" className="text-primary-600 hover:text-primary-700 font-medium">
          회원가입
        </a>
      </p>
    </form>
  );
}
