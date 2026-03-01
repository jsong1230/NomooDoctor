/**
 * API 클라이언트 설정
 * axios 인스턴스를 생성하고 인터셉터를 설정합니다.
 */

import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from 'axios';
import { authStore } from './stores/auth-store';

// API 기본 URL (환경 변수 또는 기본값)
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 30000,
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // 요청 인터셉터 - 토큰 추가
    this.client.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        const token = authStore.getState().accessToken;
        if (token && config.headers) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // 응답 인터셉터 - 토큰 갱신 및 에러 처리
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        const originalRequest = error.config as InternalAxiosRequestConfig & {
          _retry?: boolean;
        };

        // 401 에러이고 재시도하지 않은 경우
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            // 토큰 갱신 시도
            const refreshToken = authStore.getState().refreshToken;
            if (refreshToken) {
              const { authApi } = await import('./api/auth');
              const response = await authApi.refresh({ refresh_token: refreshToken });

              // 새 토큰 저장
              authStore.getState().setTokens(response.access_token, response.refresh_token);

              // 원래 요청 재시도
              if (originalRequest.headers) {
                originalRequest.headers.Authorization = `Bearer ${response.access_token}`;
              }
              return this.client(originalRequest);
            }
          } catch (refreshError) {
            // 토큰 갱신 실패 - 로그아웃
            authStore.getState().logout();
            window.location.href = '/login';
            return Promise.reject(refreshError);
          }
        }

        return Promise.reject(error);
      }
    );
  }

  getInstance(): AxiosInstance {
    return this.client;
  }

  // 외부에서 토큰이 없이 요청할 때 사용하는 인스턴스
  getPublicInstance(): AxiosInstance {
    return axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 30000,
    });
  }
}

// 단일 인스턴스 내보내기
export const apiClient = new ApiClient();

// 기본 axios 인스턴스 내보내기 (토큰 없는 요청용)
export const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});
