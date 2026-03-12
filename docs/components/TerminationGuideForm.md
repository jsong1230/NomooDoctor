# TerminationGuideForm 컴포넌트

해고/퇴직 절차 가이드 생성 폼을 담당하는 Client Component입니다.

## 위치

`frontend/components/retirement/termination-guide-form.tsx`

## Props

```typescript
interface TerminationGuideFormProps {
  employees?: Array<{ id: string; name: string }>;
  onGenerated?: () => void;
}
```

- `employees`: 선택 가능한 직원 목록 (선택사항)
- `onGenerated`: 가이드 생성 완료 후 콜백 함수 (선택사항)

## 상태 관리

Zustand 스토어(`retirementStore`)를 사용하여 다음 상태를 관리합니다:

- `terminationGuide`: 생성된 해고 절차 가이드 (TerminationGuide | null)
- `isGeneratingGuide`: 생성 진행 상태 (boolean)
- `guideError`: 에러 메시지 (string | null)

## 기능

### 1. 해고/퇴직 절차 정보 입력
- 직원 선택
- 해고/퇴직 유형: resignation(자발적 퇴사), mutual_agreement(권고사직), dismissal(해고), contract_expiry(계약만료), retirement(정년퇴직)
- 상세 사유 (최대 500자)

### 2. 위험 요소 체크
- is_pregnant: 임신 중
- is_on_parental_leave: 육아휴직 중
- is_union_member: 노조원
- is_workplace_injury: 산업재해 중
- is_whistleblower: 내부 고발자

위험 요소가 감지되면 실시간으로 경고 메시지 표시

### 3. 절차 가이드 생성
- POST `/api/v1/retirement/termination-guide` 호출
- Claude API를 통한 AI 생성 가이드
- 정적 체크리스트 + 동적 AI 가이드 조합

### 4. 생성된 가이드 표시
생성 완료 후 다음 정보를 표시합니다:

- **위험도 배지**: LOW, MEDIUM, HIGH, EMERGENCY 중 하나
- **위험 경고**: `RiskWarningBanner` 컴포넌트로 표시
- **해고 예고 정보**: 필요 시 예고 기간, 수당 등 표시
- **체크리스트**: `TerminationChecklist` 컴포넌트로 절차 표시
- **필요 서류**: 준비해야 할 서류 목록
- **실업급여 안내**: 수급 가능 여부 및 조건
- **AI 상세 가이드**: 법률 전문가 수준의 상세 설명
- **법률 참조**: 근로기준법 등 관련 법조항
- **면책 문구**: 법적 책임 부인

## 폼 검증

react-hook-form + zod를 사용하여 다음을 검증합니다:

- employee_id: 필수
- termination_type: 필수 (enum)
- reason: 필수, 1~500자
- risk_factors: 각각 boolean (모두 선택사항, 기본값 false)

## 에러 처리

- 생성 실패: `guideError` 상태에 메시지 저장
- UI에 빨간 배너로 표시
- 사용자 재시도 가능

## 위험도 판정 로직 (백엔드)

```
EMERGENCY: 임신, 육아휴직, 산재 중 (절대 해고 금지)
HIGH: 노조원, 내부 고발자 (법적 보호)
MEDIUM: 해고 유형 자체 (일반적 위험)
LOW: 자발적 퇴사, 계약만료 (낮은 위험)
```

## 사용 예시

```tsx
import { TerminationGuideForm } from '@/components/retirement/termination-guide-form';

export function MyComponent() {
  const employees = [
    { id: '1', name: '홍길동' },
    { id: '2', name: '김영희' },
  ];

  const handleGenerated = () => {
    console.log('가이드 생성 완료');
  };

  return (
    <TerminationGuideForm
      employees={employees}
      onGenerated={handleGenerated}
    />
  );
}
```

## 라이프사이클

```
초기화
  ↓
가이드 요청 폼
  ├─ 직원 선택
  ├─ 해고/퇴직 유형 선택
  ├─ 사유 입력
  ├─ 위험 요소 체크 (실시간 경고)
  └─ [절차 가이드 생성]
      ↓
  생성된 가이드 표시
  ├─ 위험도 배지
  ├─ 위험 경고
  ├─ 해고 예고 정보
  ├─ 체크리스트
  ├─ 필요 서류
  ├─ 실업급여 안내
  ├─ AI 상세 가이드
  ├─ 법률 참조
  ├─ 면책 문구
  └─ [새로운 절차 가이드 생성]
```

## 의존성

- API: `generateTerminationGuide` (lib/api/retirement.ts)
- 스토어: `retirementStore` (lib/stores/retirement-store.ts)
- 컴포넌트: `RiskWarningBanner`, `TerminationChecklist`
- 타입: `TERMINATION_TYPE_OPTIONS`, `RISK_LEVEL_COLOR_MAP`
- 라이브러리: react-hook-form, zod, lucide-react

## 성능 고려사항

- Client Component이므로 상태 변화가 많을 때 적합
- 위험 요소 체크박스는 실시간으로 업데이트되지만, 함수형 업데이트로 최적화
- Claude API 호출은 비동기로 처리되어 UI 블로킹 없음

## API 통합 참고사항

- 백엔드에서 위험도 판정 로직 수행
- Claude API를 사용한 AI 가이드 생성
- 법률 참조는 백엔드에서 사전 정의된 목록 제공
- 면책 문구는 백엔드에서 자동 추가
