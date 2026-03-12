'use client';

/**
 * 취업규칙 상세/편집 페이지 - Client 컴포넌트
 */

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { WorkRuleEditor } from '@/components/work-rule/work-rule-editor';
import { ConsentChecklist } from '@/components/work-rule/consent-checklist';
import { workRuleStore } from '@/lib/stores/work-rule-store';
import { authStore } from '@/lib/stores/auth-store';
import { getIndustryLabel, getStatusLabel, STATUS_LABELS } from '@/types/work-rule';
import type { WorkRuleUpdate } from '@/types/work-rule';
import { ArrowLeft, Download, Zap, RefreshCw, Trash2 } from 'lucide-react';

interface WorkRuleDetailClientProps {
  workRuleId: string;
}

export function WorkRuleDetailClient({ workRuleId }: WorkRuleDetailClientProps) {
  const router = useRouter();
  const { user } = authStore();
  const { currentWorkRule, isLoading, fetchWorkRule, updateWorkRule, deleteWorkRule, generateAiDraft, reviseWorkRule } = workRuleStore();
  const [isReady, setIsReady] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  // 초기 로드
  useEffect(() => {
    if (!user?.company_id) {
      router.push('/company');
    } else {
      loadWorkRule();
      setIsReady(true);
    }
  }, [workRuleId, user?.company_id, router]);

  const loadWorkRule = async () => {
    try {
      await fetchWorkRule(workRuleId);
    } catch (error) {
      console.error('취업규칙 로드 실패:', error);
      router.push('/work-rules');
    }
  };

  const handleSave = async (content: any) => {
    setIsSaving(true);
    try {
      await updateWorkRule(workRuleId, {
        content,
      });
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = async () => {
    try {
      await deleteWorkRule(workRuleId);
      router.push('/work-rules');
    } finally {
      setShowDeleteConfirm(false);
    }
  };

  const handleGenerateAi = async () => {
    if (!currentWorkRule) return;
    try {
      await generateAiDraft(workRuleId, {
        industry_type: currentWorkRule.industry_type as any,
      });
    } catch (error) {
      console.error('AI 초안 생성 실패:', error);
    }
  };

  const handleRevise = async () => {
    if (!currentWorkRule) return;
    try {
      const newRule = await reviseWorkRule(workRuleId, {
        revision_reason: '취업규칙 개정',
      });
      router.push(`/work-rules/${newRule.id}`);
    } catch (error) {
      console.error('개정 실패:', error);
    }
  };

  if (!isReady || isLoading || !currentWorkRule) {
    return (
      <div className="flex items-center justify-center py-12 min-h-screen">
        로드 중...
      </div>
    );
  }

  const isEditable = currentWorkRule.status === 'draft' || currentWorkRule.status === 'under_review';

  return (
    <div className="min-h-screen bg-slate-50 px-4 py-8 sm:px-6 sm:py-12">
      <div className="mx-auto max-w-5xl space-y-6">
        {/* 뒤로가기 및 헤더 */}
        <div className="flex items-center gap-4">
          <Button
            onClick={() => router.back()}
            variant="outline"
            size="sm"
            className="gap-2"
          >
            <ArrowLeft className="h-4 w-4" />
            뒤로가기
          </Button>
          <h1 className="text-3xl font-bold tracking-tight">
            취업규칙 V{currentWorkRule.version}
          </h1>
          <Badge variant={currentWorkRule.status === 'active' ? 'default' : 'outline'}>
            {getStatusLabel(currentWorkRule.status)}
          </Badge>
        </div>

        <Separator />

        {/* 정보 카드 */}
        <Card>
          <CardHeader>
            <CardTitle>정보</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
              <div>
                <p className="text-sm text-muted-foreground">업종</p>
                <p className="font-semibold">{getIndustryLabel(currentWorkRule.industry_type)}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">상태</p>
                <p className="font-semibold">{getStatusLabel(currentWorkRule.status)}</p>
              </div>
              {currentWorkRule.effective_date && (
                <div>
                  <p className="text-sm text-muted-foreground">시행일</p>
                  <p className="font-semibold">{currentWorkRule.effective_date}</p>
                </div>
              )}
              {currentWorkRule.approval_date && (
                <div>
                  <p className="text-sm text-muted-foreground">승인일</p>
                  <p className="font-semibold">{currentWorkRule.approval_date}</p>
                </div>
              )}
            </div>
            {currentWorkRule.ai_generated && (
              <Badge variant="secondary">AI 생성됨</Badge>
            )}
          </CardContent>
        </Card>

        {/* 액션 바 */}
        <div className="flex flex-wrap gap-2">
          {isEditable && (
            <>
              <Button
                onClick={handleGenerateAi}
                variant="outline"
                className="gap-2"
              >
                <Zap className="h-4 w-4" />
                AI 초안 생성
              </Button>
              {currentWorkRule.status === 'active' && (
                <Button
                  onClick={handleRevise}
                  variant="outline"
                  className="gap-2"
                >
                  <RefreshCw className="h-4 w-4" />
                  개정
                </Button>
              )}
              {currentWorkRule.status === 'draft' && (
                <Button
                  onClick={() => setShowDeleteConfirm(true)}
                  variant="destructive"
                  size="sm"
                  className="gap-2"
                >
                  <Trash2 className="h-4 w-4" />
                  삭제
                </Button>
              )}
            </>
          )}
        </div>

        {/* 섹션 편집기 */}
        <WorkRuleEditor
          content={currentWorkRule.content}
          onSave={handleSave}
          isEditable={isEditable}
          isSaving={isSaving}
        />

        {/* 동의 절차 체크리스트 */}
        {currentWorkRule.status !== 'draft' && (
          <ConsentChecklist />
        )}

        {/* 삭제 확인 다이얼로그 */}
        {showDeleteConfirm && (
          <Card className="border-red-200 bg-red-50 dark:border-red-900 dark:bg-red-950">
            <CardContent className="pt-6">
              <p className="mb-4 text-sm text-red-900 dark:text-red-100">
                이 취업규칙을 삭제하시겠습니까? 이 작업은 취소할 수 없습니다.
              </p>
              <div className="flex gap-3">
                <Button
                  onClick={() => setShowDeleteConfirm(false)}
                  variant="outline"
                  size="sm"
                >
                  취소
                </Button>
                <Button
                  onClick={handleDelete}
                  variant="destructive"
                  size="sm"
                >
                  삭제
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
