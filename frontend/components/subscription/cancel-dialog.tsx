'use client';

/**
 * 구독 해지 확인 다이얼로그
 */

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { subscriptionApi } from '@/lib/api/subscription';
import type { CancelResult } from '@/types/subscription';

interface CancelDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (result: CancelResult) => void;
}

const REASONS = [
  '가격이 부담돼요',
  '사용 빈도가 낮아요',
  '필요한 기능이 없어요',
  '다른 서비스를 이용 중이에요',
  '기타',
];

export function CancelDialog({ isOpen, onClose, onSuccess }: CancelDialogProps) {
  const [reason, setReason] = useState('');
  const [feedback, setFeedback] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleConfirm = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await subscriptionApi.cancelSubscription(reason || undefined, feedback || undefined);
      onSuccess(result);
      onClose();
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { error?: { message?: string } } } };
      setError(axiosErr.response?.data?.error?.message || '구독 해지에 실패했습니다.');
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
        <h3 className="mb-2 text-lg font-bold text-slate-900">구독 해지</h3>
        <p className="mb-4 text-sm text-slate-500">
          해지하시면 현재 결제 기간이 끝날 때까지 서비스를 이용하실 수 있습니다.
        </p>

        <div className="mb-4">
          <label className="mb-2 block text-sm font-medium text-slate-700">
            해지 사유
          </label>
          <div className="space-y-2">
            {REASONS.map((r) => (
              <label key={r} className="flex items-center gap-2 text-sm">
                <input
                  type="radio"
                  name="reason"
                  value={r}
                  checked={reason === r}
                  onChange={(e) => setReason(e.target.value)}
                  className="text-blue-600"
                />
                {r}
              </label>
            ))}
          </div>
        </div>

        <div className="mb-4">
          <label className="mb-2 block text-sm font-medium text-slate-700">
            추가 의견 (선택)
          </label>
          <textarea
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            className="w-full rounded-lg border border-slate-200 p-3 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            rows={3}
            placeholder="서비스 개선에 도움이 됩니다..."
          />
        </div>

        {error && (
          <p className="mb-4 rounded-lg bg-red-50 p-3 text-sm text-red-600">{error}</p>
        )}

        <div className="flex gap-2">
          <Button variant="outline" className="flex-1" onClick={onClose} disabled={isLoading}>
            돌아가기
          </Button>
          <Button
            variant="destructive"
            className="flex-1"
            onClick={handleConfirm}
            disabled={isLoading}
          >
            {isLoading ? '처리 중...' : '해지하기'}
          </Button>
        </div>
      </div>
    </div>
  );
}
