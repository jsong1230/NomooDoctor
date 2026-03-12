'use client';

/**
 * 급여명세서 상세 보기 모달
 * 근로기준법 제48조 법정 기재사항 표시
 */

import type { Payslip } from '@/types/payslip';
import {
  formatCurrency,
  getSendStatusLabel,
  getSendStatusColor,
} from '@/types/payslip';
import { X, Download, Calendar, Building2, User } from 'lucide-react';

interface PayslipDetailModalProps {
  payslip: Payslip;
  onClose: () => void;
  onDownloadPdf: () => void;
}

export function PayslipDetailModal({
  payslip,
  onClose,
  onDownloadPdf,
}: PayslipDetailModalProps) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={onClose} />
      <div className="relative bg-white rounded-2xl shadow-xl max-w-lg w-full mx-4 max-h-[90vh] overflow-y-auto">
        {/* 헤더 */}
        <div className="sticky top-0 bg-white border-b border-slate-200 px-6 py-4 rounded-t-2xl flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-900">급여명세서</h2>
          <button
            type="button"
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 transition-colors"
            aria-label="닫기"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="px-6 py-5 space-y-6">
          {/* 기본 정보 */}
          <div className="grid grid-cols-2 gap-4">
            <div className="flex items-start gap-2">
              <User className="w-4 h-4 text-slate-400 mt-0.5" />
              <div>
                <p className="text-xs text-slate-500">근로자</p>
                <p className="text-sm font-medium text-slate-900">{payslip.employee_name}</p>
              </div>
            </div>
            <div className="flex items-start gap-2">
              <Building2 className="w-4 h-4 text-slate-400 mt-0.5" />
              <div>
                <p className="text-xs text-slate-500">사업장</p>
                <p className="text-sm font-medium text-slate-900">{payslip.company_name}</p>
              </div>
            </div>
            <div className="flex items-start gap-2">
              <Calendar className="w-4 h-4 text-slate-400 mt-0.5" />
              <div>
                <p className="text-xs text-slate-500">급여 기간</p>
                <p className="text-sm font-medium text-slate-900">
                  {payslip.year}년 {payslip.month}월
                </p>
              </div>
            </div>
            <div>
              <p className="text-xs text-slate-500">발송 상태</p>
              <p className={`text-sm font-medium ${getSendStatusColor(payslip.send_status)}`}>
                {getSendStatusLabel(payslip.send_status)}
              </p>
            </div>
          </div>

          {/* 지급 항목 */}
          <div>
            <h3 className="text-sm font-semibold text-slate-900 mb-3 flex items-center gap-2">
              <div className="w-1 h-4 bg-primary-600 rounded-full" />
              지급 항목
            </h3>
            <div className="bg-slate-50 rounded-lg p-4 space-y-2">
              <PayslipRow label="기본급" amount={payslip.base_salary} />
              <PayslipRow label="주휴수당" amount={payslip.weekly_allowance} />
              <PayslipRow label="연장수당" amount={payslip.overtime_pay} />
              <PayslipRow label="야간수당" amount={payslip.night_pay} />
              <PayslipRow label="휴일수당" amount={payslip.holiday_pay} />
              <PayslipRow label="식대" amount={payslip.meal_allowance} />
              <PayslipRow label="교통비" amount={payslip.transport_allowance} />
              <div className="border-t border-slate-200 pt-2 mt-2">
                <PayslipRow
                  label="지급 합계"
                  amount={payslip.total_payment}
                  highlight="primary"
                />
              </div>
            </div>
          </div>

          {/* 공제 항목 */}
          <div>
            <h3 className="text-sm font-semibold text-slate-900 mb-3 flex items-center gap-2">
              <div className="w-1 h-4 bg-red-500 rounded-full" />
              공제 항목
            </h3>
            <div className="bg-slate-50 rounded-lg p-4 space-y-2">
              <PayslipRow label="국민연금" amount={payslip.national_pension} />
              <PayslipRow label="건강보험" amount={payslip.health_insurance} />
              <PayslipRow label="장기요양보험" amount={payslip.long_term_care} />
              <PayslipRow label="고용보험" amount={payslip.employment_insurance} />
              <PayslipRow label="소득세" amount={payslip.income_tax} />
              <PayslipRow label="지방소득세" amount={payslip.local_income_tax} />
              <div className="border-t border-slate-200 pt-2 mt-2">
                <PayslipRow
                  label="공제 합계"
                  amount={payslip.total_deduction}
                  highlight="error"
                />
              </div>
            </div>
          </div>

          {/* 실수령액 */}
          <div className="bg-primary-50 border border-primary-200 rounded-xl p-5 text-center">
            <p className="text-sm text-primary-600 mb-1">실수령액</p>
            <p className="text-2xl font-bold text-primary-700">
              {formatCurrency(payslip.net_salary)}
            </p>
          </div>

          {/* 법적 고지 */}
          <p className="text-xs text-slate-400 text-center">
            본 명세서는 근로기준법 제48조에 의거하여 발급되었습니다.
          </p>
        </div>

        {/* 하단 버튼 */}
        <div className="sticky bottom-0 bg-white border-t border-slate-200 px-6 py-4 rounded-b-2xl flex gap-3">
          <button
            type="button"
            onClick={onClose}
            className="flex-1 px-4 py-2.5 text-slate-700 hover:bg-slate-100 rounded-lg font-medium transition-colors"
          >
            닫기
          </button>
          <button
            type="button"
            onClick={onDownloadPdf}
            className="flex-1 px-4 py-2.5 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 transition-colors flex items-center justify-center gap-2"
          >
            <Download className="w-4 h-4" />
            PDF 다운로드
          </button>
        </div>
      </div>
    </div>
  );
}

function PayslipRow({
  label,
  amount,
  highlight,
}: {
  label: string;
  amount: number;
  highlight?: 'primary' | 'error';
}) {
  const valueClass = highlight
    ? highlight === 'primary'
      ? 'font-semibold text-primary-700'
      : 'font-semibold text-red-600'
    : 'text-slate-900';

  return (
    <div className="flex items-center justify-between">
      <span className="text-sm text-slate-600">{label}</span>
      <span className={`text-sm ${valueClass}`}>{formatCurrency(amount)}</span>
    </div>
  );
}
