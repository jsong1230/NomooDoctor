'use client';

/**
 * 회원가입 폼 컴포넌트
 * react-hook-form + zod 검증
 */

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useRouter } from 'next/navigation';
import { useState } from 'react';
import { Mail, Lock, User, Phone, Loader2 } from 'lucide-react';
import { authStore } from '@/lib/stores/auth-store';
import { authApi } from '@/lib/api/auth';
import type { RegisterRequest } from '@/types/auth';

// 비밀번호 정책: 8자 이상, 영문 대소문자/숫자/특수문자 중 3가지 이상 조합
const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)|(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*])|(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*])|(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*]).{8,}$/;

// 회원가입 스키마
const registerSchema = z.object({
  email: z
    .string()
    .min(1, '이메일을 입력해주세요')
    .email('유효한 이메일 형식이 아닙니다'),
  password: z
    .string()
    .min(8, '비밀번호는 8자 이상이어야 합니다')
    .regex(
      passwordRegex,
      '비밀번호는 영문 대소문자, 숫자, 특수문자 중 3가지 이상을 조합해야 합니다'
    ),
  name: z
    .string()
    .min(1, '이름을 입력해주세요')
    .min(2, '이름은 2자 이상이어야 합니다')
    .max(100, '이름은 100자 이하여야 합니다'),
  phone: z
    .string()
    .optional()
    .refine(
      (val) => !val || /^010-\d{4}-\d{4}$/.test(val),
      '전화번호 형식이 올바르지 않습니다 (예: 010-1234-5678)'
    ),
});

type RegisterFormValues = z.infer<typeof registerSchema>;

interface RegisterFormProps {
  onSuccess?: () => void;
}

export function RegisterForm({ onSuccess }: RegisterFormProps) {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      email: '',
      password: '',
      name: '',
      phone: '',
    },
  });

  const onSubmit = async (data: RegisterFormValues) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await authApi.register(data as RegisterRequest);

      // 스토어에 저장
      authStore.getState().login(
        response.user,
        response.tokens.access_token,
        response.tokens.refresh_token
      );

      // 성공 콜백 또는 사업장 등록 페이지로 이동
      if (onSuccess) {
        onSuccess();
      } else {
        router.push('/company/new');
      }
    } catch (err: any) {
      // API 에러 처리
      const errorCode = err.response?.data?.code;
      const errorMessage = err.response?.data?.detail || err.message || '회원가입에 실패했습니다';

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

      {/* 이름 입력 */}
      <div className="flex flex-col gap-1">
        <label htmlFor="name" className="text-sm font-medium text-slate-700">
          이름
        </label>
        <div className="relative">
          <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
          <input
            id="name"
            type="text"
            placeholder="홍길동"
            {...register('name')}
            disabled={isLoading}
            className={`
              w-full pl-10 pr-3 py-2.5
              border rounded-lg
              text-slate-900 placeholder-slate-400
              focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent
              disabled:bg-slate-100 disabled:text-slate-500 disabled:cursor-not-allowed
              transition-shadow duration-200
              ${errors.name ? 'border-error-500' : 'border-slate-300'}
            `}
            aria-describedby={errors.name ? 'name-error' : undefined}
          />
        </div>
        {errors.name && (
          <p
            id="name-error"
            data-testid="name-error"
            className="text-sm text-error-600"
          >
            {errors.name.message}
          </p>
        )}
      </div>

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
            onBlur={(e) => {
              // 즉시 이메일 검증을 위한 blur 이벤트 핸들러
              if (e.target.value) {
                register('email').onBlur(e);
              }
            }}
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

      {/* 전화번호 입력 */}
      <div className="flex flex-col gap-1">
        <label htmlFor="phone" className="text-sm font-medium text-slate-700">
          전화번호 (선택)
        </label>
        <div className="relative">
          <Phone className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
          <input
            id="phone"
            type="tel"
            placeholder="010-1234-5678"
            {...register('phone')}
            disabled={isLoading}
            className={`
              w-full pl-10 pr-3 py-2.5
              border rounded-lg
              text-slate-900 placeholder-slate-400
              focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent
              disabled:bg-slate-100 disabled:text-slate-500 disabled:cursor-not-allowed
              transition-shadow duration-200
              ${errors.phone ? 'border-error-500' : 'border-slate-300'}
            `}
            aria-describedby={errors.phone ? 'phone-error' : undefined}
          />
        </div>
        {errors.phone && (
          <p
            id="phone-error"
            data-testid="phone-error"
            className="text-sm text-error-600"
          >
            {errors.phone.message}
          </p>
        )}
      </div>

      {/* 비밀번호 입력 */}
      <div className="flex flex-col gap-1">
        <label htmlFor="password" className="text-sm font-medium text-slate-700">
          비밀번호
        </label>
        <div className="relative">
          <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
          <input
            id="password"
            type="password"
            placeholder="8자 이상, 영문/숫자/특수문자 조합"
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
        <p className="text-xs text-slate-500">
          비밀번호는 8자 이상이며, 영문 대소문자, 숫자, 특수문자 중 3가지 이상을 조합해야 합니다.
        </p>
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
            가입 중...
          </>
        ) : (
          '회원가입'
        )}
      </button>

      {/* 로그인 링크 */}
      <p className="text-center text-sm text-slate-600">
        이미 계정이 있으신가요?{' '}
        <a href="/login" className="text-primary-600 hover:text-primary-700 font-medium">
          로그인
        </a>
      </p>
    </form>
  );
}
