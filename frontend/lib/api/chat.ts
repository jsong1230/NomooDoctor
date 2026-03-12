/**
 * AI 챗봇 API 클라이언트
 */

import { apiClient } from '../api-client';
import { authStore } from '../stores/auth-store';
import type {
  ChatSession,
  ChatSessionDetail,
  FAQItem,
} from '@/types/chat';

const CHAT_ENDPOINT = '/chat';

/**
 * 채팅 세션 목록 조회
 */
async function listSessions(params?: {
  skip?: number;
  limit?: number;
}): Promise<ChatSession[]> {
  const response = await apiClient.getInstance().get<{
    success: boolean;
    data: ChatSession[];
  }>(`${CHAT_ENDPOINT}/sessions`, { params });
  return response.data.data;
}

/**
 * 새 채팅 세션 생성
 */
async function createSession(title?: string): Promise<ChatSession> {
  const response = await apiClient.getInstance().post<{
    success: boolean;
    data: ChatSession;
  }>(`${CHAT_ENDPOINT}/sessions`, { title: title || null });
  return response.data.data;
}

/**
 * 채팅 세션 상세 (메시지 포함)
 */
async function getSession(sessionId: string): Promise<ChatSessionDetail> {
  const response = await apiClient.getInstance().get<{
    success: boolean;
    data: ChatSessionDetail;
  }>(`${CHAT_ENDPOINT}/sessions/${sessionId}`);
  return response.data.data;
}

/**
 * 채팅 세션 삭제
 */
async function deleteSession(sessionId: string): Promise<void> {
  await apiClient.getInstance().delete(`${CHAT_ENDPOINT}/sessions/${sessionId}`);
}

/**
 * 메시지 전송 (SSE 스트리밍)
 * fetch API로 SSE 스트림을 처리합니다.
 */
async function sendMessage(
  sessionId: string,
  content: string,
  onMessage: (text: string) => void,
  onLawReference?: (ref: { law_name: string; article: string }) => void,
  onRiskLevel?: (level: string) => void,
  onDone?: (data: { message_id: string; risk_level: string; attorney_referred: boolean }) => void,
  onError?: (error: { code: string; message: string }) => void,
): Promise<void> {
  const token = authStore.getState().accessToken;
  const baseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

  const response = await fetch(
    `${baseURL}${CHAT_ENDPOINT}/sessions/${sessionId}/messages`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
        'Accept': 'text/event-stream',
      },
      body: JSON.stringify({ content }),
    },
  );

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }

  const reader = response.body?.getReader();
  if (!reader) throw new Error('No response body');

  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop() || '';

    let currentEvent = '';

    for (const line of lines) {
      if (line.startsWith('event: ')) {
        currentEvent = line.slice(7).trim();
      } else if (line.startsWith('data: ')) {
        const dataStr = line.slice(6);
        try {
          const data = JSON.parse(dataStr);
          switch (currentEvent) {
            case 'message':
              onMessage(data.content);
              break;
            case 'law_reference':
              onLawReference?.(data);
              break;
            case 'risk_level':
              onRiskLevel?.(data.level);
              break;
            case 'done':
              onDone?.(data);
              break;
            case 'error':
              onError?.(data);
              break;
          }
        } catch {
          // JSON 파싱 실패 무시
        }
        currentEvent = '';
      }
    }
  }
}

/**
 * FAQ 목록 조회
 */
async function getFAQ(): Promise<FAQItem[]> {
  const response = await apiClient.getInstance().get<{
    success: boolean;
    data: FAQItem[];
  }>(`${CHAT_ENDPOINT}/faq`);
  return response.data.data;
}

export const chatApi = {
  listSessions,
  createSession,
  getSession,
  deleteSession,
  sendMessage,
  getFAQ,
};
