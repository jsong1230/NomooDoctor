'use client';

/**
 * 현재 구독 정보 및 사용량 카드
 */

import { Button } from '@/components/ui/button';
import type { Subscription, UsageInfo } from '@/types/subscription';

interface SubscriptionInfoProps {
  subscription: Subscription | null;
  usage: UsageInfo;
  onChangePlan: () => void;
  onCancel: () => void;
}

const PLAN_LABELS: Record<string, string> = {
  starter: '스타터 (무료)',
  basic: '베이직',
  standard: '스탠다드',
  premium: '프리미엄',
};

const STATUS_LABELS: Record<string, { text: string; color: string }> = {
  active: { text: '활성', color: 'bg-green-100 text-green-700' },
  cancelled: { text: '해지 예정', color: 'bg-yellow-100 text-yellow-700' },
  paused: { text: '일시정지', color: 'bg-red-100 text-red-700' },
  expired: { text: '만료', color: 'bg-slate-100 text-slate-600' },
};

function UsageBar({ used, limit, label }: { used: number; limit: number | null; label: string }) {
  const percentage = limit ? Math.min((used / limit) * 100, 100) : 0;
  const isUnlimited = limit === null;

  return (
    <div>
      <div className="mb-1 flex items-center justify-between text-sm">
        <span className="text-slate-600">{label}</span>
        <span className="font-medium text-slate-900">
          {used}{isUnlimited ? '' : ` / ${limit}`}
          {isUnlimited && <span className="ml-1 text-xs text-slate-400">(무제한)</span>}
        </span>
      </div>
      {!isUnlimited && (
        <div className="h-2 overflow-hidden rounded-full bg-slate-100">
          <div
            className={`h-full rounded-full transition-all ${
              percentage >= 90 ? 'bg-red-500' : percentage >= 70 ? 'bg-yellow-500' : 'bg-blue-500'
            }`}
            style={{ width: `${percentage}%` }}
          />
        </div>
      )}
    </div>
  );
}

export function SubscriptionInfo({
  subscription,
  usage,
  onChangePlan,
  onCancel,
}: SubscriptionInfoProps) {
  const statusInfo = subscription
    ? STATUS_LABELS[subscription.status] || { text: subscription.status, color: 'bg-slate-100 text-slate-600' }
    : null;

  return (
    <div className="space-y-6">
      {/* 구독 상태 카드 */}
      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="mb-4 flex items-center justify-between">
          <h3 className="text-lg font-bold text-slate-900">현재 구독</h3>
          {statusInfo && (
            <span className={`rounded-full px-3 py-1 text-xs font-medium ${statusInfo.color}`}>
              {statusInfo.text}
            </span>
          )}
        </div>

        {subscription ? (
          <div className="space-y-3">
            <div className="flex items-baseline justify-between">
              <span className="text-2xl font-bold text-slate-900">
                {PLAN_LABELS[subscription.plan] || subscription.plan}
              </span>
              <span className="text-lg font-semibold text-slate-700">
                ₩{subscription.monthly_amount.toLocaleString()}/월
              </span>
            </div>

            <div className="grid grid-cols-2 gap-3 text-sm text-slate-500">
              <div>
                <span className="block text-xs text-slate-400">시작일</span>
                {new Date(subscription.starts_at).toLocaleDateString('ko-KR')}
              </div>
              <div>
                <span className="block text-xs text-slate-400">다음 결제일</span>
                {subscription.expires_at
                  ? new Date(subscription.expires_at).toLocaleDateString('ko-KR')
                  : '-'}
              </div>
            </div>

            {subscription.cancelled_at && (
              <p className="mt-2 rounded-lg bg-yellow-50 p-3 text-sm text-yellow-700">
                해지 예정 — {subscription.expires_at
                  ? `${new Date(subscription.expires_at).toLocaleDateString('ko-KR')}까지 이용 가능`
                  : '곧 만료 예정'}
              </p>
            )}

            <div className="flex gap-2 pt-2">
              <Button variant="outline" size="sm" onClick={onChangePlan}>
                플랜 변경
              </Button>
              {subscription.status === 'active' && !subscription.cancelled_at && (
                <Button variant="ghost" size="sm" className="text-red-600 hover:text-red-700" onClick={onCancel}>
                  구독 해지
                </Button>
              )}
            </div>
          </div>
        ) : (
          <div className="text-center py-4">
            <p className="text-slate-500 mb-3">현재 무료 플랜(스타터)을 사용 중입니다.</p>
            <Button onClick={onChangePlan}>유료 플랜 살펴보기</Button>
          </div>
        )}
      </div>

      {/* 사용량 카드 */}
      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h3 className="mb-4 text-lg font-bold text-slate-900">
          이번 달 사용량
          <span className="ml-2 text-sm font-normal text-slate-400">{usage.month}</span>
        </h3>
        <div className="space-y-4">
          <UsageBar used={usage.chat_count} limit={usage.chat_limit} label="AI 상담" />
          <UsageBar used={usage.contract_count} limit={usage.contract_limit} label="계약서 생성" />
          <UsageBar used={usage.payslip_send_count} limit={usage.payslip_send_limit} label="급여명세서 발송" />
        </div>
      </div>
    </div>
  );
}
