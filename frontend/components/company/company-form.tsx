'use client';

/**
 * 사업장 등록/수정 폼 컴포넌트
 * react-hook-form + zod 검증
 */

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useRouter } from 'next/navigation';
import { useState } from 'react';
import { Building2, Phone, MapPin, Users, AlertCircle, CheckCircle, Loader2 } from 'lucide-react';
import { companyApi } from '@/lib/api/company';
import type { Company, CreateCompanyRequest, UpdateCompanyRequest, IndustryType } from '@/types/company';
import { INDUSTRY_OPTIONS } from '@/types/company';
import { companyStore } from '@/lib/stores/company-store';
import { authStore } from '@/lib/stores/auth-store';

// 사업자등록번호 정규식
const businessNumberRegex = /^\d{3}-\d{2}-\d{5}$/;

// 사업장 등록 스키마
const companySchema = z.object({
  business_name: z
    .string()
    .min(1, '사업장명을 입력해주세요')
    .max(200, '사업장명은 200자 이내로 입력해주세요'),
  business_number: z
    .string()
    .min(1, '사업자등록번호를 입력해주세요')
    .regex(businessNumberRegex, '사업자등록번호 형식이 올바르지 않습니다. (xxx-xx-xxxxx)'),
  representative_name: z
    .string()
    .min(1, '대표자명을 입력해주세요')
    .max(100, '대표자명은 100자 이내로 입력해주세요'),
  industry_type: z.enum(['manufacturing', 'food_service', 'retail', 'service', 'it', 'construction', 'healthcare', 'other'], {
    required_error: '업종을 선택해주세요',
  }),
  employee_count: z
    .number({
      required_error: '직원 수를 입력해주세요',
      invalid_type_error: '직원 수는 숫자로 입력해주세요',
    })
    .int('직원 수는 정수로 입력해주세요')
    .min(0, '직원 수는 0 이상이어야 합니다')
    .max(1000, '직원 수는 1000 이하여야 합니다'),
  address: z.string().max(500, '주소는 500자 이내로 입력해주세요').optional(),
  postal_code: z.string().optional(),
  phone: z.string().optional(),
});

type CompanyFormValues = z.infer<typeof companySchema>;

interface CompanyFormProps {
  company?: Company;
  mode?: 'create' | 'edit';
  onSuccess?: () => void;
}

