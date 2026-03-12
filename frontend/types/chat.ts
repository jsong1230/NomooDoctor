/**
 * AI 챗봇 관련 타입 정의
 */

export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'EMERGENCY';

export type MessageRole = 'user' | 'assistant' | 'system';

export interface ChatSession {
  id: string;
  title: string | null;
  risk_level: string;
  attorney_referred: boolean;
  message_count: number;
  created_at: string;
  updated_at: string;
}

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  law_references: { references: LawReference[] } | null;
  risk_level: string | null;
  disclaimer_shown: boolean;
  created_at: string;
}

export interface LawReference {
  law_name: string;
  article: string;
  content?: string;
}

export interface ChatSessionDetail {
  session: ChatSession;
  messages: ChatMessage[];
}

export interface FAQItem {
  category: string;
  question: string;
  description: string;
}

// SSE 이벤트 타입
export interface SSEMessageEvent {
  content: string;
}

export interface SSELawReferenceEvent {
  law_name: string;
  article: string;
  content?: string;
}

export interface SSERiskLevelEvent {
  level: RiskLevel;
}

export interface SSEDoneEvent {
  message_id: string;
  risk_level: RiskLevel;
  attorney_referred: boolean;
}

export interface SSEErrorEvent {
  code: string;
  message: string;
}

// 위험도별 설정
export const RISK_LEVEL_CONFIG: Record<string, { label: string; color: string; bgColor: string }> = {
  low: { label: '안전', color: 'text-green-700', bgColor: 'bg-green-100' },
  medium: { label: '주의', color: 'text-yellow-700', bgColor: 'bg-yellow-100' },
  high: { label: '위험', color: 'text-red-700', bgColor: 'bg-red-100' },
  emergency: { label: '긴급', color: 'text-red-900', bgColor: 'bg-red-200' },
};

export function getRiskLabel(level: string): string {
  return RISK_LEVEL_CONFIG[level.toLowerCase()]?.label ?? level;
}

export function getRiskColor(level: string): string {
  return RISK_LEVEL_CONFIG[level.toLowerCase()]?.color ?? 'text-slate-600';
}
