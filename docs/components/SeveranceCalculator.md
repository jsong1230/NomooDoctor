# SeveranceCalculator 컴포넌트

퇴직금 계산 폼과 결과 표시를 담당하는 Client Component입니다.

## 위치

`frontend/components/retirement/severance-calculator.tsx`

## Props

```typescript
interface SeveranceCalculatorProps {
  employees?: Array<{ id: string; name: string }>;
  onCalculated?: () => void;
}
```

- `employees`: 선택 가능한 직원 목록 (선택사항)
- `onCalculated`: 계산 완료 후 콜백 함수 (선택사항)

## 상태 관리

Zustand 스토어(`retirementStore`)를 사용하여 다음 상태를 관리합니다:

- `calculationResult`: 계산 결과 (SeveranceResult | null)
- `savedRecord`: 저장된 퇴직금 기록 (SeveranceRecord | null)
- `isCalculating`: 계산 진행 상태 (boolean)
- `calculateError`: 에러 메시지 (string | null)

## 기능

### 1. 퇴직금 계산
- 직원 선택, 퇴직일, 추가 정보(상여금, 미사용 연차) 입력
- POST `/api/v1/retirement/calculate` 호출
- 결과는 DB에 저장하지 않음 (미리보기)

### 2. 계산 결과 확인
- `SeveranceResultCard` 컴포넌트로 결과 표시
- 항목별 금액 breakdown 제공
- 상세 계산식 표시 (확장 가능)

### 3. 퇴직금 확정 저장
- "퇴직금 확정 저장" 버튼 클릭
- POST `/api/v1/retirement/severance` 호출
- DB에 저장 후 기록 ID 반환

### 4. 급여 수동 입력 (선택사항)
- 최근 3개월 급여 수동 입력 가능
- payslips 데이터가 없을 때 사용
- `MonthlyWageInput` 컴포넌트 제공

## 폼 검증

react-hook-form + zod를 사용하여 다음을 검증합니다:

- employee_id: 필수
- resign_date: 필수 (YYYY-MM-DD 형식)
- annual_bonus: 0 이상
- unused_annual_leave_days: 0~40 범위

## 에러 처리

- 계산 실패: `calculateError` 상태에 메시지 저장
- UI에 빨간 배너로 표시
- 사용자 재시도 가능

## 사용 예시

```tsx
import { SeveranceCalculator } from '@/components/retirement/severance-calculator';

export function MyComponent() {
  const employees = [
    { id: '1', name: '홍길동' },
    { id: '2', name: '김영희' },
  ];

  const handleCalculated = () => {
    console.log('계산 완료');
  };

  return (
    <SeveranceCalculator
      employees={employees}
      onCalculated={handleCalculated}
    />
  );
}
```

## 라이프사이클

```
초기화
  ↓
퇴직금 계산 폼
  ↓
[계산] → 계산 결과 표시 (SeveranceResultCard)
  ├─ [다시 계산] → 폼으로 돌아가기
  └─ [확정 저장] → 저장 완료 메시지 → 새로운 계산
```

## 의존성

- API: `calculateSeverance`, `createSeverance` (lib/api/retirement.ts)
- 스토어: `retirementStore` (lib/stores/retirement-store.ts)
- 컴포넌트: `SeveranceResultCard`, `MonthlyWageInput`
- 라이브러리: react-hook-form, zod, lucide-react

## 성능 고려사항

- Client Component이므로 상태 변화가 많지 않을 때 최적
- 계산 결과는 스토어에 캐싱됨 (필요시 재사용 가능)
- 급여 입력은 토글로 제어하여 렌더링 최소화
