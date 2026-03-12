'use client';

/**
 * 취업규칙 의무 안내 배너 컴포넌트
 * 10인 이상 사업장에 표시
 */

import { AlertTriangle, FileText, X } from 'lucide-react';
import { useState } from 'react';
import Link from 'next/link';

interface WorkRuleNoticeProps {
  employeeCount: number;
  onDismiss?: () => void;
  className?: string;
}

export function WorkRuleNotice({ employeeCount, onDismiss, className = '' }: WorkRuleNoticeProps) {
  const [isDismissed, setIsDismissed] = useState(false);

  // 10인 미만이거나 이미 닫힌 경우 표시하지 않음
  if (employeeCount < 10 || isDismissed) {
    return null;
  }

  const handleDismiss = () => {
    setIsDismissed(true);
    onDismiss?.();
  };

  return (
    <div
      data-testid="work-rule-notice"
      className={`
        bg-gradient-to-r from-warning-50 to-amber-50
        border border-warning-200 rounded-xl
        p-4
        flex items-start gap-3
        ${className}
      `}
    >
      <div className="p-2 bg-warning-100 rounded-lg flex-shrink-0">
        <AlertTriangle className="w-5 h-5 text-warning-600" />
      </div>
      <div className="flex-1 min-w-0">
        <h3 className="text-sm font-semibold text-warning-900 mb-1">
          취업규칙 작성이 필요합니다
        </h3>
        <p className="text-sm text-warning-800 leading-relaxed">
          근로기준법에 따라 10인 이상 사업장은 취업규칙 작성이 의무입니다.
          미작성 시 과태료가 부과될 수 있습니다.
        </p>
        <div className="flex items-center gap-3 mt-3">
          <Link
            href="/work-rules/new"
            className="
              inline-flex items-center gap-2
              px-4 py-2
              bg-warning-600 hover:bg-warning-700
              text-white text-sm font-medium
              rounded-lg
              transition-colors duration-200
            "
          >
            <FileText className="w-4 h-4" />
            취업규칙 작성하기
          </Link>
        </div>
      </div>
      <button
        type="button"
        onClick={handleDismiss}
        className="p-1 text-warning-400 hover:text-warning-600 transition-colors duration-200"
        aria-label="닫기"
      >
        <X className="w-5 h-5" />
      </button>
    </div>
  );
}
