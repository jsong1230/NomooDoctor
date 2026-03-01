'use client';

/**
 * 비밀번호 찾기 페이지
 * 이메일 입력 후 재설정 링크 발송
 */

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useState } from 'react';
import { Mail, Loader2, CheckCircle, ArrowLeft } from 'lucide-react';
import { authApi } from '@/lib/api/auth';
import Link from 'next/link';

// 비밀번호 찾기 스키마
const forgotPasswordSchema = z.object({
  email: z
    .string()
    .min(1, '이메일을 입력해주세요')
    .email('유효한 이메일 형식이 아닙니다'),
});

type ForgotPasswordFormValues = z.infer<typeof forgotPasswordSchema>;

export default function ForgotPasswordPage() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isSuccess, setIsSuccess] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ForgotPasswordFormValues>({
    resolver: zodResolver(forgotPasswordSchema),
    defaultValues: {
      email: '',
    },
  });

  const onSubmit = async (data: ForgotPasswordFormValues) => {
    setIsLoading(true);
    setError(null);

    try {
      await authApi.requestPasswordReset({ email: data.email });
      setIsSuccess(true);
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || '요청에 실패했습니다';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col">
      {/* 뒤로가기 */}
      <Link
        href="/login"
        className="flex items-center gap-2 text-sm text-slate-600 hover:text-slate-900 mb-4"
      >
        <ArrowLeft className="w-4 h-4" />
        로그인으로 돌아가기
      </Link>

      {/* 페이지 제목 */}
      <div className="text-center mb-6">
        <h2 className="text-2xl font-semibold text-slate-900">
          비밀번호 찾기
        </h2>
        <p className="text-sm text-slate-600 mt-1">
          가입한 이메일을 입력하면 비밀번호 재설정 링크를 보내드립니다.
        </p>
      </div>

      {/* 전체 에러 메시지 */}
      {error && (
        <div
          data-testid="error-message"
          className="p-3 bg-error-50 border border-error-200 rounded-lg text-error-700 text-sm mb-4"
        >
          {error}
        </div>
      )}

      {/* 성공 메시지 */}
      {isSuccess ? (
        <div
          data-testid="success-message"
          className="p-4 bg-success-50 border border-success-200 rounded-lg text-center"
        >
          <CheckCircle className="w-12 h-12 text-success-600 mx-auto mb-2" />
          <h3 className="font-semibold text-slate-900 mb-1">
            이메일을 발송했습니다
          </h3>
          <p className="text-sm text-slate-600">
            비밀번호 재설정 링크가 이메일로 전송되었습니다.
            <br />
            이메일을 확인하여 비밀번호를 변경해주세요.
          </p>
          <div className="mt-4">
            <Link
              href="/login"
              className="inline-flex items-center gap-2 text-sm text-primary-600 hover:text-primary-700 font-medium"
            >
              <ArrowLeft className="w-4 h-4" />
              로그인 페이지로 이동
            </Link>
          </div>
        </div>
      ) : (
        <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4">
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
                전송 중...
              </>
            ) : (
              '비밀번호 재설정 링크 보내기'
            )}
          </button>
        </form>
      )}
    </div>
  );
}
