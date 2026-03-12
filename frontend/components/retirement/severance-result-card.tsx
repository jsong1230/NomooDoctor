'use client';

/**
 * 퇴직금 계산 결과 카드 컴포넌트
 * 금액 breakdown과 상세 정보 표시
 */

import { ChevronDown, ChevronUp } from 'lucide-react';
import { useState } from 'react';
import type { SeveranceResult } from '@/types/retirement';

interface SeveranceResultCardProps {
  result: SeveranceResult;
  onSave?: () => void;
  isSaving?: boolean;
}

export function SeveranceResultCard({
  result,
  onSave,
  isSaving = false
}: SeveranceResultCardProps) {
  const [isDetailsOpen, setIsDetailsOpen] = useState(false);

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const formatCurrency = (amount: number) => {
    return amount.toLocaleString('ko-KR');
  };

  return (
    <div className="border border-gray-200 rounded-lg bg-white overflow-hidden">
      {/* 헤더 */}
      <div className="bg-gradient-to-r from-blue-50 to-blue-100 border-b border-blue-200 p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-2">
          {result.employee_name}
        </h3>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <p className="text-gray-600">입사일</p>
            <p className="font-medium text-gray-900">{formatDate(result.hire_date)}</p>
          </div>
          <div>
            <p className="text-gray-600">퇴직예정일</p>
            <p className="font-medium text-gray-900">{formatDate(result.resign_date)}</p>
          </div>
          <div>
            <p className="text-gray-600">재직기간</p>
            <p className="font-medium text-gray-900">{result.total_service_days}일</p>
          </div>
          <div>
            <p className="text-gray-600">적격 여부</p>
            <p className={`font-medium ${result.eligible ? 'text-green-600' : 'text-red-600'}`}>
              {result.eligible ? '수급 자격 있음' : '수급 자격 없음'}
            </p>
          </div>
        </div>
      </div>

      {/* 메인 계산 결과 */}
      <div className="p-6 space-y-6">
        {/* 총 지급액 */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-sm text-gray-600 mb-1">총 지급액</p>
          <p className="text-4xl font-bold text-blue-600">
            {formatCurrency(result.total_payment)}
            <span className="text-lg ml-1">원</span>
          </p>
          <p className="text-sm text-gray-500 mt-2">
            지급 기한: {formatDate(result.payment_deadline)}
          </p>
        </div>

        {/* 항목별 금액 */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="border border-gray-200 rounded-lg p-4">
            <p className="text-sm text-gray-600 mb-2">퇴직금</p>
            <p className="text-2xl font-bold text-gray-900">
              {formatCurrency(result.severance_pay)}
              <span className="text-sm ml-1">원</span>
            </p>
          </div>

          <div className="border border-gray-200 rounded-lg p-4">
            <p className="text-sm text-gray-600 mb-2">연차미사용수당</p>
            <p className="text-2xl font-bold text-gray-900">
              {formatCurrency(result.unused_leave_pay)}
              <span className="text-sm ml-1">원</span>
            </p>
          </div>

          <div className="border border-gray-200 rounded-lg p-4">
            <p className="text-sm text-gray-600 mb-2">상여금 포함분</p>
            <p className="text-2xl font-bold text-gray-900">
              {formatCurrency(result.bonus_included)}
              <span className="text-sm ml-1">원</span>
            </p>
          </div>

          <div className="border border-gray-200 rounded-lg p-4">
            <p className="text-sm text-gray-600 mb-2">일평균임금</p>
            <p className="text-2xl font-bold text-gray-900">
              {formatCurrency(result.average_daily_wage)}
              <span className="text-sm ml-1">원</span>
            </p>
          </div>
        </div>

        {/* 상세 계산 정보 */}
        <div className="border border-gray-200 rounded-lg overflow-hidden">
          <button
            onClick={() => setIsDetailsOpen(!isDetailsOpen)}
            className="w-full px-4 py-3 flex justify-between items-center hover:bg-gray-50 transition"
          >
            <span className="font-medium text-gray-900">계산 상세 내역</span>
            {isDetailsOpen ? (
              <ChevronUp className="w-5 h-5 text-gray-600" />
            ) : (
              <ChevronDown className="w-5 h-5 text-gray-600" />
            )}
          </button>

          {isDetailsOpen && (
            <div className="border-t border-gray-200 bg-gray-50 p-4 space-y-3">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-gray-600">최근 3개월 임금합계</p>
                  <p className="font-medium text-gray-900">
                    {formatCurrency(result.calculation_detail.last_3_months_total_wage)}원
                  </p>
                </div>
                <div>
                  <p className="text-gray-600">최근 3개월 총 일수</p>
                  <p className="font-medium text-gray-900">
                    {result.calculation_detail.last_3_months_total_days}일
                  </p>
                </div>
                <div>
                  <p className="text-gray-600">상여금 3/12</p>
                  <p className="font-medium text-gray-900">
                    {formatCurrency(result.calculation_detail.bonus_3_months_share)}원
                  </p>
                </div>
                <div>
                  <p className="text-gray-600">계산된 일평균임금</p>
                  <p className="font-medium text-gray-900">
                    {formatCurrency(result.calculation_detail.average_daily_wage)}원
                  </p>
                </div>
              </div>

              <div className="border-t border-gray-300 pt-3 mt-3">
                <p className="text-xs text-gray-500 mb-2">퇴직금 계산식</p>
                <p className="font-mono text-xs bg-white p-2 border border-gray-200 rounded text-gray-700">
                  {result.calculation_detail.severance_formula}
                </p>
              </div>

              <div>
                <p className="text-xs text-gray-500 mb-2">연차미사용수당 계산식</p>
                <p className="font-mono text-xs bg-white p-2 border border-gray-200 rounded text-gray-700">
                  {result.calculation_detail.unused_leave_formula}
                </p>
              </div>
            </div>
          )}
        </div>

        {/* 저장 버튼 */}
        {onSave && (
          <button
            onClick={onSave}
            disabled={isSaving}
            className="w-full px-4 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:bg-blue-400 transition"
          >
            {isSaving ? '저장 중...' : '퇴직금 확정 저장'}
          </button>
        )}
      </div>
    </div>
  );
}
