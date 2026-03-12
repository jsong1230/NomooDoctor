'use client';

/**
 * 리스크 스코어 카드 컴포넌트
 * 큰 숫자 + 색상 배경으로 리스크 스코어를 표현
 */

import { Shield, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import type { RiskScoreResponse, RiskLevel } from '@/types/compliance';
import { RISK_LEVEL_CONFIG, getRiskLevelLabel } from '@/types/compliance';

interface RiskScoreCardProps {
  scoreData: RiskScoreResponse;
}

function getScoreBgClass(level: RiskLevel): string {
  switch (level) {
    case 'green':
      return 'bg-gradient-to-br from-green-500 to-green-600';
    case 'yellow':
      return 'bg-gradient-to-br from-yellow-400 to-yellow-500';
    case 'red':
      return 'bg-gradient-to-br from-red-500 to-red-600';
  }
}

function getScoreTextClass(level: RiskLevel): string {
  switch (level) {
    case 'green':
      return 'text-white';
    case 'yellow':
      return 'text-yellow-900';
    case 'red':
      return 'text-white';
  }
}

export function RiskScoreCard({ scoreData }: RiskScoreCardProps) {
  const { score, level, total_employees, details } = scoreData;
  const bgClass = getScoreBgClass(level);
  const textClass = getScoreTextClass(level);
  const levelConfig = RISK_LEVEL_CONFIG[level];

  return (
    <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
      {/* 스코어 표시 영역 */}
      <div className={`${bgClass} px-6 py-8`}>
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <Shield className={`w-5 h-5 ${textClass} opacity-80`} />
              <span className={`text-sm font-medium ${textClass} opacity-80`}>
                컴플라이언스 스코어
              </span>
            </div>
            <div className={`text-6xl font-bold ${textClass} tracking-tight`}>
              {score}
            </div>
            <div className={`text-sm ${textClass} opacity-80 mt-1`}>
              / 100점
            </div>
          </div>
          <div className="text-right">
            <span
              className={`
                inline-flex items-center gap-1 px-3 py-1.5 rounded-full text-sm font-semibold
                ${level === 'yellow' ? 'bg-yellow-600/20 text-yellow-900' : 'bg-white/20 ' + textClass}
              `}
            >
              {getRiskLevelLabel(level)}
            </span>
          </div>
        </div>
      </div>

      {/* 요약 정보 */}
      <div className="px-6 py-4">
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-slate-900">
              {total_employees}
            </div>
            <div className="text-xs text-slate-500 mt-0.5">활성 직원</div>
          </div>
          <div className="text-center border-x border-slate-100">
            <div className="text-2xl font-bold text-slate-900">
              {scoreData.employees_without_contract}
            </div>
            <div className="text-xs text-slate-500 mt-0.5">계약서 미작성</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-slate-900">
              {scoreData.employees_without_payslip}
            </div>
            <div className="text-xs text-slate-500 mt-0.5">명세서 미발송</div>
          </div>
        </div>

        {/* 감점 요약 */}
        {details.length > 0 && (
          <div className="mt-4 pt-4 border-t border-slate-100">
            <div className="text-xs font-medium text-slate-500 uppercase tracking-wider mb-2">
              감점 항목 {details.length}건
            </div>
            <div className="space-y-1">
              {details.map((d, idx) => (
                <div key={idx} className="flex items-center justify-between text-sm">
                  <span className="text-slate-600">{d.category}</span>
                  <span className="font-medium text-red-600">{d.deduction}점</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {details.length === 0 && (
          <div className="mt-4 pt-4 border-t border-slate-100">
            <p className="text-sm text-green-600 font-medium text-center">
              모든 컴플라이언스 항목을 준수하고 있습니다.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
