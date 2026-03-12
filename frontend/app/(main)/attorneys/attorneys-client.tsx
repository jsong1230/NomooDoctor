'use client';

import { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { AttorneyList } from '@/components/attorney/attorney-list';
import { MyCases } from '@/components/attorney/my-cases';
import { ReviewForm } from '@/components/attorney/review-form';
import { authStore } from '@/lib/stores/auth-store';
import type { AttorneyCase } from '@/types/attorney';

export function AttorneysClient() {
  const [activeTab, setActiveTab] = useState('browse');
  const [reviewTarget, setReviewTarget] = useState<AttorneyCase | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const isAuthenticated = authStore((s) => s.isAuthenticated);

  const handleReview = (caseItem: AttorneyCase) => {
    setReviewTarget(caseItem);
  };

  const handleReviewSuccess = () => {
    setReviewTarget(null);
    setSuccessMessage('리뷰가 등록되었습니다.');
    setTimeout(() => setSuccessMessage(null), 3000);
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="mx-auto max-w-4xl px-4 py-8">
        {/* 헤더 */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900">노무사 마켓플레이스</h1>
          <p className="mt-1 text-slate-500">
            전문 노무사를 찾아 복잡한 노무 문제를 해결하세요.
          </p>
        </div>

        {/* 알림 */}
        {successMessage && (
          <div className="mb-6 rounded-lg bg-green-50 border border-green-200 p-4 text-sm text-green-700">
            {successMessage}
          </div>
        )}

        {/* 리뷰 작성 모드 */}
        {reviewTarget && (
          <div className="mb-6 rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="mb-4 text-lg font-semibold">리뷰 작성</h2>
            <ReviewForm
              caseId={reviewTarget.case_id}
              attorneyName={reviewTarget.attorney_name}
              onSuccess={handleReviewSuccess}
              onCancel={() => setReviewTarget(null)}
            />
          </div>
        )}

        {/* 탭 */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="mb-6">
            <TabsTrigger value="browse">노무사 찾기</TabsTrigger>
            {isAuthenticated && (
              <TabsTrigger value="my-cases">내 상담</TabsTrigger>
            )}
          </TabsList>

          <TabsContent value="browse">
            <AttorneyList />
          </TabsContent>

          {isAuthenticated && (
            <TabsContent value="my-cases">
              <MyCases onReview={handleReview} />
            </TabsContent>
          )}
        </Tabs>
      </div>
    </div>
  );
}
