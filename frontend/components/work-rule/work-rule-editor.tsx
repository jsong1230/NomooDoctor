'use client';

/**
 * 취업규칙 편집 컴포넌트
 * 14개 섹션을 아코디언 형태로 표시하고 편집
 */

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import type { WorkRuleContent, WorkRuleSection } from '@/types/work-rule';
import { Save, FileText } from 'lucide-react';

interface WorkRuleEditorProps {
  content: WorkRuleContent;
  onSave: (content: WorkRuleContent) => Promise<void>;
  isEditable: boolean;
  isSaving?: boolean;
}

export function WorkRuleEditor({
  content,
  onSave,
  isEditable,
  isSaving = false,
}: WorkRuleEditorProps) {
  const [editedContent, setEditedContent] = useState<WorkRuleContent>(content);
  const [isDirty, setIsDirty] = useState(false);

  const handleSectionChange = (sectionNumber: number, newHtml: string) => {
    setEditedContent({
      sections: editedContent.sections.map((s) =>
        s.section_number === sectionNumber
          ? { ...s, content_html: newHtml }
          : s
      ),
    });
    setIsDirty(true);
  };

  const handleSave = async () => {
    try {
      await onSave(editedContent);
      setIsDirty(false);
    } catch (error) {
      console.error('저장 실패:', error);
    }
  };

  const handleReset = () => {
    setEditedContent(content);
    setIsDirty(false);
  };

  return (
    <div className="space-y-4">
      {/* 편집 상태 표시 및 저장 버튼 */}
      {isEditable && isDirty && (
        <Card className="border-yellow-200 bg-yellow-50 dark:border-yellow-900 dark:bg-yellow-950">
          <CardContent className="flex items-center justify-between py-3">
            <span className="text-sm font-medium text-yellow-900 dark:text-yellow-100">
              수정되었습니다. 저장 버튼을 클릭하여 변경 사항을 저장하세요.
            </span>
            <div className="flex gap-2">
              <Button
                onClick={handleReset}
                variant="outline"
                size="sm"
                disabled={isSaving}
              >
                취소
              </Button>
              <Button
                onClick={handleSave}
                size="sm"
                disabled={isSaving}
                className="gap-2"
              >
                <Save className="h-4 w-4" />
                {isSaving ? '저장 중...' : '저장'}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* 섹션 아코디언 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            취업규칙 내용
          </CardTitle>
          <CardDescription>
            근로기준법 제93조 법정 필수 기재사항 {editedContent.sections.length}개 항목
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Accordion type="single" collapsible className="w-full">
            {editedContent.sections.map((section) => (
              <AccordionItem
                key={section.section_number}
                value={`section-${section.section_number}`}
              >
                <AccordionTrigger className="hover:no-underline">
                  <div className="flex w-full items-center gap-3 text-left">
                    <Badge variant="outline" className="flex-shrink-0">
                      {section.section_number}
                    </Badge>
                    <div className="flex-1">
                      <h3 className="font-semibold">{section.title}</h3>
                      {section.law_reference && (
                        <p className="text-xs text-muted-foreground">
                          {section.law_reference}
                        </p>
                      )}
                    </div>
                  </div>
                </AccordionTrigger>

                <AccordionContent className="space-y-4 pt-4">
                  {/* HTML 미리보기 */}
                  <div className="rounded-lg border bg-muted/30 p-4">
                    <h4 className="mb-2 text-sm font-semibold">내용 미리보기</h4>
                    <div
                      className="prose prose-sm dark:prose-invert max-w-none"
                      dangerouslySetInnerHTML={{
                        __html: editedContent.sections.find(
                          (s) => s.section_number === section.section_number
                        )?.content_html || '',
                      }}
                    />
                  </div>

                  {/* 편집 영역 */}
                  {isEditable ? (
                    <div className="space-y-2">
                      <label className="text-sm font-semibold">
                        HTML 편집
                      </label>
                      <Textarea
                        value={editedContent.sections.find(
                          (s) => s.section_number === section.section_number
                        )?.content_html || ''}
                        onChange={(e) =>
                          handleSectionChange(section.section_number, e.target.value)
                        }
                        placeholder="취업규칙 내용을 HTML 형식으로 작성하세요."
                        className="min-h-[200px] font-mono text-xs"
                      />
                      <p className="text-xs text-muted-foreground">
                        &lt;p&gt;, &lt;ol&gt;, &lt;li&gt; 등의 HTML 태그를 사용할 수 있습니다.
                      </p>
                    </div>
                  ) : (
                    <div className="rounded-lg bg-muted p-3 text-sm text-muted-foreground">
                      이 버전은 편집할 수 없습니다. (상태: {section.section_number === 1 ? 'Active' : 'Review'})
                    </div>
                  )}

                  {/* 필수 항목 표시 */}
                  {section.is_required && (
                    <div className="rounded-lg bg-red-50 p-3 dark:bg-red-950">
                      <p className="text-xs font-semibold text-red-900 dark:text-red-100">
                        이는 근로기준법 제93조에 명시된 법정 필수 기재사항입니다.
                      </p>
                    </div>
                  )}
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </CardContent>
      </Card>
    </div>
  );
}
