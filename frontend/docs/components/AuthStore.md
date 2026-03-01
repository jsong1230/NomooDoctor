# AuthStore (인증 상태 관리)

## 설명

Zustand를 사용한 인증 상태 관리 스토어입니다. 사용자 정보, 액세스 토큰, 리프레시 토큰을 저장하고 관리합니다.

## 상태

| 상태 | 타입 | 설명 |
|------|------|------|
| user | `User \| null` | 현재 로그인한 사용자 정보 |
| accessToken | `string \| null` | 액세스 토큰 (1시간 유효) |
| refreshToken | `string \| null` | 리프레시 토큰 (30일 유효) |
| isAuthenticated | `boolean` | 인증 여부 |

## 액션

| 액션 | 매개변수 | 설명 |
|------|----------|------|
| setUser | `user: User` | 사용자 정보 설정 |
| setTokens | `accessToken: string, refreshToken: string` | 토큰 설정 |
| login | `user: User, accessToken: string, refreshToken: string` | 로그인 (사용자 정보 + 토큰 설정) |
| logout | `() => void` | 로그아웃 (모든 상태 초기화) |
| updateUser | `updates: Partial<User>` | 사용자 정보 일부 업데이트 |

## 사용 예시

```tsx
import { authStore } from '@/lib/stores/auth-store';

// 로그인
authStore.getState().login(user, accessToken, refreshToken);

// 사용자 정보 접근
const user = authStore.getState().user;
const token = authStore.getState().accessToken;

// 로그아웃
authStore.getState().logout();

// 사용자 정보 업데이트
authStore.getState().updateUser({ name: '새 이름' });

// React 컴포넌트에서 사용 (useStore hook)
import { useStore } from 'zustand';
const user = useStore(authStore, (state) => state.user);
```

## 영구 저장

`zustand/middleware`의 `persist`를 사용하여 localStorage에 상태를 영구 저장합니다.

- 저장 키: `auth-storage`
- 저장 항목: `user`, `accessToken`, `refreshToken`, `isAuthenticated`

## 토큰 관리

### 액세스 토큰
- 유효기간: 1시간
- 사용자 정보 포함 (user_id, company_id, plan, role)
- API 요청 시 Authorization 헤더에 포함

### 리프레시 토큰
- 유효기간: 30일
- 액세스 토큰 만료 시 갱신에 사용
- Refresh Token Rotation으로 재사용 감지

## 보안 고려사항

1. 토큰은 localStorage에 저장 (서버 사이드 렌더링 필요 시 쿠키로 전환 고려)
2. HTTPS 환경에서만 사용 권장
3. 토큰 탈취 시 즉시 로그아웃 필요
4. 민감한 작업 시 재인증 고려
