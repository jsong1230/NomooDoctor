# WorkRule Component Documentation

## Overview

WorkRule 컴포넌트는 F-08 취업규칙 자동화 기능을 위한 프론트엔드 컴포넌트입니다. React Server Components와 Client Components 패턴을 따릅니다.

## File Structure

```
frontend/
├── types/work-rule.ts                    # 타입 정의
├── lib/
│   ├── api/work-rule.ts                  # API 클라이언트
│   └── stores/work-rule-store.ts         # Zustand 상태 관리
├── components/work-rule/
│   ├── template-selector.tsx             # 업종 템플릿 선택
│   ├── work-rule-list.tsx                # 취업규칙 목록
│   ├── work-rule-editor.tsx              # 섹션 편집기
│   └── consent-checklist.tsx             # 동의 절차 체크리스트
└── app/(main)/work-rules/
    ├── page.tsx                          # 목록 페이지 (RSC)
    ├── work-rules-client.tsx             # 목록 페이지 클라이언트
    └── [id]/
        ├── page.tsx                      # 상세 페이지 (RSC)
        └── work-rule-detail-client.tsx   # 상세 페이지 클라이언트
```

## Components

### TemplateSelector
**Props:**
- `open: boolean` - 모달 오픈 상태
- `onOpenChange: (open: boolean) => void` - 모달 상태 변경 콜백
- `onSelect: (industryType: IndustryType) => Promise<void>` - 템플릿 선택 시 콜백
- `isLoading?: boolean` - 로딩 상태

**Features:**
- 업종별 표준 템플릿 표시
- 각 템플릿의 설명 및 섹션 수 표시
- 템플릿 선택 시 새 취업규칙 생성

### WorkRuleList
**Props:**
- `companyId: string` - 사업장 ID

**Features:**
- 취업규칙 목록 조회 및 표시
- 버전, 상태, AI 생성 여부 표시
- 새로 작성 버튼
- 각 항목 클릭 시 상세 페이지로 이동

### WorkRuleEditor
**Props:**
- `content: WorkRuleContent` - 편집할 내용
- `onSave: (content: WorkRuleContent) => Promise<void>` - 저장 콜백
- `isEditable: boolean` - 편집 가능 여부
- `isSaving?: boolean` - 저장 중 상태

**Features:**
- 14개 섹션을 아코디언으로 표시
- 각 섹션에 대한 HTML 미리보기 및 편집
- 법정 필수 기재사항 표시
- 저장 및 취소 버튼

### ConsentChecklist
**Props:**
- `compact?: boolean` - 축약 모드 여부

**Features:**
- 근로자 동의 절차 안내
- 필요 동의율 표시
- 각 단계별 설명 및 법령 인용

## Type Definitions

### WorkRule
```typescript
interface WorkRule {
  id: string;
  company_id: string;
  version: number;
  status: WorkRuleStatus;
  industry_type: string;
  content: WorkRuleContent;
  effective_date?: string;
  approval_date?: string;
  worker_consent_count?: number;
  total_worker_count?: number;
  revision_reason?: string;
  ai_generated: boolean;
  ai_model?: string;
  docx_url?: string;
  pdf_url?: string;
  filed_at?: string;
  created_at: string;
  updated_at: string;
}
```

### WorkRuleSection
```typescript
interface WorkRuleSection {
  section_number: number;
  title: string;
  content_html: string;
  is_required: boolean;
  law_reference?: string;
}
```

## API Client Functions

### getTemplates
업종별 표준 템플릿 조회
```typescript
getTemplates(industryType?: string): Promise<TemplateResponse[]>
```

### createWorkRule
새 취업규칙 생성
```typescript
createWorkRule(data: WorkRuleCreate): Promise<WorkRule>
```

### getWorkRules
취업규칙 목록 조회
```typescript
getWorkRules(params?: {
  status?: string;
  page?: number;
  per_page?: number;
}): Promise<WorkRuleListItem[]>
```

### getWorkRule
취업규칙 상세 조회
```typescript
getWorkRule(id: string): Promise<WorkRule>
```

