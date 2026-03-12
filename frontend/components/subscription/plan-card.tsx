'use client';

/**
 * 플랜 카드 컴포넌트
 * 각 플랜의 가격, 기능, 선택 버튼을 표시합니다.
 */

import { Button } from '@/components/ui/button';
import type { PlanInfo } from '@/types/subscription';

interface PlanCardProps {
  plan: PlanInfo;
  currentPlan?: string;
  onSelect: (planId: string) => void;
  isLoading?: boolean;
}

const PLAN_LABELS: Record<string, string> = {
  starter: '스타터',
  basic: '베이직',
  standard: '스탠다드',
  premium: '프리미엄',
};

const PLAN_DESCRIPTIONS: Record<string, string> = {
  starter: '서비스를 체험해보세요',
  basic: '소규모 사업장에 적합',
  standard: '성장하는 사업장에 추천',
  premium: '모든 기능을 제한 없이',
};

function formatLimit(value: number | null): string {
  if (value === null) return '무제한';
  return `${value}회/월`;
}

export function PlanCard({ plan, currentPlan, onSelect, isLoading }: PlanCardProps) {
  const isCurrent = currentPlan === plan.id;
  const isPopular = plan.id === 'standard';

  return (
    <div
      className={`relative flex flex-col rounded-xl border p-6 ${
        isPopular
          ? 'border-blue-500 ring-2 ring-blue-500'
          : 'border-slate-200'
      } bg-white shadow-sm`}
    >
      {isPopular && (
        <div className="absolute -top-3 left-1/2 -translate-x-1/2">
          <span className="rounded-full bg-blue-600 px-3 py-1 text-xs font-semibold text-white">
            추천
          </span>
        </div>
      )}

      <div className="mb-4">
        <h3 className="text-lg font-bold text-slate-900">
          {PLAN_LABELS[plan.id] || plan.name}
        </h3>
        <p className="mt-1 text-sm text-slate-500">
          {PLAN_DESCRIPTIONS[plan.id]}
        </p>
      </div>

      <div className="mb-6">
        <span className="text-3xl font-bold text-slate-900">
          {plan.price === 0 ? '무료' : `₩${plan.price.toLocaleString()}`}
        </span>
        {plan.price > 0 && (
          <span className="text-sm text-slate-500">/월</span>
        )}
      </div>

      <ul className="mb-6 flex-1 space-y-3 text-sm">
        <li className="flex items-center gap-2">
          <CheckIcon />
          <span>AI 상담 {formatLimit(plan.features.chat_limit)}</span>
        </li>
        <li className="flex items-center gap-2">
          <CheckIcon />
          <span>계약서 {formatLimit(plan.features.contract_limit)}</span>
        </li>
        <li className="flex items-center gap-2">
          {plan.features.payroll ? <CheckIcon /> : <XIcon />}
          <span className={plan.features.payroll ? '' : 'text-slate-400'}>
            급여 관리
          </span>
        </li>
        <li className="flex items-center gap-2">
          {(plan.features.payslip_send_limit ?? 0) > 0 ? <CheckIcon /> : <XIcon />}
          <span className={(plan.features.payslip_send_limit ?? 0) > 0 ? '' : 'text-slate-400'}>
            급여명세서 {plan.features.payslip_send_limit
              ? formatLimit(plan.features.payslip_send_limit)
              : '미지원'}
          </span>
        </li>
        <li className="flex items-center gap-2">
          {plan.features.attorney_consult ? <CheckIcon /> : <XIcon />}
          <span className={plan.features.attorney_consult ? '' : 'text-slate-400'}>
            노무사 상담 {plan.features.attorney_consult
              ? formatLimit(plan.features.attorney_consult_limit)
              : '미지원'}
          </span>
        </li>
      </ul>

      <Button
        onClick={() => onSelect(plan.id)}
        disabled={isCurrent || isLoading}
        variant={isPopular ? 'default' : 'outline'}
        className={`w-full ${isPopular ? 'bg-blue-600 hover:bg-blue-700' : ''}`}
      >
        {isCurrent ? '현재 플랜' : plan.price === 0 ? '무료로 시작' : '구독하기'}
      </Button>
    </div>
  );
}

function CheckIcon() {
  return (
    <svg className="h-4 w-4 shrink-0 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
    </svg>
  );
}

function XIcon() {
  return (
    <svg className="h-4 w-4 shrink-0 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
    </svg>
  );
}
