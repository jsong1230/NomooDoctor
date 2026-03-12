'use client';

/**
 * 구독 관리 클라이언트 컴포넌트
 */

import { useEffect, useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { PlanCard } from '@/components/subscription/plan-card';
import { SubscriptionInfo } from '@/components/subscription/subscription-info';
import { PaymentHistory } from '@/components/subscription/payment-history';
import { PlanChangeDialog } from '@/components/subscription/plan-change-dialog';
import { CancelDialog } from '@/components/subscription/cancel-dialog';
import { subscriptionApi } from '@/lib/api/subscription';
import { subscriptionStore } from '@/lib/stores/subscription-store';
import { authStore } from '@/lib/stores/auth-store';
import type { PlanInfo, MySubscriptionData, PlanChangeResult, CancelResult } from '@/types/subscription';

export function SubscriptionClient() {
  const [plans, setPlans] = useState<PlanInfo[]>([]);
  const [myData, setMyData] = useState<MySubscriptionData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('overview');

  // 다이얼로그 상태
  const [changePlanTarget, setChangePlanTarget] = useState<PlanInfo | null>(null);
  const [showCancel, setShowCancel] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const isAuthenticated = authStore((s) => s.isAuthenticated);
  const { setSubscription, setUsage, setPlans: setStorePlans } = subscriptionStore();

  // 데이터 로드
  useEffect(() => {
    const load = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const plansData = await subscriptionApi.getPlans();
        setPlans(plansData);
        setStorePlans(plansData);

        if (isAuthenticated) {
          const subData = await subscriptionApi.getMySubscription();
          setMyData(subData);
          setSubscription(subData.subscription);
          setUsage(subData.usage);
        }
      } catch {
        setError('데이터를 불러올 수 없습니다.');
      } finally {
        setIsLoading(false);
      }
    };
    load();
  }, [isAuthenticated, setSubscription, setUsage, setStorePlans]);

  const handlePlanSelect = async (planId: string) => {
    const currentPlan = myData?.subscription?.plan || 'starter';

    if (planId === currentPlan) return;

    // 유료 → 다른 유료: 플랜 변경 다이얼로그
    if (myData?.subscription) {
      const target = plans.find((p) => p.id === planId);
      if (target) setChangePlanTarget(target);
      return;
    }

    // 무료 → 유료: 구독 생성 (mock billing key)
    if (planId === 'starter') return;

    try {
      setIsLoading(true);
      const billingKey = `tb_${crypto.randomUUID()}`;
      await subscriptionApi.createSubscription(planId, billingKey);
      // 구독 생성 후 다시 로드
      const subData = await subscriptionApi.getMySubscription();
      setMyData(subData);
      setSubscription(subData.subscription);
      setUsage(subData.usage);
      setSuccessMessage('구독이 시작되었습니다!');
      setActiveTab('overview');
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { error?: { message?: string } } } };
      setError(axiosErr.response?.data?.error?.message || '구독 생성에 실패했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  const handlePlanChanged = async (result: PlanChangeResult) => {
    setChangePlanTarget(null);
    setSuccessMessage(`${result.old_plan} → ${result.new_plan} 플랜으로 변경되었습니다.`);
    setTimeout(() => setSuccessMessage(null), 3000);
    // 데이터 새로고침
    const subData = await subscriptionApi.getMySubscription();
    setMyData(subData);
    setSubscription(subData.subscription);
    setUsage(subData.usage);
  };

  const handleCancelled = async (result: CancelResult) => {
    setShowCancel(false);
    setSuccessMessage(result.message);
    setTimeout(() => setSuccessMessage(null), 5000);
    const subData = await subscriptionApi.getMySubscription();
    setMyData(subData);
    setSubscription(subData.subscription);
    setUsage(subData.usage);
  };

  if (isLoading && !myData) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="mx-auto max-w-5xl px-4 py-8">
        {/* 헤더 */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900">구독 관리</h1>
          <p className="mt-1 text-slate-500">플랜을 선택하고 구독을 관리하세요.</p>
        </div>

        {/* 알림 메시지 */}
        {successMessage && (
          <div className="mb-6 rounded-lg bg-green-50 border border-green-200 p-4 text-sm text-green-700">
            {successMessage}
          </div>
        )}
        {error && (
          <div className="mb-6 rounded-lg bg-red-50 border border-red-200 p-4 text-sm text-red-600">
            {error}
          </div>
        )}

        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="mb-6">
            <TabsTrigger value="overview">구독 현황</TabsTrigger>
            <TabsTrigger value="plans">플랜 비교</TabsTrigger>
            <TabsTrigger value="history">결제 내역</TabsTrigger>
          </TabsList>

          {/* 구독 현황 탭 */}
          <TabsContent value="overview">
            {myData ? (
              <SubscriptionInfo
                subscription={myData.subscription}
                usage={myData.usage}
                onChangePlan={() => setActiveTab('plans')}
                onCancel={() => setShowCancel(true)}
              />
            ) : (
              <div className="rounded-xl border border-slate-200 bg-white p-8 text-center shadow-sm">
                <p className="text-slate-500">로그인 후 구독 정보를 확인할 수 있습니다.</p>
              </div>
            )}
          </TabsContent>

          {/* 플랜 비교 탭 */}
          <TabsContent value="plans">
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {plans.map((plan) => (
                <PlanCard
                  key={plan.id}
                  plan={plan}
                  currentPlan={myData?.subscription?.plan || 'starter'}
                  onSelect={handlePlanSelect}
                  isLoading={isLoading}
                />
              ))}
            </div>
          </TabsContent>

          {/* 결제 내역 탭 */}
          <TabsContent value="history">
            <PaymentHistory />
          </TabsContent>
        </Tabs>

        {/* 플랜 변경 다이얼로그 */}
        {changePlanTarget && myData?.subscription && (
          <PlanChangeDialog
            isOpen={!!changePlanTarget}
            onClose={() => setChangePlanTarget(null)}
            currentPlan={myData.subscription.plan}
            targetPlan={changePlanTarget}
            onSuccess={handlePlanChanged}
          />
        )}

        {/* 구독 해지 다이얼로그 */}
        <CancelDialog
          isOpen={showCancel}
          onClose={() => setShowCancel(false)}
          onSuccess={handleCancelled}
        />
      </div>
    </div>
  );
}