### updateWorkRule
취업규칙 수정
```typescript
updateWorkRule(id: string, data: WorkRuleUpdate): Promise<WorkRule>
```

### generateAiDraft
AI 초안 생성
```typescript
generateAiDraft(id: string, data: WorkRuleGenerateRequest): Promise<WorkRule>
```

### reviseWorkRule
취업규칙 개정
```typescript
reviseWorkRule(id: string, data: WorkRuleReviseRequest): Promise<WorkRule>
```

### downloadWorkRule
Word/PDF 다운로드
```typescript
downloadWorkRule(id: string, type: 'docx' | 'pdf'): Promise<DownloadResponse>
```

## State Management (Zustand)

### WorkRuleStore
```typescript
interface WorkRuleState {
  workRules: WorkRuleListItem[];
  currentWorkRule: WorkRule | null;
  templates: TemplateResponse[];
  consentChecklist: ConsentChecklistResponse | null;
  isLoading: boolean;
  error: string | null;

  // Actions
  fetchWorkRules: (params?: {...}) => Promise<void>;
  fetchWorkRule: (id: string) => Promise<void>;
  fetchTemplates: (industryType?: string) => Promise<void>;
  fetchConsentChecklist: () => Promise<void>;
  createWorkRule: (data: WorkRuleCreate) => Promise<WorkRule>;
  updateWorkRule: (id: string, data: WorkRuleUpdate) => Promise<void>;
  deleteWorkRule: (id: string) => Promise<void>;
  generateAiDraft: (id: string, data: WorkRuleGenerateRequest) => Promise<void>;
  reviseWorkRule: (id: string, data: WorkRuleReviseRequest) => Promise<WorkRule>;
}
```

## UI Components

새로운 UI 컴포넌트들이 생성되었습니다:
- `button.tsx` - 버튼 컴포넌트
- `card.tsx` - 카드 컴포넌트
- `badge.tsx` - 배지 컴포넌트
- `dialog.tsx` - 다이얼로그/모달 컴포넌트
- `textarea.tsx` - 텍스트 에어리어 컴포넌트
- `accordion.tsx` - 아코디언 컴포넌트
- `separator.tsx` - 구분선 컴포넌트
- `progress.tsx` - 진행 바 컴포넌트

## Styling

모든 컴포넌트는 Tailwind CSS로 스타일링되어 있으며, 다음을 준수합니다:
- shadcn/ui 디자인 패턴
- 다크 모드 지원
- WCAG 접근성 기준

## Usage Example

### 취업규칙 목록 페이지
```tsx
import { WorkRuleList } from '@/components/work-rule/work-rule-list';

export default function WorkRulesPage() {
  return <WorkRuleList companyId="company-uuid" />;
}
```

### 취업규칙 상세 페이지
```tsx
import { WorkRuleEditor } from '@/components/work-rule/work-rule-editor';

export default function WorkRuleDetailPage() {
  const { currentWorkRule, updateWorkRule } = workRuleStore();

  return (
    <WorkRuleEditor
      content={currentWorkRule.content}
      onSave={updateWorkRule}
      isEditable={currentWorkRule.status === 'draft'}
    />
  );
}
```

## Notes

1. **Server Components**: 페이지 컴포넌트 (page.tsx)는 RSC로 구현되어 있습니다.
2. **Client Components**: 상태 관리가 필요한 컴포넌트는 'use client' 지시문을 사용합니다.
3. **API 호출**: 모든 API 호출은 `lib/api/work-rule.ts`를 통해 이루어집니다.
4. **에러 처리**: 오류는 try-catch로 처리되며 사용자에게 표시됩니다.
5. **로딩 상태**: isLoading 플래그로 UI 업데이트 중 상태를 관리합니다.

## Future Enhancements

1. **Rich Text Editor**: TipTap을 통한 고급 텍스트 편집 기능
2. **Word/PDF 생성**: 다운로드 기능 추가
3. **버전 비교**: 이전 버전과의 차이점 표시
4. **동의 추적**: 근로자 동의 현황 관리
