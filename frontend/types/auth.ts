/**
 * 인증 관련 타입 정의
 */

// 사용자 정보
export interface User {
  id: string;
  email: string;
  name: string;
  phone?: string;
  role: 'owner' | 'manager' | 'employee' | 'admin';
  plan: 'free' | 'basic' | 'standard' | 'premium' | 'enterprise';
  plan_expires_at?: string;
  company_id?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// 인증 토큰
export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

// 로그인/회원가입 응답
export interface AuthResponse {
  user: User;
  tokens: AuthTokens;
}

// 로그인 요청
export interface LoginRequest {
  email: string;
  password: string;
}

// 회원가입 요청
export interface RegisterRequest {
  email: string;
  password: string;
  name: string;
  phone?: string;
}

// 토큰 갱신 요청
export interface RefreshRequest {
  refresh_token: string;
}

// 토큰 갱신 응답
export interface RefreshResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

// 비밀번호 재설정 요청
export interface PasswordResetRequest {
  email: string;
}

// 비밀번호 재설정 확인 요청
export interface PasswordResetConfirmRequest {
  token: string;
  new_password: string;
}
