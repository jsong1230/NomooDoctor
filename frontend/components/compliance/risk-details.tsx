'use client';

/**
 * 위반 항목 상세 목록 컴포넌트
 * 위반 항목 클릭 시 해결 방법을 안내
 */

import { useState } from 'react';
import {
  AlertTriangle,
  ChevronDown,
  ChevronUp,
  FileText,
  BookOpen,
  Receipt,
  ExternalLink,
} from 'lucide-react';
import type { RiskDeduction } from '@/types/compliance';

interface RiskDetailsProps {
  details: RiskDeduction[];
  score: number;
  level: string;
}

function getCategoryIcon(category: string) {
  switch (category) {
    case '근로계약서':
      return <FileText className="w-5 h-5" />;
    case '취업규칙':
      return <BookOpen className="w-5 h-5" />;
    case '급여명세서':
      return <Receipt className="w-5 h-5" />;
    default:
      return <AlertTriangle className="w-5 h-5" />;
  }
}

function getCategoryColor(category: string): {
  bg: string;
  text: string;
  border: string;
  iconBg: string;
} {
  switch (category) {
    case '근로계약서':
      return {
        bg: 'bg-orange-50',
        text: 'text-orange-700',
        border: 'border-orange-200',
        iconBg: 'bg-orange-100',
      };
    case '취업규칙':
      return {
        bg: 'bg-red-50',
        text: 'text-red-700',
        border: 'border-red-200',
        iconBg: 'bg-red-100',
      };
    case '급여명세서':
      return {
        bg: 'bg-yellow-50',
        text: 'text-yellow-700',
        border: 'border-yellow-200',
        iconBg: 'bg-yellow-100',
      };
    default:
      return {
        bg: 'bg-slate-50',
        text: 'text-slate-700',
        border: 'border-slate-200',
        iconBg: 'bg-slate-100',
      };
  }
}

function RiskDetailItem({ detail }: { detail: RiskDeduction }) {
  const [isExpanded, setIsExpanded] = useState(false);
  const colors = getCategoryColor(detail.category);

  return (
    <div
      className={`border ${colors.border} rounded-lg overflow-hidden transition-all duration-200`}
    >
      {/* 헤더 (클릭 영역) */}
      <button
        type="button"
        onClick={() => setIsExpanded(!isExpanded)}
        className={`w-full flex items-center gap-3 px-4 py-3 text-left hover:${colors.bg} transition-colors`}
      >
        <div className={`p-2 ${colors.iconBg} rounded-lg ${colors.text} flex-shrink-0`}>
          {getCategoryIcon(detail.category)}
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="text-sm font-semibold text-slate-900">
              {detail.category}
            </span>
            <span
              className={`text-xs font-medium px-2 py-0.5 rounded-full ${colors.bg} ${colors.text}`}
            >
              {detail.count}건
            </span>
          </div>
          <p className="text-sm text-slate-600 mt-0.5 truncate">
            {detail.message}
          </p>
        </div>

        <div className="flex items-center gap-3 flex-shrink-0">
          <span className="text-sm font-bold text-red-600">
            {detail.deduction}점
          </span>
          {isExpanded ? (
            <ChevronUp className="w-4 h-4 text-slate-400" />
          ) : (
            <ChevronDown className="w-4 h-4 text-slate-400" />
          )}
        </div>
      </button>

      {/* 확장 영역 (해결 방법) */}
      {isExpanded && (
        <div className={`px-4 py-3 ${colors.bg} border-t ${colors.border}`}>
          <div className="flex items-start gap-2">
            <ExternalLink className={`w-4 h-4 ${colors.text} mt-0.5 flex-shrink-0`} />
            <div>
              <div className={`text-xs font-semibold ${colors.text} uppercase tracking-wider mb-1`}>
                해결 방법
              </div>
              <p className="text-sm text-slate-700 leading-relaxed">
                {detail.resolution}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export function RiskDetails({ details, score, level }: RiskDetailsProps) {
  if (details.length === 0) {
    return (
      <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6">
        <h2 className="text-lg font-bold text-slate-900 mb-4">위반 항목</h2>
        <div className="text-center py-8">
          <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
            <AlertTriangle className="w-6 h-6 text-green-600" />
          </div>
          <p className="text-sm font-medium text-slate-900">
            위반 항목이 없습니다
          </p>
          <p className="text-xs text-slate-500 mt-1">
            모든 노무 컴플라이언스를 준수하고 있습니다.
          </p>
        </div>
      </div>
    );
  }

  const totalDeduction = details.reduce((sum, d) => sum + d.deduction, 0);

  return (
    <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-bold text-slate-900">위반 항목</h2>
        <span className="text-sm text-red-600 font-medium">
          총 감점: {totalDeduction}점
        </span>
      </div>

      <p className="text-sm text-slate-500 mb-4">
        항목을 클릭하면 해결 방법을 확인할 수 있습니다.
      </p>

      <div className="space-y-3">
        {details.map((detail, idx) => (
          <RiskDetailItem key={idx} detail={detail} />
        ))}
      </div>
    </div>
  );
}
