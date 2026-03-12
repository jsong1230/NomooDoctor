'use client';

/**
 * 채팅 메시지 입력 컴포넌트
 */

import { useState, useRef, useEffect } from 'react';
import { Send, Loader2 } from 'lucide-react';

interface MessageInputProps {
  onSend: (content: string) => void;
  isStreaming: boolean;
  disabled?: boolean;
}

export function MessageInput({ onSend, isStreaming, disabled }: MessageInputProps) {
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (!isStreaming && textareaRef.current) {
      textareaRef.current.focus();
    }
  }, [isStreaming]);

  const handleSubmit = () => {
    const trimmed = input.trim();
    if (!trimmed || isStreaming || disabled) return;
    onSend(trimmed);
    setInput('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    // 자동 높이 조정
    const el = e.target;
    el.style.height = 'auto';
    el.style.height = Math.min(el.scrollHeight, 120) + 'px';
  };

  return (
    <div className="border-t border-slate-200 bg-white px-4 py-3">
      <div className="flex items-end gap-2 max-w-3xl mx-auto">
        <textarea
          ref={textareaRef}
          value={input}
          onChange={handleInput}
          onKeyDown={handleKeyDown}
          placeholder="노동법 관련 질문을 입력하세요..."
          rows={1}
          disabled={isStreaming || disabled}
          className="
            flex-1 resize-none rounded-xl border border-slate-300 px-4 py-2.5
            text-sm text-slate-900 placeholder-slate-400
            focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent
            disabled:opacity-50 disabled:cursor-not-allowed
          "
          style={{ maxHeight: '120px' }}
        />
        <button
          type="button"
          onClick={handleSubmit}
          disabled={!input.trim() || isStreaming || disabled}
          className="
            p-2.5 bg-primary-600 text-white rounded-xl
            hover:bg-primary-700 transition-colors
            disabled:opacity-50 disabled:cursor-not-allowed
            flex-shrink-0
          "
          aria-label="전송"
        >
          {isStreaming ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <Send className="w-5 h-5" />
          )}
        </button>
      </div>
      <p className="text-xs text-slate-400 text-center mt-2">
        AI가 제공하는 일반적인 법률 정보이며, 법적 조언이 아닙니다.
      </p>
    </div>
  );
}
