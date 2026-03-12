'use client';

/**
 * 플랜 변경 확인 다이얼로그
 */

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { subscriptionApi } from '@/lib/api/subscription';
import type { PlanInfo, PlanChangeResult } from '@/types/subscription';

interface PlanChangeDialogProps {
  isOpen: boolean;
  onClose: () => void;
  currentPlan: string;
  targetPlan: PlanInfo;
  onSuccess: (result: PlanChangeResult) => void;
}

const PLAN_LABELS: Record<string, string> = {
  starter: '스타터',
  basic: '베이직',
  standard: '스탠다드',
  premium: '프리미엄',
};

export function PlanChangeDialog({
  isOpen,
  onClose,
  currentPlan,
  targetPlan,
  onSuccess,
}: PlanChangeDialogProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const isUpgrade = getOrder(targetPlan.id) > getOrder(currentPlan);

  const handleConfirm = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await subscriptionApi.changePlan(targetPlan.id);
      onSuccess(result);
      onClose();
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { error?: { message?: string } } } };
      setError(axiosErr.response?.data?.error?.message || '플랜 변경에 실패했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50" onClick={onClose}>
      <div
        className="w-full max-w-md rounded-xl bg-white p-6 shadow-lg"
        onClick={(e) => e.stopPropagation()}
      >
        <h3 className="mb-2 text-lg font-bold text-slate-900">
          플랜 {isUpgrade ? '업그레이드' : '다운그레이드'}
        </h3>
        <p className="mb-4 text-sm text-slate-500">
          {PLAN_LABELS[currentPlan]} → {PLAN_LABELS[targetPlan.id]} 플랜으로 변경합니다.
        </p>

        <div className="mb-4 rounded-lg bg-slate-50 p-4">
          <div className="flex items-center justify-between text-sm">
            <span className="text-slate-600">변경 후 월 요금</span>
            <span className="text-lg font-bold text-slate-900">
              ₩{targetPlan.price.toLocaleString()}/월
            </span>
          </div>
          {isUpgrade && (
            <p className="mt-2 text-xs text-slate-400">
              일할 차액이 즉시 결제됩니다.
            </p>
          )}
        </div>

        {error && (
          <p className="mb-4 rounded-lg bg-red-50 p-3 text-sm text-red-600">{error}</p>
        )}

        <div className="flex gap-2">
          <Button variant="outline" className="flex-1" onClick={onClose} disabled={isLoading}>
            취소
          </Button>
          <Button className="flex-1 bg-blue-600 hover:bg-blue-700" onClick={handleConfirm} disabled={isLoading}>
            {isLoading ? '처리 중...' : '변경하기'}
          </Button>
        </div>
      </div>
    </div>
  );
}

function getOrder(plan: string): number {
  const order: Record<string, number> = { starter: 0, basic: 1, standard: 2, premium: 3 };
  return order[plan] ?? 0;
}
