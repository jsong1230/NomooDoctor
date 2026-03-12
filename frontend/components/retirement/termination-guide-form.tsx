'use client';

/**
 * 해고 절차 가이드 요청 폼 컴포넌트
 * 해고/퇴직 유형, 사유, 위험 요소 입력
 */

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { AlertCircle, Loader2, CheckCircle2 } from 'lucide-react';
import { generateTerminationGuide } from '@/lib/api/retirement';
import { retirementStore } from '@/lib/stores/retirement-store';
import { RiskWarningBanner } from './risk-warning-banner';
import { TerminationChecklist } from './termination-checklist';
import { TERMINATION_TYPE_OPTIONS, RISK_LEVEL_COLOR_MAP } from '@/types/retirement';
import type { TerminationGuideRequest, ChecklistItem, RiskFactors } from '@/types/retirement';

// 유효성 검증 스키마
const terminationGuideSchema = z.object({
  employee_id: z.string().min(1, '직원을 선택해주세요'),
  termination_type: z.enum(['resignation', 'mutual_agreement', 'dismissal', 'contract_expiry', 'retirement'], {
    errorMap: () => ({ message: '해고/퇴직 유형을 선택해주세요' }),
  }),
  reason: z.string().min(1, '사유를 입력해주세요').max(500, '사유는 500자 이내로 입력해주세요'),
  is_pregnant: z.boolean().default(false),
  is_on_parental_leave: z.boolean().default(false),
  is_union_member: z.boolean().default(false),
  is_workplace_injury: z.boolean().default(false),
  is_whistleblower: z.boolean().default(false),
});

type TerminationGuideFormValues = z.infer<typeof terminationGuideSchema>;

interface TerminationGuideFormProps {
  employees?: Array<{ id: string; name: string }>;
  onGenerated?: () => void;
}

