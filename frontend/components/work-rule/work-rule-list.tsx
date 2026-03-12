'use client';

/**
 * 취업규칙 목록 컴포넌트
 * 취업규칙 목록 조회 및 새로 작성 버튼
 */

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { useRouter } from 'next/navigation';
import { TemplateSelector } from './template-selector';
import type { WorkRuleListItem, IndustryType } from '@/types/work-rule';
import { getIndustryLabel, getStatusLabel, STATUS_LABELS } from '@/types/work-rule';
import { workRuleStore } from '@/lib/stores/work-rule-store';
import { formatDistanceToNow } from 'date-fns';
import { ko } from 'date-fns/locale';
import { Plus, FileText, Clock } from 'lucide-react';

interface WorkRuleListProps {
  companyId: string;
}

export function WorkRuleList({ companyId }: WorkRuleListProps) {
  const router = useRouter();
  const { workRules, isLoading, fetchWorkRules, createWorkRule } = workRuleStore();
  const [templateSelectorOpen, setTemplateSelectorOpen] = useState(false);
  const [creatingWorkRule, setCreatingWorkRule] = useState(false);

  useEffect(() => {
    fetchWorkRules({ per_page: 20 });
  }, [fetchWorkRules]);

  const handleCreateWorkRule = async (industryType: IndustryType) => {
    setCreatingWorkRule(true);
    try {
      const newRule = await createWorkRule({
        industry_type: industryType,
      });
      router.push(`/work-rules/${newRule.id}`);
    } catch (error) {
      console.error('취업규칙 생성 실패:', error);
    } finally {
      setCreatingWorkRule(false);
    }
  };

  const getStatusBadgeVariant = (status: string): 'default' | 'secondary' | 'destructive' | 'outline' => {
    switch (status) {
      case 'draft':
        return 'outline';
      case 'under_review':
        return 'secondary';
      case 'active':
        return 'default';
      case 'superseded':
        return 'destructive';
      default:
        return 'outline';
    }
  };

  return (
    <>
      <div className="space-y-4">
        {/* 헤더 및 액션 */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">취업규칙 관리</h1>
            <p className="mt-2 text-muted-foreground">
              사업장의 취업규칙을 작성하고 관리합니다.
            </p>
          </div>
          <Button
            onClick={() => setTemplateSelectorOpen(true)}
            disabled={creatingWorkRule || isLoading}
            size="lg"
            className="gap-2"
          >
            <Plus className="h-4 w-4" />
            새로 작성
          </Button>
        </div>

        <Separator />

        {/* 취업규칙 목록 */}
        {isLoading ? (
          <div className="py-8 text-center text-muted-foreground">
            로드 중...
          </div>
        ) : workRules.length === 0 ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <FileText className="mb-4 h-12 w-12 text-muted-foreground/50" />
              <h3 className="font-semibold">아직 작성된 취업규칙이 없습니다.</h3>
              <p className="mt-1 text-sm text-muted-foreground">
                "새로 작성" 버튼을 클릭하여 취업규칙을 작성하세요.
              </p>
              <Button
                onClick={() => setTemplateSelectorOpen(true)}
                disabled={creatingWorkRule || isLoading}
                variant="outline"
                className="mt-4"
              >
                취업규칙 작성
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-3">
            {workRules.map((rule) => (
              <Link key={rule.id} href={`/work-rules/${rule.id}`}>
                <Card className="hover:bg-accent transition-colors cursor-pointer">
                  <CardContent className="py-4">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-3">
                          <h3 className="font-semibold">
                            V{rule.version} - {getIndustryLabel(rule.industry_type)}
                          </h3>
                          <Badge variant={getStatusBadgeVariant(rule.status)}>
                            {getStatusLabel(rule.status as keyof typeof STATUS_LABELS)}
                          </Badge>
                        </div>
                        <div className="mt-2 flex flex-wrap gap-4 text-sm text-muted-foreground">
                          {rule.effective_date && (
                            <div className="flex items-center gap-1">
                              <Clock className="h-4 w-4" />
                              <span>시행일: {rule.effective_date}</span>
                            </div>
                          )}
                          {rule.approval_date && (
                            <div>승인일: {rule.approval_date}</div>
                          )}
                          {rule.ai_generated && (
                            <Badge variant="secondary" className="text-xs">
                              AI 생성
                            </Badge>
                          )}
                        </div>
                        {rule.worker_consent_count !== undefined && (
                          <div className="mt-2 text-sm">
                            <span className="font-medium">
                              {rule.worker_consent_count}명 동의
                            </span>
                            <span className="ml-2 text-muted-foreground">
                              ({rule.worker_consent_count > 0 ? '동의 진행 중' : '미진행'})
                            </span>
                          </div>
                        )}
                      </div>
                      <div className="flex-shrink-0 text-right text-xs text-muted-foreground">
                        <div>
                          {formatDistanceToNow(new Date(rule.created_at), {
                            addSuffix: true,
                            locale: ko,
                          })}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        )}
      </div>

      {/* 템플릿 선택 모달 */}
      <TemplateSelector
        open={templateSelectorOpen}
        onOpenChange={setTemplateSelectorOpen}
        onSelect={handleCreateWorkRule}
        isLoading={creatingWorkRule}
      />
    </>
  );
}
