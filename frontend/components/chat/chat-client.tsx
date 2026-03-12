'use client';

/**
 * AI 챗봇 클라이언트 컴포넌트
 * SSE 스트리밍, 세션 관리, FAQ 통합
 */

import { useState, useEffect, useCallback } from 'react';
import { chatApi } from '@/lib/api/chat';
import { chatStore } from '@/lib/stores/chat-store';
import type { ChatSession, ChatMessage, FAQItem } from '@/types/chat';
import { getRiskLabel, RISK_LEVEL_CONFIG } from '@/types/chat';
import { MessageList } from './message-list';
import { MessageInput } from './message-input';
import { FAQPanel } from './faq-panel';
import {
  MessageSquare,
  Plus,
  Trash2,
  Loader2,
  AlertCircle,
  ChevronLeft,
  PhoneCall,
} from 'lucide-react';

export function ChatClient() {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [currentSession, setCurrentSession] = useState<ChatSession | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingContent, setStreamingContent] = useState('');
  const [faqItems, setFaqItems] = useState<FAQItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showSidebar, setShowSidebar] = useState(true);
  const [showAttorneyCTA, setShowAttorneyCTA] = useState(false);

  // 세션 목록 & FAQ 로드
  useEffect(() => {
    const load = async () => {
      try {
        const [sessionList, faq] = await Promise.all([
          chatApi.listSessions(),
          chatApi.getFAQ(),
        ]);
        setSessions(sessionList);
        setFaqItems(faq);
      } catch (err: any) {
        setError(err.response?.data?.error?.message || '채팅 데이터를 불러오는데 실패했습니다.');
      } finally {
        setIsLoading(false);
      }
    };
    load();
  }, []);

  // 세션 선택
  const selectSession = useCallback(async (session: ChatSession) => {
    try {
      const detail = await chatApi.getSession(session.id);
      setCurrentSession(detail.session);
      setMessages(detail.messages);
      setShowAttorneyCTA(detail.session.attorney_referred);
      chatStore.getState().setCurrentSession(detail.session);
      chatStore.getState().setMessages(detail.messages);
    } catch {
      setError('세션을 불러오는데 실패했습니다.');
    }
  }, []);

  // 새 세션 생성
  const createNewSession = useCallback(async () => {
    try {
      const session = await chatApi.createSession();
      setSessions((prev) => [session, ...prev]);
      setCurrentSession(session);
      setMessages([]);
      setShowAttorneyCTA(false);
    } catch {
      setError('새 세션을 생성할 수 없습니다.');
    }
  }, []);

  // 세션 삭제
  const deleteSession = useCallback(async (sessionId: string) => {
    try {
      await chatApi.deleteSession(sessionId);
      setSessions((prev) => prev.filter((s) => s.id !== sessionId));
      if (currentSession?.id === sessionId) {
        setCurrentSession(null);
        setMessages([]);
      }
    } catch {
      setError('세션 삭제에 실패했습니다.');
    }
  }, [currentSession]);

  // 메시지 전송
  const sendMessage = useCallback(async (content: string) => {
    let session = currentSession;

    // 세션 없으면 자동 생성
    if (!session) {
      try {
        session = await chatApi.createSession(content.slice(0, 50));
        setSessions((prev) => [session!, ...prev]);
        setCurrentSession(session);
      } catch {
        setError('세션 생성에 실패했습니다.');
        return;
      }
    }

    // 사용자 메시지 즉시 표시
    const userMessage: ChatMessage = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content,
      law_references: null,
      risk_level: null,
      disclaimer_shown: false,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setIsStreaming(true);
    setStreamingContent('');
    setError(null);

    try {
      await chatApi.sendMessage(
        session.id,
        content,
        // onMessage
        (text) => {
          setStreamingContent((prev) => prev + text);
        },
        // onLawReference
        undefined,
        // onRiskLevel
        (level) => {
          if (level === 'HIGH' || level === 'EMERGENCY') {
            setShowAttorneyCTA(true);
          }
        },
        // onDone
        (data) => {
          // 스트리밍 완료 → 메시지 목록 갱신
          setStreamingContent('');
          setIsStreaming(false);

          // 세션 새로 로드하여 동기화
          chatApi.getSession(session!.id).then((detail) => {
            setMessages(detail.messages);
            setCurrentSession(detail.session);
            setSessions((prev) =>
              prev.map((s) => (s.id === session!.id ? detail.session : s))
            );
          });
        },
        // onError
        (err) => {
          setIsStreaming(false);
          setStreamingContent('');
          setError(err.message);
        },
      );
    } catch (err: any) {
      setIsStreaming(false);
      setStreamingContent('');
      setError(err.message || '메시지 전송에 실패했습니다.');
    }
  }, [currentSession]);

  // FAQ 선택 시 메시지 전송
  const handleFAQSelect = useCallback((question: string) => {
    sendMessage(question);
  }, [sendMessage]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-primary-600 animate-spin" />
      </div>
    );
  }

  return (
    <div className="h-[calc(100vh-64px)] flex bg-slate-50">
      {/* 사이드바 - 세션 목록 */}
      <aside
        className={`
          ${showSidebar ? 'w-72' : 'w-0'}
          flex-shrink-0 bg-white border-r border-slate-200
          transition-all duration-300 overflow-hidden
        `}
      >
        <div className="flex flex-col h-full w-72">
          {/* 사이드바 헤더 */}
          <div className="flex items-center justify-between px-4 py-3 border-b border-slate-200">
            <h2 className="text-sm font-semibold text-slate-900">대화 목록</h2>
            <button
              type="button"
              onClick={createNewSession}
              className="p-1.5 text-slate-500 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
              title="새 대화"
            >
              <Plus className="w-4 h-4" />
            </button>
          </div>

          {/* 세션 목록 */}
          <div className="flex-1 overflow-y-auto">
            {sessions.length === 0 ? (
              <div className="p-4 text-center text-sm text-slate-400">
                대화 기록이 없습니다.
              </div>
            ) : (
              sessions.map((session) => (
                <div
                  key={session.id}
                  className={`
                    flex items-center gap-2 px-4 py-3 cursor-pointer
                    border-b border-slate-100 group
                    ${currentSession?.id === session.id ? 'bg-primary-50' : 'hover:bg-slate-50'}
                  `}
                  onClick={() => selectSession(session)}
                >
                  <MessageSquare className="w-4 h-4 text-slate-400 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-slate-900 truncate">
                      {session.title || '새 대화'}
                    </p>
                    <p className="text-xs text-slate-400">
                      {session.message_count}개 메시지
                    </p>
                  </div>
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteSession(session.id);
                    }}
                    className="p-1 text-slate-300 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-all"
                    title="삭제"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              ))
            )}
          </div>
        </div>
      </aside>

      {/* 메인 채팅 영역 */}
      <main className="flex-1 flex flex-col min-w-0">
        {/* 채팅 헤더 */}
        <div className="flex items-center gap-3 px-4 py-3 bg-white border-b border-slate-200">
          <button
            type="button"
            onClick={() => setShowSidebar(!showSidebar)}
            className="p-1.5 text-slate-500 hover:text-slate-700 rounded-lg sm:hidden"
          >
            <ChevronLeft className="w-5 h-5" />
          </button>
          <div className="p-1.5 bg-primary-100 rounded-lg">
            <MessageSquare className="w-5 h-5 text-primary-600" />
          </div>
          <div className="flex-1">
            <h1 className="text-sm font-semibold text-slate-900">AI 노무 상담</h1>
            <p className="text-xs text-slate-500">
              {currentSession ? currentSession.title || '새 대화' : '질문을 시작하세요'}
            </p>
          </div>

          {/* 위험도 배지 */}
          {currentSession && currentSession.risk_level !== 'low' && (
            <span
              className={`text-xs font-medium px-2.5 py-1 rounded-full ${
                RISK_LEVEL_CONFIG[currentSession.risk_level]?.bgColor ?? 'bg-slate-100'
              } ${RISK_LEVEL_CONFIG[currentSession.risk_level]?.color ?? 'text-slate-600'}`}
            >
              {getRiskLabel(currentSession.risk_level)}
            </span>
          )}
        </div>

        {/* 에러 메시지 */}
        {error && (
          <div className="mx-4 mt-3 bg-red-50 border border-red-200 rounded-lg p-3 flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-red-600 flex-shrink-0" />
            <p className="text-sm text-red-700 flex-1">{error}</p>
            <button
              type="button"
              onClick={() => setError(null)}
              className="text-red-400 hover:text-red-600 text-xs"
            >
              닫기
            </button>
          </div>
        )}

        {/* 노무사 연결 CTA */}
        {showAttorneyCTA && (
          <div className="mx-4 mt-3 bg-amber-50 border border-amber-200 rounded-lg p-3 flex items-center gap-3">
            <PhoneCall className="w-5 h-5 text-amber-600 flex-shrink-0" />
            <div className="flex-1">
              <p className="text-sm font-medium text-amber-800">
                전문 노무사 상담을 권장합니다
              </p>
              <p className="text-xs text-amber-600 mt-0.5">
                이 사안은 법적 분쟁 가능성이 있어 전문가의 검토가 필요합니다.
              </p>
            </div>
          </div>
        )}

        {/* 메시지 목록 or FAQ */}
        {!currentSession && messages.length === 0 && !isStreaming ? (
          <div className="flex-1 overflow-y-auto">
            <div className="py-8 px-4 text-center">
              <MessageSquare className="w-12 h-12 text-primary-300 mx-auto mb-4" />
              <h2 className="text-lg font-medium text-slate-900 mb-2">
                AI 노무 비서에게 물어보세요
              </h2>
              <p className="text-sm text-slate-500 mb-6 max-w-md mx-auto">
                노동법, 급여 계산, 근로계약, 해고 절차 등 사업장 운영에 필요한
                모든 노무 관련 질문에 답변해 드립니다.
              </p>
            </div>
            {faqItems.length > 0 && (
              <FAQPanel items={faqItems} onSelect={handleFAQSelect} />
            )}
          </div>
        ) : (
          <MessageList
            messages={messages}
            streamingContent={streamingContent}
            isStreaming={isStreaming}
          />
        )}

        {/* 메시지 입력 */}
        <MessageInput
          onSend={sendMessage}
          isStreaming={isStreaming}
        />
      </main>
    </div>
  );
}