export function TerminationGuideForm({
  employees = [],
  onGenerated
}: TerminationGuideFormProps) {
  const {
    terminationGuide,
    isGeneratingGuide,
    guideError,
    setTerminationGuide,
    setIsGeneratingGuide,
    setGuideError,
  } = retirementStore();

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting },
    reset,
  } = useForm<TerminationGuideFormValues>({
    resolver: zodResolver(terminationGuideSchema),
    defaultValues: {
      employee_id: '',
      termination_type: 'dismissal',
      reason: '',
      is_pregnant: false,
      is_on_parental_leave: false,
      is_union_member: false,
      is_workplace_injury: false,
      is_whistleblower: false,
    },
  });

  const riskFactors = watch([
    'is_pregnant',
    'is_on_parental_leave',
    'is_union_member',
    'is_workplace_injury',
    'is_whistleblower',
  ]);

  const hasRisk = riskFactors.some(factor => factor === true);

  // 해고 절차 가이드 생성
  const onSubmit = async (values: TerminationGuideFormValues) => {
    setIsGeneratingGuide(true);
    setGuideError(null);

    try {
      const request: TerminationGuideRequest = {
        employee_id: values.employee_id,
        termination_type: values.termination_type,
        reason: values.reason,
        risk_factors: {
          is_pregnant: values.is_pregnant,
          is_on_parental_leave: values.is_on_parental_leave,
          is_union_member: values.is_union_member,
          is_workplace_injury: values.is_workplace_injury,
          is_whistleblower: values.is_whistleblower,
        },
      };

      const guide = await generateTerminationGuide(request);
      setTerminationGuide(guide);
      onGenerated?.();
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : '가이드 생성 중 오류가 발생했습니다.';
      setGuideError(errorMessage);
    } finally {
      setIsGeneratingGuide(false);
    }
  };

  // 새로운 가이드 생성
  const handleNewGuide = () => {
    reset();
    setTerminationGuide(null);
    setGuideError(null);
  };

  // 가이드 생성 완료 후 상태 표시
  if (terminationGuide) {
    return (
      <div className="space-y-6">
        {/* 위험도 배지 */}
        <div className={`rounded-lg p-6 ${RISK_LEVEL_COLOR_MAP[terminationGuide.risk_level]}`}>
          <h3 className="font-semibold mb-2">위험도: {terminationGuide.risk_level}</h3>
          <p className="text-sm">
            {terminationGuide.risk_level === 'EMERGENCY'
              ? '긴급 주의가 필요합니다. 반드시 노무사와 상담하세요.'
              : terminationGuide.risk_level === 'HIGH'
              ? '높은 위험도입니다. 전문가 상담을 권장합니다.'
              : terminationGuide.risk_level === 'MEDIUM'
              ? '주의가 필요합니다. 체크리스트를 반드시 확인하세요.'
              : '일반적인 절차를 따르면 됩니다.'}
          </p>
        </div>

        {/* 위험 경고 */}
        {terminationGuide.risk_warnings.length > 0 && (
          <div>
            <h3 className="font-semibold text-gray-900 mb-3">위험 경고</h3>
            <RiskWarningBanner
              warnings={terminationGuide.risk_warnings}
              riskLevel={terminationGuide.risk_level}
            />
          </div>
        )}

        {/* 해고 예고 정보 */}
        {terminationGuide.advance_notice.required && (
          <div className="border border-blue-200 rounded-lg p-4 bg-blue-50">
            <h3 className="font-semibold text-blue-900 mb-2">해고 예고 필수 사항</h3>
            <div className="space-y-2 text-sm text-blue-800">
              <p>
                <span className="font-medium">예고 기간:</span> {terminationGuide.advance_notice.notice_days}일
              </p>
              <p>
                <span className="font-medium">예고 수당:</span>{' '}
                {terminationGuide.advance_notice.notice_pay_amount.toLocaleString('ko-KR')}원
              </p>
              <p className="mt-2">{terminationGuide.advance_notice.description}</p>
            </div>
          </div>
        )}

        {/* 체크리스트 */}
        <div>
          <h3 className="font-semibold text-gray-900 mb-3">진행 절차</h3>
          <TerminationChecklist
            items={terminationGuide.checklist}
            readonly={true}
          />
        </div>

        {/* 필요 서류 */}
        <div>
          <h3 className="font-semibold text-gray-900 mb-3">준비 서류</h3>
          <div className="grid gap-2">
            {terminationGuide.documents.map((doc, index) => (
              <div
                key={index}
                className="flex items-center gap-2 p-3 border border-gray-200 rounded-lg"
              >
                <CheckCircle2 className={`w-5 h-5 flex-shrink-0 ${
                  doc.available ? 'text-green-600' : 'text-gray-400'
                }`} />
                <span className={doc.available ? 'text-gray-900 font-medium' : 'text-gray-500'}>
                  {doc.name}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* 실업급여 정보 */}
        {terminationGuide.unemployment_benefit_guide.eligible && (
          <div className="border border-green-200 rounded-lg p-4 bg-green-50">
            <h3 className="font-semibold text-green-900 mb-2">실업급여 수급 가능</h3>
            <div className="space-y-2 text-sm text-green-800">
              <p>{terminationGuide.unemployment_benefit_guide.conditions}</p>
              <p className="font-medium">필요 서류:</p>
              <ul className="list-disc list-inside">
                {terminationGuide.unemployment_benefit_guide.required_documents.map((doc, idx) => (
                  <li key={idx}>{doc}</li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {/* AI 상세 가이드 */}
        <div className="border border-gray-200 rounded-lg p-4 bg-gray-50">
          <h3 className="font-semibold text-gray-900 mb-2">상세 가이드</h3>
          <div className="prose prose-sm max-w-none">
            <p className="text-gray-700 whitespace-pre-wrap text-sm">
              {terminationGuide.ai_guide}
            </p>
          </div>
        </div>

        {/* 법률 참조 */}
        {terminationGuide.law_references.length > 0 && (
          <div className="border border-gray-200 rounded-lg p-4">
            <h3 className="font-semibold text-gray-900 mb-3">참조 법률</h3>
            <div className="space-y-3">
              {terminationGuide.law_references.map((ref, index) => (
                <div key={index} className="border-l-4 border-gray-300 pl-4 py-2">
                  <p className="font-medium text-gray-900">
                    {ref.law_name} {ref.article}
                  </p>
                  <p className="text-sm text-gray-600 mt-1">{ref.content}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 면책 문구 */}
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p className="text-xs text-yellow-800">{terminationGuide.disclaimer}</p>
        </div>

        {/* 새로운 가이드 생성 버튼 */}
        <button
          onClick={handleNewGuide}
          className="w-full px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
        >
          새로운 절차 가이드 생성
        </button>
      </div>
    );
  }

  // 가이드 요청 폼
  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {/* 오류 메시지 */}
      {guideError && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex gap-2">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-medium text-red-900">오류</p>
            <p className="text-sm text-red-700">{guideError}</p>
          </div>
        </div>
      )}

      {/* 직원 선택 */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          직원 <span className="text-red-600">*</span>
        </label>
        <select
          {...register('employee_id')}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">직원을 선택해주세요</option>
          {employees.map(emp => (
            <option key={emp.id} value={emp.id}>
              {emp.name}
            </option>
          ))}
        </select>
        {errors.employee_id && (
          <p className="text-red-600 text-sm mt-1">{errors.employee_id.message}</p>
        )}
      </div>

      {/* 해고/퇴직 유형 */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          해고/퇴직 유형 <span className="text-red-600">*</span>
        </label>
        <select
          {...register('termination_type')}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          {TERMINATION_TYPE_OPTIONS.map(option => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        {errors.termination_type && (
          <p className="text-red-600 text-sm mt-1">{errors.termination_type.message}</p>
        )}
      </div>

      {/* 사유 */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          해고/퇴직 사유 <span className="text-red-600">*</span>
        </label>
        <textarea
          {...register('reason')}
          placeholder="상세한 사유를 입력해주세요"
          rows={4}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        {errors.reason && (
          <p className="text-red-600 text-sm mt-1">{errors.reason.message}</p>
        )}
      </div>

      {/* 위험 요소 체크 */}
      <div className="border border-yellow-200 bg-yellow-50 rounded-lg p-4">
        <h3 className="font-semibold text-yellow-900 mb-4">위험 요소 확인</h3>
        <div className="space-y-3">
          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              {...register('is_pregnant')}
              className="w-4 h-4 rounded border-gray-300"
            />
            <span className="text-sm text-yellow-900">임신 중</span>
          </label>

          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              {...register('is_on_parental_leave')}
              className="w-4 h-4 rounded border-gray-300"
            />
            <span className="text-sm text-yellow-900">육아휴직 중</span>
          </label>

          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              {...register('is_union_member')}
              className="w-4 h-4 rounded border-gray-300"
            />
            <span className="text-sm text-yellow-900">노조원</span>
          </label>

          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              {...register('is_workplace_injury')}
              className="w-4 h-4 rounded border-gray-300"
            />
            <span className="text-sm text-yellow-900">산업재해 중</span>
          </label>

          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              {...register('is_whistleblower')}
              className="w-4 h-4 rounded border-gray-300"
            />
            <span className="text-sm text-yellow-900">내부 고발자</span>
          </label>
        </div>

        {hasRisk && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded text-sm text-red-700">
            위험 요소가 감지되었습니다. 반드시 노무사와 상담하세요.
          </div>
        )}
      </div>

      {/* 생성 버튼 */}
      <button
        type="submit"
        disabled={isSubmitting || isGeneratingGuide}
        className="w-full px-4 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:bg-blue-400 transition flex justify-center items-center gap-2"
      >
        {isGeneratingGuide ? (
          <>
            <Loader2 className="w-4 h-4 animate-spin" />
            생성 중...
          </>
        ) : (
          '절차 가이드 생성'
        )}
      </button>
    </form>
  );
}
