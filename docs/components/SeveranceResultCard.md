# SeveranceResultCard 컴포넌트

퇴직금 계산 결과를 표시하는 카드 컴포넌트입니다. 금액 breakdown과 상세 계산 정보를 제공합니다.

## 위치

`frontend/components/retirement/severance-result-card.tsx`

## Props

```typescript
interface SeveranceResultCardProps {
  result: SeveranceResult;
  onSave?: () => void;
  isSaving?: boolean;
}
```

- `result`: 퇴직금 계산 결과 (필수)
- `onSave`: "퇴직금 확정 저장" 버튼 클릭 시 호출 함수 (선택사항)
- `isSaving`: 저장 진행 상태 (선택사항, 기본값 false)

## 표시 정보

### 헤더 영역
- 직원명
- 입사일, 퇴직예정일
- 재직기간 (일수)
- 퇴직금 수급 자격 여부

### 메인 결과
**총 지급액** (강조 표시)
- 큰 폰트, 파란색 배경
- 지급 기한 표시

### 항목별 금액 (4열 그리드)
1. 퇴직금 (기본값)
2. 연차미사용수당
3. 상여금 포함분
4. 일평균임금

### 상세 계산 정보 (확장 가능)
- 최근 3개월 임금합계
- 최근 3개월 총 일수
- 상여금 3/12
- 계산된 일평균임금
- 퇴직금 계산식 (수식 형태)
- 연차미사용수당 계산식 (수식 형태)

### 저장 버튼 (선택사항)
- "퇴직금 확정 저장" 버튼
- onSave prop이 전달되면 표시
- isSaving 상태에 따라 활성화/비활성화

## 특징

### 1. 반응형 레이아웃
- 항목별 금액: 모바일에서는 1열, 데스크톱에서는 2열

### 2. 동적 우정보
- 상세 계산 정보는 기본 숨김 (ChevronDown/ChevronUp으로 토글)
- 클릭하면 펼쳐져 모든 정보 표시

### 3. 금액 포맷팅
- `toLocaleString('ko-KR')` 사용
- 3자리 쉼표 구분
- "원" 단위 표시

### 4. 날짜 포맷팅
- `toLocaleDateString('ko-KR')`
- "2026년 3월 31일" 형태

## 사용 예시

```tsx
import { SeveranceResultCard } from '@/components/retirement/severance-result-card';
import type { SeveranceResult } from '@/types/retirement';

export function MyComponent({ result }: { result: SeveranceResult }) {
  const handleSave = async () => {
    // 저장 로직
    console.log('저장 중...');
  };

  return (
    <SeveranceResultCard
      result={result}
      onSave={handleSave}
      isSaving={false}
    />
  );
}
```

## CSS 클래스 구조

```
.border.border-gray-200.rounded-lg.bg-white
  ├─ .bg-gradient-to-r.from-blue-50.to-blue-100 (헤더)
  │   ├─ h3 (직원명)
  │   └─ .grid.grid-cols-2 (입사일, 퇴직예정일, 재직기간, 자격)
  ├─ .p-6.space-y-6 (메인 영역)
  │   ├─ .bg-blue-50.border.border-blue-200 (총 지급액)
  │   ├─ .grid.grid-cols-1.md:grid-cols-2 (항목별 금액)
  │   │   ├─ .border.border-gray-200 (퇴직금)
  │   │   ├─ .border.border-gray-200 (연차미사용수당)
  │   │   ├─ .border.border-gray-200 (상여금)
  │   │   └─ .border.border-gray-200 (일평균임금)
  │   ├─ .border.border-gray-200 (상세 계산 정보)
  │   │   ├─ button (토글)
  │   │   └─ .border-t.bg-gray-50 (상세 내용)
  │   └─ button (저장)
```

## 의존성

- 라이브러리: lucide-react (ChevronDown, ChevronUp)
- 타입: SeveranceResult

## 성능 고려사항

- Client Component로 상태 관리 간단
- 상세 정보 토글은 로컬 상태로 관리
- 금액 포맷팅은 렌더링 시마다 수행 (많지 않음)

## 접근성

- 토글 버튼은 명확한 아이콘 제공
- 모든 숫자는 천 단위 구분으로 읽기 쉬움
- 색상 외 텍스트로도 정보 전달 (예: "금액", "수당")
