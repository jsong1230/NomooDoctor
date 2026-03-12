'use client';

/**
 * 채팅 메시지 목록 컴포넌트
 */

import { useEffect, useRef } from 'react';
import type { ChatMessage } from '@/types/chat';
import { getRiskLabel, getRiskColor } from '@/types/chat';
import { Bot, User, AlertTriangle, Scale } from 'lucide-react';

interface MessageListProps {
  messages: ChatMessage[];
  streamingContent: string;
  isStreaming: boolean;
}

export function MessageList({ messages, streamingContent, isStreaming }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingContent]);

  return (
    <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4">
      {messages.length === 0 && !isStreaming && (
        <div className="text-center py-12">
          <Bot className="w-12 h-12 text-primary-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-slate-900 mb-2">
            무엇이든 물어보세요
          </h3>
          <p className="text-sm text-slate-500 max-w-sm mx-auto">
            노동법, 급여, 근로계약, 해고 절차 등 사업장 운영에 필요한 노무 관련
            질문에 답변해 드립니다.
          </p>
        </div>
      )}

      {messages.map((message) => (
        <MessageBubble key={message.id} message={message} />
      ))}

      {/* 스트리밍 중인 응답 */}
      {isStreaming && streamingContent && (
        <div className="flex gap-3">
          <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center flex-shrink-0">
            <Bot className="w-4 h-4 text-primary-600" />
          </div>
          <div className="flex-1 bg-white border border-slate-200 rounded-2xl rounded-tl-sm px-4 py-3 max-w-[80%]">
            <div className="text-sm text-slate-900 whitespace-pre-wrap">
              {streamingContent}
              <span className="inline-block w-1.5 h-4 bg-primary-600 animate-pulse ml-0.5" />
            </div>
          </div>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
}

function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === 'user';

  if (isUser) {
    return (
      <div className="flex gap-3 justify-end">
        <div className="bg-primary-600 text-white rounded-2xl rounded-tr-sm px-4 py-3 max-w-[80%]">
          <p className="text-sm whitespace-pre-wrap">{message.content}</p>
        </div>
        <div className="w-8 h-8 bg-slate-200 rounded-full flex items-center justify-center flex-shrink-0">
          <User className="w-4 h-4 text-slate-600" />
        </div>
      </div>
    );
  }

  return (
    <div className="flex gap-3">
      <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center flex-shrink-0">
        <Bot className="w-4 h-4 text-primary-600" />
      </div>
      <div className="flex-1 max-w-[80%] space-y-2">
        <div className="bg-white border border-slate-200 rounded-2xl rounded-tl-sm px-4 py-3">
          <div className="text-sm text-slate-900 whitespace-pre-wrap">
            {message.content}
          </div>
        </div>

        {/* 위험도 태그 */}
        {message.risk_level && message.risk_level !== 'low' && (
          <div className="flex items-center gap-1.5">
            <AlertTriangle className="w-3.5 h-3.5 text-amber-500" />
            <span className={`text-xs font-medium ${getRiskColor(message.risk_level)}`}>
              위험도: {getRiskLabel(message.risk_level)}
            </span>
          </div>
        )}

        {/* 법령 인용 */}
        {message.law_references?.references && message.law_references.references.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {message.law_references.references.map((ref, i) => (
              <span
                key={i}
                className="inline-flex items-center gap-1 text-xs bg-blue-50 text-blue-700 px-2 py-0.5 rounded-full"
              >
                <Scale className="w-3 h-3" />
                {ref.law_name} {ref.article}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