export function CompanyForm({ company, mode = 'create', onSuccess }: CompanyFormProps) {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [workRuleNotice, setWorkRuleNotice] = useState(false);

  const isEditMode = mode === 'edit' && company;

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<CompanyFormValues>({
    resolver: zodResolver(companySchema),
    defaultValues: company
      ? {
          business_name: company.business_name,
          business_number: company.business_number,
          representative_name: company.representative_name,
          industry_type: company.industry_type,
          employee_count: company.employee_count,
          address: company.address || '',
          postal_code: company.postal_code || '',
          phone: company.phone || '',
        }
      : {
          business_name: '',
          business_number: '',
          representative_name: '',
          industry_type: 'it',
          employee_count: 0,
          address: '',
          postal_code: '',
          phone: '',
        },
  });

  const employeeCount = watch('employee_count');
  const businessNumber = watch('business_number');

  // 직원 수 변경 시 취업규칙 의무 확인
  const showWorkRuleNotice = employeeCount >= 10;

  // 사업자등록번호 자동 포맷팅
  const handleBusinessNumberChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value.replace(/\D/g, '');
    let formatted = '';

    if (value.length > 0) {
      if (value.length <= 3) {
        formatted = value;
      } else if (value.length <= 5) {
        formatted = `${value.slice(0, 3)}-${value.slice(3)}`;
      } else {
        formatted = `${value.slice(0, 3)}-${value.slice(3, 5)}-${value.slice(5, 10)}`;
      }
    }

    setValue('business_number', formatted);
  };

  // 전화번호 자동 포맷팅
  const handlePhoneChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value.replace(/\D/g, '');
    let formatted = '';

    if (value.length > 0) {
      if (value.length <= 3) {
        formatted = value;
      } else if (value.length <= 7) {
        formatted = `${value.slice(0, 3)}-${value.slice(3)}`;
      } else {
        formatted = `${value.slice(0, 3)}-${value.slice(3, 7)}-${value.slice(7, 11)}`;
      }
    }

    setValue('phone', formatted);
  };

  const onSubmit = async (data: CompanyFormValues) => {
    setIsLoading(true);
    setError(null);

    try {
      if (isEditMode && company) {
        // 수정 모드
        const updateData: UpdateCompanyRequest = {
          business_name: data.business_name,
          representative_name: data.representative_name,
          industry_type: data.industry_type,
          employee_count: data.employee_count,
          address: data.address || undefined,
          postal_code: data.postal_code || undefined,
          phone: data.phone || undefined,
        };

        const updatedCompany = await companyApi.updateCompany(company.id, updateData);

        // 스토어 업데이트
        companyStore.getState().updateCompany(company.id, updatedCompany);

        // 이전 직원 수가 10 미만이었고, 현재 10 이상인 경우 취업규칙 안내 표시
        if (!company.work_rule_required && updatedCompany.work_rule_required) {
          setWorkRuleNotice(true);
        } else if (onSuccess) {
          onSuccess();
        } else {
          router.push(`/company/${company.id}`);
        }
      } else {
        // 등록 모드
        const createData: CreateCompanyRequest = {
          business_name: data.business_name,
          business_number: data.business_number,
          representative_name: data.representative_name,
          industry_type: data.industry_type,
          employee_count: data.employee_count,
          address: data.address || undefined,
          postal_code: data.postal_code || undefined,
          phone: data.phone || undefined,
        };

        const newCompany = await companyApi.createCompany(createData);

        // 스토어에 추가
        companyStore.getState().addCompany(newCompany);
        companyStore.getState().setCurrentCompany(newCompany);

        // 사용자 정보 업데이트
        authStore.getState().updateUser({ company_id: newCompany.id });

        // 10인 이상인 경우 취업규칙 안내 표시
        if (newCompany.work_rule_required) {
          setWorkRuleNotice(true);
        } else if (onSuccess) {
          onSuccess();
        } else {
          router.push('/dashboard');
        }
      }
    } catch (err: any) {
      // API 에러 처리
      const errorCode = err.response?.data?.code;
      const errorMessage = err.response?.data?.detail || err.message || '요청에 실패했습니다';

      if (errorCode === 'E-4002') {
        setError('이미 등록된 사업자등록번호입니다.');
      } else if (errorCode === 'E-4003') {
        setError('사업자등록번호 형식이 올바르지 않습니다.');
      } else if (errorCode === 'E-1001') {
        setError('입력값을 확인해주세요.');
      } else {
        setError(errorMessage);
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-5">
        {/* 전체 에러 메시지 */}
        {error && (
          <div
            data-testid="error-message"
            className="p-3 bg-error-50 border border-error-200 rounded-lg text-error-700 text-sm flex items-start gap-2"
          >
            <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        {/* 사업장명 */}
        <div className="flex flex-col gap-1">
          <label htmlFor="business_name" className="text-sm font-medium text-slate-700">
            사업장명 <span className="text-error-600">*</span>
          </label>
          <div className="relative">
            <Building2 className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
            <input
              id="business_name"
              type="text"
              placeholder="예: 노무닥터 주식회사"
              {...register('business_name')}
              disabled={isLoading}
              className={`
                w-full pl-10 pr-3 py-2.5
                border rounded-lg
                text-slate-900 placeholder-slate-400
                focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent
                disabled:bg-slate-100 disabled:text-slate-500 disabled:cursor-not-allowed
                transition-shadow duration-200
                ${errors.business_name ? 'border-error-500' : 'border-slate-300'}
              `}
              aria-describedby={errors.business_name ? 'business_name-error' : undefined}
            />
          </div>
          {errors.business_name && (
            <p
              id="business_name-error"
              data-testid="business_name-error"
              className="text-sm text-error-600"
            >
              {errors.business_name.message}
            </p>
          )}
        </div>

        {/* 사업자등록번호 */}
        <div className="flex flex-col gap-1">
          <label htmlFor="business_number" className="text-sm font-medium text-slate-700">
            사업자등록번호 <span className="text-error-600">*</span>
          </label>
          <input
            id="business_number"
            type="text"
            placeholder="xxx-xx-xxxxx"
            {...register('business_number', {
              onChange: handleBusinessNumberChange,
            })}
            disabled={isLoading || isEditMode === true}
            maxLength={12}
            className={`
              w-full px-3 py-2.5
              border rounded-lg
              text-slate-900 placeholder-slate-400
              font-mono tracking-wide
              focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent
              disabled:bg-slate-100 disabled:text-slate-500 disabled:cursor-not-allowed
              transition-shadow duration-200
              ${errors.business_number ? 'border-error-500' : 'border-slate-300'}
            `}
            aria-describedby={errors.business_number ? 'business_number-error' : undefined}
          />
          {errors.business_number && (
            <p
              id="business_number-error"
              data-testid="business_number-error"
              className="text-sm text-error-600"
            >
              {errors.business_number.message}
            </p>
          )}
        </div>

        {/* 대표자명 */}
        <div className="flex flex-col gap-1">
          <label htmlFor="representative_name" className="text-sm font-medium text-slate-700">
            대표자명 <span className="text-error-600">*</span>
          </label>
          <input
            id="representative_name"
            type="text"
            placeholder="예: 홍길동"
            {...register('representative_name')}
            disabled={isLoading}
            className={`
              w-full px-3 py-2.5
              border rounded-lg
              text-slate-900 placeholder-slate-400
              focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent
              disabled:bg-slate-100 disabled:text-slate-500 disabled:cursor-not-allowed
              transition-shadow duration-200
              ${errors.representative_name ? 'border-error-500' : 'border-slate-300'}
            `}
            aria-describedby={errors.representative_name ? 'representative_name-error' : undefined}
          />
          {errors.representative_name && (
            <p
              id="representative_name-error"
              data-testid="representative_name-error"
              className="text-sm text-error-600"
            >
              {errors.representative_name.message}
            </p>
          )}
        </div>

        {/* 업종 */}
        <div className="flex flex-col gap-1">
          <label htmlFor="industry_type" className="text-sm font-medium text-slate-700">
            업종 <span className="text-error-600">*</span>
          </label>
          <select
            id="industry_type"
            {...register('industry_type', { valueAsNumber: false })}
            disabled={isLoading}
            className={`
              w-full px-3 py-2.5
              border rounded-lg
              text-slate-900 bg-white
              focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent
              disabled:bg-slate-100 disabled:text-slate-500 disabled:cursor-not-allowed
              transition-shadow duration-200
              ${errors.industry_type ? 'border-error-500' : 'border-slate-300'}
            `}
            aria-describedby={errors.industry_type ? 'industry_type-error' : undefined}
          >
            <option value="">업종을 선택해주세요</option>
            {INDUSTRY_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          {errors.industry_type && (
            <p
              id="industry_type-error"
              data-testid="industry_type-error"
              className="text-sm text-error-600"
            >
              {errors.industry_type.message}
            </p>
          )}
        </div>

        {/* 직원 수 */}
        <div className="flex flex-col gap-1">
          <label htmlFor="employee_count" className="text-sm font-medium text-slate-700">
            직원 수 <span className="text-error-600">*</span>
          </label>
          <div className="relative">
            <Users className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
            <input
              id="employee_count"
              type="number"
              placeholder="0"
              min="0"
              max="1000"
              {...register('employee_count', { valueAsNumber: true })}
              disabled={isLoading}
              className={`
                w-full pl-10 pr-3 py-2.5
                border rounded-lg
                text-slate-900 placeholder-slate-400
                focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent
                disabled:bg-slate-100 disabled:text-slate-500 disabled:cursor-not-allowed
                transition-shadow duration-200
                ${errors.employee_count ? 'border-error-500' : 'border-slate-300'}
              `}
              aria-describedby={errors.employee_count ? 'employee_count-error' : undefined}
            />
          </div>
          {errors.employee_count && (
            <p
              id="employee_count-error"
              data-testid="employee_count-error"
              className="text-sm text-error-600"
            >
              {errors.employee_count.message}
            </p>
          )}
          {/* 취업규칙 의무 안내 (실시간) */}
          {showWorkRuleNotice && !errors.employee_count && (
            <div className="mt-1 flex items-start gap-2 text-xs text-warning-700">
              <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
              <span>10인 이상 사업장은 취업규칙 작성이 의무입니다.</span>
            </div>
          )}
        </div>

        {/* 주소 */}
        <div className="flex flex-col gap-1">
          <label htmlFor="address" className="text-sm font-medium text-slate-700">
            주소
          </label>
          <div className="relative">
            <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
            <input
              id="address"
              type="text"
              placeholder="예: 서울특별시 강남구 테헤란로 123"
              {...register('address')}
              disabled={isLoading}
              className={`
                w-full pl-10 pr-3 py-2.5
                border rounded-lg
                text-slate-900 placeholder-slate-400
                focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent
                disabled:bg-slate-100 disabled:text-slate-500 disabled:cursor-not-allowed
                transition-shadow duration-200
                ${errors.address ? 'border-error-500' : 'border-slate-300'}
              `}
              aria-describedby={errors.address ? 'address-error' : undefined}
            />
          </div>
          {errors.address && (
            <p
              id="address-error"
              data-testid="address-error"
              className="text-sm text-error-600"
            >
              {errors.address.message}
            </p>
          )}
        </div>

        {/* 우편번호와 전화번호 (2열 레이아웃) */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* 우편번호 */}
          <div className="flex flex-col gap-1">
            <label htmlFor="postal_code" className="text-sm font-medium text-slate-700">
              우편번호
            </label>
            <input
              id="postal_code"
              type="text"
              placeholder="예: 06123"
              {...register('postal_code')}
              disabled={isLoading}
              className={`
                w-full px-3 py-2.5
                border rounded-lg
                text-slate-900 placeholder-slate-400
                focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent
                disabled:bg-slate-100 disabled:text-slate-500 disabled:cursor-not-allowed
                transition-shadow duration-200
                ${errors.postal_code ? 'border-error-500' : 'border-slate-300'}
              `}
            />
            {errors.postal_code && (
              <p
                id="postal_code-error"
                data-testid="postal_code-error"
                className="text-sm text-error-600"
              >
                {errors.postal_code.message}
              </p>
            )}
          </div>

          {/* 전화번호 */}
          <div className="flex flex-col gap-1">
            <label htmlFor="phone" className="text-sm font-medium text-slate-700">
              대표 전화번호
            </label>
            <div className="relative">
              <Phone className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
              <input
                id="phone"
                type="text"
                placeholder="예: 02-1234-5678"
                {...register('phone', {
                  onChange: handlePhoneChange,
                })}
                disabled={isLoading}
                maxLength={13}
                className={`
                  w-full pl-10 pr-3 py-2.5
                  border rounded-lg
                  text-slate-900 placeholder-slate-400
                  focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent
                  disabled:bg-slate-100 disabled:text-slate-500 disabled:cursor-not-allowed
                  transition-shadow duration-200
                  ${errors.phone ? 'border-error-500' : 'border-slate-300'}
                `}
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
        </div>

        {/* 제출 버튼 */}
        <button
          type="submit"
          disabled={isLoading}
          className="
            w-full py-3
            bg-primary-600 hover:bg-primary-700 active:bg-primary-800
            text-white font-semibold
            rounded-lg
            transition-colors duration-200
            disabled:bg-slate-300 disabled:cursor-not-allowed
            flex items-center justify-center gap-2
          "
        >
          {isLoading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              {isEditMode ? '수정 중...' : '등록 중...'}
            </>
          ) : (
            <>
              <CheckCircle className="w-5 h-5" />
              {isEditMode ? '사업장 정보 수정' : '사업장 등록'}
            </>
          )}
        </button>
      </form>

      {/* 취업규칙 의무 안내 모달 */}
      {workRuleNotice && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" />
          <div className="relative bg-white rounded-2xl shadow-xl max-w-md w-full mx-4 p-6 animate-in fade-in slide-in-from-bottom-4">
            <div className="flex items-start gap-3 mb-4">
              <div className="p-2 bg-warning-100 rounded-lg">
                <AlertCircle className="w-6 h-6 text-warning-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-slate-900">
                  취업규칙 작성 안내
                </h3>
                <p className="text-sm text-slate-600 mt-2">
                  10인 이상 사업장은 근로기준법에 따라 취업규칙 작성이 의무입니다.
                  노무닥터를 통해 쉽게 작성할 수 있습니다.
                </p>
              </div>
            </div>
            <div className="flex gap-3 mt-6">
              <button
                type="button"
                onClick={() => setWorkRuleNotice(false)}
                className="flex-1 px-4 py-2 text-slate-700 hover:bg-slate-100 rounded-lg font-medium transition-colors duration-200"
              >
                나중에 하기
              </button>
              <button
                type="button"
                onClick={() => {
                  setWorkRuleNotice(false);
                  router.push('/work-rules/new');
                }}
                className="flex-1 px-4 py-2 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 transition-colors duration-200"
              >
                취업규칙 작성
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
