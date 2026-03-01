# LoginForm Component

## 설명

로그인 폼 컴포넌트로, 이메일/비밀번호를 통한 사용자 로그인을 처리합니다.

## 기능

- 이메일/비밀번호 입력 폼
- zod 스키마를 통한 클라이언트 측 검증
- API 호출을 통한 서버 측 인증
- 에러 메시지 표시
- 로딩 상태 처리
- 비밀번호 찾기 링크
- 회원가입 링크

## Props

| Prop | 타입 | 설명 | 필수 여부 |
|------|------|------|-----------|
| onSuccess | `() => void` | 로그인 성공 시 호출되는 콜백 함수 | 아니오 |

## 사용 예시

```tsx
import { LoginForm } from '@/components/auth/login-form';

export default function LoginPage() {
  return (
    <div>
      <LoginForm onSuccess={() => console.log('로그인 성공')} />
    </div>
  );
}
```

## 검증 규칙

| 필드 | 규칙 |
|------|------|
| email | 유효한 이메일 형식, 필수 |
| password | 최소 1자, 필수 |

## 상태 관리

- 로딩 중일 때 버튼에 스피너 표시
- 에러 발생 시 전체 에러 메시지 표시
- 필드별 에러 발생 시 해당 필드 아래에 에러 메시지 표시

## 라우팅

- 로그인 성공 시 기본적으로 `/dashboard`로 리다이렉트
- `onSuccess` prop이 제공되면 콜백 호출 후 리다이렉트되지 않음
