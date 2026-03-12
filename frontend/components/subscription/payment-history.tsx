'use client';

/**
 * 결제 내역 테이블 컴포넌트
 */

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { subscriptionApi } from '@/lib/api/subscription';
import type { PaymentHistoryItem, PaginationMeta } from '@/types/subscription';

const STATUS_MAP: Record<string, { text: string; color: string }> = {
  done: { text: '완료', color: 'text-green-600' },
  success: { text: '완료', color: 'text-green-600' },
  failed: { text: '실패', color: 'text-red-600' },
  pending: { text: '대기', color: 'text-yellow-600' },
  cancelled: { text: '취소', color: 'text-slate-500' },
};

export function PaymentHistory() {
  const [payments, setPayments] = useState<PaymentHistoryItem[]>([]);
  const [pagination, setPagination] = useState<PaginationMeta | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadPayments = async (cursor?: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await subscriptionApi.getPaymentHistory({ limit: 10, cursor });
      if (cursor) {
        setPayments((prev) => [...prev, ...data.payments]);
      } else {
        setPayments(data.payments);
      }
      setPagination(data.pagination);
    } catch {
      setError('결제 내역을 불러올 수 없습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadPayments();
  }, []);

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <h3 className="mb-4 text-lg font-bold text-slate-900">결제 내역</h3>

      {error && (
        <p className="mb-4 rounded-lg bg-red-50 p-3 text-sm text-red-600">{error}</p>
      )}

      {payments.length === 0 && !isLoading ? (
        <p className="py-8 text-center text-sm text-slate-400">결제 내역이 없습니다.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-100 text-left text-slate-500">
                <th className="pb-3 font-medium">결제일</th>
                <th className="pb-3 font-medium">금액</th>
                <th className="pb-3 font-medium">결제수단</th>
                <th className="pb-3 font-medium">상태</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50">
              {payments.map((p) => {
                const st = STATUS_MAP[p.status] || { text: p.status, color: 'text-slate-500' };
                return (
                  <tr key={p.id}>
                    <td className="py-3 text-slate-700">
                      {p.paid_at
                        ? new Date(p.paid_at).toLocaleDateString('ko-KR')
                        : '-'}
                    </td>
                    <td className="py-3 font-medium text-slate-900">
                      ₩{p.amount.toLocaleString()}
                    </td>
                    <td className="py-3 text-slate-600">
                      {p.payment_method || '-'}
                    </td>
                    <td className={`py-3 font-medium ${st.color}`}>
                      {st.text}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {pagination?.has_next && (
        <div className="mt-4 text-center">
          <Button
            variant="outline"
            size="sm"
            onClick={() => loadPayments(pagination.cursor ?? undefined)}
            disabled={isLoading}
          >
            {isLoading ? '로딩 중...' : '더 보기'}
          </Button>
        </div>
      )}
    </div>
  );
}
