/**
 * AI 노무 상담 채팅 페이지
 */

import { Metadata } from 'next';
import { ChatClient } from '@/components/chat/chat-client';

export const metadata: Metadata = {
  title: 'AI 노무 상담 | 노무닥터',
  description: '노동법 관련 질문에 AI가 즉시 답변해 드립니다.',
};

export default function ChatPage() {
  return <ChatClient />;
}
