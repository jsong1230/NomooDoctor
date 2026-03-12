'use client';

/**
 * 취업규칙 템플릿 선택 컴포넌트
 * 업종별 표준 템플릿을 선택하는 모달/드롭다운
 */

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import type { IndustryType, TemplateResponse } from '@/types/work-rule';
import { INDUSTRY_OPTIONS } from '@/types/work-rule';
import { workRuleApi } from '@/lib/api/work-rule';

interface TemplateSelectorProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSelect: (industryType: IndustryType) => Promise<void>;
  isLoading?: boolean;
}

export function TemplateSelector({
  open,
  onOpenChange,
  onSelect,
  isLoading = false,
}: TemplateSelectorProps) {
  const [templates, setTemplates] = useState<TemplateResponse[]>([]);
  const [loadingTemplates, setLoadingTemplates] = useState(false);
  const [selectedIndustry, setSelectedIndustry] = useState<IndustryType | null>(null);

  // 템플릿 로드
  useEffect(() => {
    if (open) {
      loadTemplates();
    }
  }, [open]);

  const loadTemplates = async () => {
    setLoadingTemplates(true);
    try {
      const data = await workRuleApi.getTemplates();
      setTemplates(data);
    } catch (error) {
      console.error('템플릿 로드 실패:', error);
    } finally {
      setLoadingTemplates(false);
    }
  };

  const handleSelect = async (industryType: IndustryType) => {
    setSelectedIndustry(industryType);
    try {
      await onSelect(industryType);
      onOpenChange(false);
    } catch (error) {
      console.error('템플릿 선택 실패:', error);
    } finally {
      setSelectedIndustry(null);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>템플릿 선택</DialogTitle>
          <DialogDescription>
            업종을 선택하면 해당 업종에 맞는 표준 취업규칙 템플릿이 적용됩니다.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {loadingTemplates ? (
            <div className="py-8 text-center text-muted-foreground">
              템플릿을 로드 중입니다...
            </div>
          ) : templates.length === 0 ? (
            <div className="py-8 text-center text-muted-foreground">
              사용 가능한 템플릿이 없습니다.
            </div>
          ) : (
            <div className="grid gap-3">
              {templates.map((template) => (
                <div
                  key={template.industry_type}
                  className="rounded-lg border p-4 hover:bg-accent hover:text-accent-foreground cursor-pointer transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="font-semibold">{template.industry_name}</h3>
                      <p className="mt-1 text-sm text-muted-foreground">
                        {template.description}
                      </p>
                      <p className="mt-2 text-xs text-muted-foreground">
                        {template.sections.length}개 법정 필수 섹션
                      </p>
                    </div>
                    <Button
                      onClick={() => handleSelect(template.industry_type as IndustryType)}
                      disabled={isLoading || selectedIndustry === template.industry_type}
                      variant="outline"
                      size="sm"
                      className="ml-4"
                    >
                      {selectedIndustry === template.industry_type ? '선택 중...' : '선택'}
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
