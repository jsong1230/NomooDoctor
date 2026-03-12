'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft, Star, MapPin, Briefcase, CheckCircle, MessageSquare } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { CaseForm } from '@/components/attorney/case-form';
import { attorneyApi } from '@/lib/api/attorney';
import { authStore } from '@/lib/stores/auth-store';
import type { AttorneyDetail, Review } from '@/types/attorney';
import { CASE_TYPE_LABELS, type CaseType } from '@/types/attorney';

interface AttorneyDetailClientProps {
  attorneyId: string;
}

export function AttorneyDetailClient({ attorneyId }: AttorneyDetailClientProps) {
  const router = useRouter();
  const [data, setData] = useState<AttorneyDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [showCaseForm, setShowCaseForm] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const isAuthenticated = authStore((s) => s.isAuthenticated);

  useEffect(() => {
    const load = async () => {
      try {
        const detail = await attorneyApi.getAttorney(attorneyId);
        setData(detail);
      } catch {
        // not found
      } finally {
        setIsLoading(false);
      }
    };
    load();
  }, [attorneyId]);

  const handleCaseSuccess = () => {
    setShowCaseForm(false);
    setSuccessMessage('상담 신청이 완료되었습니다!');
    setTimeout(() => setSuccessMessage(null), 3000);
  };

  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent" />
      </div>
    );
  }

  if (!data) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-8 text-center">
        <p className="text-slate-500">노무사를 찾을 수 없습니다.</p>
        <Button variant="link" onClick={() => router.push('/attorneys')}>
          목록으로 돌아가기
        </Button>
      </div>
    );
  }

  const { attorney, recent_reviews } = data;

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="mx-auto max-w-4xl px-4 py-8">
        {/* 뒤로가기 */}
        <Button
          variant="ghost"
          size="sm"
          className="mb-4"
          onClick={() => router.push('/attorneys')}
        >
          <ArrowLeft className="h-4 w-4 mr-1" />
          목록으로
        </Button>

        {/* 알림 */}
        {successMessage && (
          <div className="mb-6 rounded-lg bg-green-50 border border-green-200 p-4 text-sm text-green-700">
            {successMessage}
          </div>
        )}

        {/* 프로필 카드 */}
        <Card className="mb-6">
          <CardContent className="p-6">
            <div className="flex items-start gap-5">
              <div className="h-20 w-20 shrink-0 rounded-full bg-slate-200 flex items-center justify-center text-2xl font-bold text-slate-500">
                {attorney.name.charAt(0)}
              </div>

              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <h1 className="text-2xl font-bold text-slate-900">{attorney.name}</h1>
                  {attorney.verified && (
                    <CheckCircle className="h-5 w-5 text-blue-500" />
                  )}
                </div>
                <p className="text-slate-500">{attorney.firm_name}</p>

                <div className="mt-3 flex flex-wrap gap-4 text-sm text-slate-600">
                  <span className="flex items-center gap-1">
                    <Star className="h-4 w-4 text-amber-400 fill-amber-400" />
                    {attorney.rating.toFixed(1)} ({attorney.review_count}개 리뷰)
                  </span>
                  <span className="flex items-center gap-1">
                    <Briefcase className="h-4 w-4" />
                    경력 {attorney.experience_years}년
                  </span>
                  <span className="flex items-center gap-1">
                    <MapPin className="h-4 w-4" />
                    {attorney.regions.join(', ')}
                  </span>
                  <span className="flex items-center gap-1">
                    <MessageSquare className="h-4 w-4" />
                    응답률 {attorney.response_rate}%
                  </span>
                </div>

                {/* 전문분야 */}
                <div className="mt-3 flex flex-wrap gap-1.5">
                  {attorney.specialties.map((s) => (
                    <Badge key={s} variant="secondary">
                      {CASE_TYPE_LABELS[s as CaseType] || s}
                    </Badge>
                  ))}
                </div>
              </div>

              {/* 상담료 + CTA */}
              <div className="shrink-0 text-right">
                <p className="text-2xl font-bold text-slate-900">
                  {attorney.consultation_fee.toLocaleString()}원
                </p>
                <p className="text-xs text-slate-400 mb-3">상담료</p>
                {isAuthenticated && !showCaseForm && (
                  <Button onClick={() => setShowCaseForm(true)}>
                    상담 신청
                  </Button>
                )}
              </div>
            </div>

            {/* 소개 */}
            {attorney.bio && (
              <>
                <Separator className="my-5" />
                <div>
                  <h3 className="text-sm font-medium text-slate-500 mb-2">소개</h3>
                  <p className="text-slate-700 whitespace-pre-wrap">{attorney.bio}</p>
                </div>
              </>
            )}
          </CardContent>
        </Card>

        {/* 상담 신청 폼 */}
        {showCaseForm && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>상담 신청</CardTitle>
            </CardHeader>
            <CardContent>
              <CaseForm
                attorney={attorney}
                onSuccess={handleCaseSuccess}
                onCancel={() => setShowCaseForm(false)}
              />
            </CardContent>
          </Card>
        )}

        {/* 리뷰 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              리뷰
              <span className="text-sm font-normal text-slate-400">
                ({recent_reviews.length})
              </span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {recent_reviews.length === 0 ? (
              <p className="text-sm text-slate-400 text-center py-8">
                아직 리뷰가 없습니다.
              </p>
            ) : (
              <div className="space-y-4">
                {recent_reviews.map((review) => (
                  <ReviewItem key={review.id} review={review} />
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function ReviewItem({ review }: { review: Review }) {
  return (
    <div className="border-b border-slate-100 pb-4 last:border-0">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="flex">
            {[1, 2, 3, 4, 5].map((i) => (
              <Star
                key={i}
                className={`h-4 w-4 ${
                  i <= review.rating
                    ? 'text-amber-400 fill-amber-400'
                    : 'text-slate-200'
                }`}
              />
            ))}
          </div>
          <span className="text-sm font-medium text-slate-700">{review.user_name}</span>
        </div>
        <span className="text-xs text-slate-400">
          {new Date(review.created_at).toLocaleDateString('ko-KR')}
        </span>
      </div>
      {review.comment && (
        <p className="mt-2 text-sm text-slate-600">{review.comment}</p>
      )}
    </div>
  );
}
