'use client';

/**
 * 동의 절차 체크리스트 컴포넌트
 * 근로자 과반수 동의 절차를 안내하는 체크리스트
 */

import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import type { ConsentChecklistResponse } from '@/types/work-rule';
import { workRuleApi } from '@/lib/api/work-rule';
import { CheckCircle2, Circle, AlertCircle } from 'lucide-react';

interface ConsentChecklistProps {
  compact?: boolean;
}

export function ConsentChecklist({ compact = false }: ConsentChecklistProps) {
  const [checklist, setChecklist] = useState<ConsentChecklistResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadChecklist();
  }, []);

  const loadChecklist = async () => {
    try {
      const data = await workRuleApi.getConsentChecklist();
      setChecklist(data);
    } catch (error) {
      console.error('체크리스트 로드 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="py-4 text-center text-muted-foreground">로드 중...</div>;
  }

  if (!checklist) {
    return null;
  }

  const { checklist: steps, employee_count, consent_threshold, consent_type } = checklist;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>근로자 동의 절차</span>
          <Badge variant="outline">
            {employee_count}명 ({consent_type === 'majority' ? '과반수' : '의견청취'})
          </Badge>
        </CardTitle>
        <CardDescription>
          {consent_type === 'majority'
            ? `전체 근로자 ${employee_count}명 중 최소 ${consent_threshold}명 이상의 동의가 필요합니다.`
            : `전체 근로자 ${employee_count}명의 의견을 청취해야 합니다.`}
        </CardDescription>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* 동의 임계값 진행률 */}
        {consent_type === 'majority' && (
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="font-medium">필요 동의율</span>
              <span className="text-muted-foreground">
                {Math.round((consent_threshold / employee_count) * 100)}%
              </span>
            </div>
            <Progress
              value={(consent_threshold / employee_count) * 100}
              className="h-2"
            />
          </div>
        )}

        {/* 체크리스트 스텝 */}
        <div className="space-y-4">
          {steps.map((step) => (
            <div key={step.step} className="flex gap-4">
              <div className="flex-shrink-0 pt-0.5">
                <Circle className="h-6 w-6 text-muted-foreground" />
              </div>
              <div className="flex-1 space-y-1">
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <h4 className="font-semibold">
                      {step.step}. {step.title}
                    </h4>
                    <p className="mt-1 text-sm text-muted-foreground">
                      {step.description}
                    </p>
                  </div>
                  {step.is_required && (
                    <Badge variant="destructive" className="flex-shrink-0">
                      필수
                    </Badge>
                  )}
                </div>
                {step.law_reference && (
                  <p className="text-xs text-primary">
                    {step.law_reference}
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* 주의사항 */}
        <div className="flex gap-3 rounded-lg bg-amber-50 p-3 dark:bg-amber-950">
          <AlertCircle className="h-5 w-5 flex-shrink-0 text-amber-600 dark:text-amber-500" />
          <div className="text-sm text-amber-900 dark:text-amber-100">
            <p className="font-semibold">주의: 불이익 변경의 경우</p>
            <p className="mt-1">
              근로시간 단축, 임금 감소 등 근로자에게 불리한 변경은 과반수 동의가 반드시 필요하며,
              합의하지 못한 경우 변경할 수 없습니다.
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
