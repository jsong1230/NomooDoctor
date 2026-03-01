/**
 * 인증 API 클라이언트
 * design.md의 API 스펙을 참조하여 구현
 */

import { axiosInstance } from '../api-client';
import type {
  AuthResponse,
  LoginRequest,
  RegisterRequest,
  RefreshRequest,
  RefreshResponse,
  PasswordResetRequest,
  PasswordResetConfirmRequest,
} from '@/types/auth';

const AUTH_ENDPOINT = '/auth';

/**
 * 회원가입
 * POST /api/v1/auth/register
 */
export async function register(data: RegisterRequest): Promise<AuthResponse> {
  const response = await axiosInstance.post<{ success: boolean; data: AuthResponse; message: string }>(
    `${AUTH_ENDPOINT}/register`,
    data
  );
  return response.data.data;
}

/**
 * 로그인
 * POST /api/v1/auth/login
 */
export async function login(data: LoginRequest): Promise<AuthResponse> {
  const response = await axiosInstance.post<{ success: boolean; data: AuthResponse; message: string }>(
    `${AUTH_ENDPOINT}/login`,
    data
  );
  return response.data.data;
}

/**
 * 토큰 갱신 (Refresh Token Rotation)
 * POST /api/v1/auth/refresh
 */
export async function refresh(data: RefreshRequest): Promise<RefreshResponse> {
  const response = await axiosInstance.post<{ success: boolean; data: RefreshResponse }>(
    `${AUTH_ENDPOINT}/refresh`,
    data
  );
  return response.data.data;
}

/**
 * 로그아웃
 * POST /api/v1/auth/logout
 */
export async function logout(): Promise<void> {
  const { apiClient } = await import('../api-client');
  await apiClient.getInstance().post<{ success: boolean; data: null; message: string }>(
    `${AUTH_ENDPOINT}/logout`
  );
}

/**
 * 비밀번호 재설정 이메일 발송
 * POST /api/v1/auth/password/reset
 */
export async function requestPasswordReset(data: PasswordResetRequest): Promise<void> {
  await axiosInstance.post<{ success: boolean; data: null; message: string }>(
    `${AUTH_ENDPOINT}/password/reset`,
    data
  );
}

/**
 * 비밀번호 재설정 확인
 * POST /api/v1/auth/password/confirm
 */
export async function confirmPasswordReset(data: PasswordResetConfirmRequest): Promise<void> {
  await axiosInstance.post<{ success: boolean; data: null; message: string }>(
    `${AUTH_ENDPOINT}/password/confirm`,
    data
  );
}

// API 함수들을 객체로 내보내기
export const authApi = {
  register,
  login,
  refresh,
  logout,
  requestPasswordReset,
  confirmPasswordReset,
};
