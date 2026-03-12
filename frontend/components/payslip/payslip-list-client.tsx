'use client';

/**
 * 급여명세서 목록 클라이언트 컴포넌트
 */

import { useState, useEffect, useCallback } from 'react';
import { payslipApi } from '@/lib/api/payslip';
import { payslipStore } from '@/lib/stores/payslip-store';
import type { Payslip } from '@/types/payslip';
import {
  formatCurrency,
  getSendStatusLabel,
  getSendStatusColor,
} from '@/types/payslip';
import { SendPayslipDialog } from './send-payslip-dialog';
import { PayslipDetailModal } from './payslip-detail-modal';
import {
  Receipt,
  Loader2,
  AlertCircle,
  Download,
  Send,
  Eye,
  ChevronDown,
  Search,
  FileText,
} from 'lucide-react';

export function PayslipListClient() {
  const [payslips, setPayslips] = useState<Payslip[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // 필터
  const [filterYear, setFilterYear] = useState<number>(new Date().getFullYear());
  const [filterMonth, setFilterMonth] = useState<number | undefined>(undefined);

  // 모달
  const [selectedPayslip, setSelectedPayslip] = useState<Payslip | null>(null);
  const [showDetail, setShowDetail] = useState(false);
  const [showSendDialog, setShowSendDialog] = useState(false);

  const loadPayslips = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const data = await payslipApi.listPayslips({
        year: filterYear,
        month: filterMonth,
      });
      setPayslips(data);
      payslipStore.getState().setPayslips(data);
    } catch (err: any) {
      const errorMessage =
        err.response?.data?.error?.message ||
        err.message ||
        '급여명세서 목록을 불러오는데 실패했습니다.';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, [filterYear, filterMonth]);

  useEffect(() => {
    loadPayslips();
  }, [loadPayslips]);

  const handleDownloadPdf = async (payslip: Payslip) => {
    try {
      const blob = await payslipApi.downloadPayslipPdf(payslip.id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `급여명세서_${payslip.employee_name}_${payslip.year}년${payslip.month}월.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      alert('PDF 다운로드에 실패했습니다.');
    }
  };

  const handleSendComplete = (updatedPayslip: Payslip) => {
    setPayslips((prev) =>
      prev.map((p) => (p.id === updatedPayslip.id ? updatedPayslip : p))
    );
    payslipStore.getState().updatePayslip(updatedPayslip.id, updatedPayslip);
    setShowSendDialog(false);
  };

  const currentYear = new Date().getFullYear();
  const years = Array.from({ length: 5 }, (_, i) => currentYear - i);
  const months = Array.from({ length: 12 }, (_, i) => i + 1);

  if (isLoading && payslips.length === 0) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-primary-600 animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="max-w-6xl mx-auto px-4 py-8 sm:px-6 sm:py-12">
        {/* 페이지 헤더 */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-primary-100 rounded-lg">
              <Receipt className="w-6 h-6 text-primary-600" />
            </div>
            <h1 className="text-2xl font-bold text-slate-900">급여명세서</h1>
          </div>
          <p className="text-slate-600">
            급여명세서를 조회하고 직원에게 발송합니다.
          </p>
        </div>

        {/* 필터 바 */}
        <div className="bg-white border border-slate-200 rounded-xl p-4 mb-6 shadow-sm">
          <div className="flex flex-wrap items-center gap-4">
            {/* 연도 선택 */}
            <div className="relative">
              <select
                value={filterYear}
                onChange={(e) => setFilterYear(Number(e.target.value))}
                className="
                  appearance-none bg-white border border-slate-300 rounded-lg
                  px-4 py-2 pr-8 text-sm text-slate-900
                  focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent
                "
              >
                {years.map((y) => (
                  <option key={y} value={y}>
                    {y}년
                  </option>
                ))}
              </select>
              <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none" />
            </div>

            {/* 월 선택 */}
            <div className="relative">
              <select
                value={filterMonth ?? ''}
                onChange={(e) =>
                  setFilterMonth(
                    e.target.value ? Number(e.target.value) : undefined
                  )
                }
                className="
                  appearance-none bg-white border border-slate-300 rounded-lg
                  px-4 py-2 pr-8 text-sm text-slate-900
                  focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent
                "
              >
                <option value="">전체 월</option>
                {months.map((m) => (
                  <option key={m} value={m}>
                    {m}월
                  </option>
                ))}
              </select>
              <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none" />
            </div>

            {/* 건수 표시 */}
            <span className="text-sm text-slate-500">
              총 {payslips.length}건
            </span>
          </div>
        </div>

        {/* 에러 메시지 */}
        {error && (
          <div className="bg-error-50 border border-error-200 rounded-xl p-4 mb-6 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-error-600 flex-shrink-0 mt-0.5" />
            <p className="text-sm text-error-700">{error}</p>
          </div>
        )}

        {/* 급여명세서 목록 */}
        {payslips.length === 0 && !isLoading ? (
          <div className="bg-white border border-slate-200 rounded-xl p-12 text-center shadow-sm">
            <FileText className="w-12 h-12 text-slate-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-slate-900 mb-2">
              급여명세서가 없습니다
            </h3>
            <p className="text-sm text-slate-500">
              급여 계산 후 급여명세서를 생성할 수 있습니다.
            </p>
          </div>
        ) : (
          <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
            {/* 테이블 헤더 */}
            <div className="hidden sm:grid sm:grid-cols-[1fr_80px_120px_120px_100px_120px] gap-4 px-6 py-3 bg-slate-50 border-b border-slate-200 text-xs font-medium text-slate-500 uppercase tracking-wider">
              <div>직원</div>
              <div>기간</div>
              <div className="text-right">지급 합계</div>
              <div className="text-right">실수령액</div>
              <div className="text-center">발송 상태</div>
              <div className="text-center">관리</div>
            </div>

            {/* 테이블 바디 */}
            {payslips.map((payslip) => (
              <div
                key={payslip.id}
                className="
                  grid grid-cols-1 sm:grid-cols-[1fr_80px_120px_120px_100px_120px]
                  gap-2 sm:gap-4 px-6 py-4
                  border-b border-slate-100 last:border-b-0
                  hover:bg-slate-50 transition-colors duration-150
                "
              >
                {/* 직원 */}
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center text-sm font-medium text-primary-700">
                    {payslip.employee_name.charAt(0)}
                  </div>
                  <span className="text-sm font-medium text-slate-900">
                    {payslip.employee_name}
                  </span>
                </div>

                {/* 기간 */}
                <div className="flex items-center text-sm text-slate-600">
                  {payslip.month}월
                </div>

                {/* 지급 합계 */}
                <div className="flex items-center justify-end text-sm text-slate-900 font-medium">
                  {formatCurrency(payslip.total_payment)}
                </div>

                {/* 실수령액 */}
                <div className="flex items-center justify-end text-sm font-semibold text-primary-700">
                  {formatCurrency(payslip.net_salary)}
                </div>

                {/* 발송 상태 */}
                <div className="flex items-center justify-center">
                  <span
                    className={`text-xs font-medium px-2.5 py-1 rounded-full ${
                      payslip.send_status === 'sent'
                        ? 'bg-green-100 text-green-700'
                        : payslip.send_status === 'failed'
                          ? 'bg-red-100 text-red-700'
                          : 'bg-slate-100 text-slate-600'
                    }`}
                  >
                    {getSendStatusLabel(payslip.send_status)}
                  </span>
                </div>

                {/* 관리 버튼 */}
                <div className="flex items-center justify-center gap-1">
                  <button
                    type="button"
                    onClick={() => {
                      setSelectedPayslip(payslip);
                      setShowDetail(true);
                    }}
                    className="p-1.5 text-slate-400 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                    title="상세 보기"
                  >
                    <Eye className="w-4 h-4" />
                  </button>
                  <button
                    type="button"
                    onClick={() => handleDownloadPdf(payslip)}
                    className="p-1.5 text-slate-400 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                    title="PDF 다운로드"
                  >
                    <Download className="w-4 h-4" />
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setSelectedPayslip(payslip);
                      setShowSendDialog(true);
                    }}
                    className="p-1.5 text-slate-400 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                    title="발송"
                    disabled={payslip.send_status === 'sent'}
                  >
                    <Send className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 상세 보기 모달 */}
      {showDetail && selectedPayslip && (
        <PayslipDetailModal
          payslip={selectedPayslip}
          onClose={() => {
            setShowDetail(false);
            setSelectedPayslip(null);
          }}
          onDownloadPdf={() => handleDownloadPdf(selectedPayslip)}
        />
      )}

      {/* 발송 다이얼로그 */}
      {showSendDialog && selectedPayslip && (
        <SendPayslipDialog
          payslip={selectedPayslip}
          onClose={() => {
            setShowSendDialog(false);
            setSelectedPayslip(null);
          }}
          onSendComplete={handleSendComplete}
        />
      )}
    </div>
  );
}
