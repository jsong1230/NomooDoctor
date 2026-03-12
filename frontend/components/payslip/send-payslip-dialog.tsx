'use client';

/**
 * 급여명세서 발송 다이얼로그
 */

import { useState } from 'react';
import { payslipApi } from '@/lib/api/payslip';
import type { Payslip, SendMethod } from '@/types/payslip';
import { formatCurrency } from '@/types/payslip';
import { X, Send, Mail, MessageSquare, Loader2, CheckCircle, AlertCircle } from 'lucide-react';

interface SendPayslipDialogProps {
  payslip: Payslip;
  onClose: () => void;
  onSendComplete: (updatedPayslip: Payslip) => void;
}

export function SendPayslipDialog({
  payslip,
  onClose,
  onSendComplete,
}: SendPayslipDialogProps) {
  const [method, setMethod] = useState<SendMethod>('email');
  const [email, setEmail] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [sendResult, setSendResult] = useState<'success' | 'error' | null>(null);
  const [errorMessage, setErrorMessage] = useState('');

  const handleSend = async () => {
    setIsSending(true);
    setSendResult(null);
    setErrorMessage('');

    try {
      const updatedPayslip = await payslipApi.sendPayslip(payslip.id, {
        method,
        email: email || undefined,
      });
      setSendResult('success');
      setTimeout(() => {
        onSendComplete(updatedPayslip);
      }, 1500);
    } catch (err: any) {
      setSendResult('error');
      setErrorMessage(
        err.response?.data?.error?.message ||
        err.message ||
        '발송에 실패했습니다.'
      );
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={onClose} />
      <div className="relative bg-white rounded-2xl shadow-xl max-w-md w-full mx-4 p-6">
        {/* 닫기 버튼 */}
        <button
          type="button"
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-slate-600"
          aria-label="닫기"
        >
          <X className="w-5 h-5" />
        </button>

        {/* 제목 */}
        <div className="flex items-start gap-3 mb-5">
          <div className="p-2 bg-primary-100 rounded-lg">
            <Send className="w-5 h-5 text-primary-600" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-slate-900">급여명세서 발송</h3>
            <p className="text-sm text-slate-600 mt-1">
              {payslip.employee_name} - {payslip.year}년 {payslip.month}월 ({formatCurrency(payslip.net_salary)})
            </p>
          </div>
        </div>

        {/* 성공 메시지 */}
        {sendResult === 'success' && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-center gap-3 mb-4">
            <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0" />
            <p className="text-sm text-green-700">급여명세서가 발송되었습니다.</p>
          </div>
        )}

        {/* 에러 메시지 */}
        {sendResult === 'error' && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center gap-3 mb-4">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0" />
            <p className="text-sm text-red-700">{errorMessage}</p>
          </div>
        )}

        {!sendResult && (
          <>
            {/* 발송 방법 선택 */}
            <div className="mb-5">
              <label className="text-sm font-medium text-slate-700 mb-3 block">
                발송 방법
              </label>
              <div className="grid grid-cols-3 gap-3">
                <button
                  type="button"
                  onClick={() => setMethod('email')}
                  className={`
                    flex flex-col items-center gap-2 p-3 rounded-xl border-2 transition-all
                    ${method === 'email'
                      ? 'border-primary-500 bg-primary-50 text-primary-700'
                      : 'border-slate-200 text-slate-600 hover:border-slate-300'}
                  `}
                >
                  <Mail className="w-5 h-5" />
                  <span className="text-xs font-medium">이메일</span>
                </button>
                <button
                  type="button"
                  onClick={() => setMethod('kakao')}
                  className={`
                    flex flex-col items-center gap-2 p-3 rounded-xl border-2 transition-all
                    ${method === 'kakao'
                      ? 'border-primary-500 bg-primary-50 text-primary-700'
                      : 'border-slate-200 text-slate-600 hover:border-slate-300'}
                  `}
                >
                  <MessageSquare className="w-5 h-5" />
                  <span className="text-xs font-medium">알림톡</span>
                </button>
                <button
                  type="button"
                  onClick={() => setMethod('both')}
                  className={`
                    flex flex-col items-center gap-2 p-3 rounded-xl border-2 transition-all
                    ${method === 'both'
                      ? 'border-primary-500 bg-primary-50 text-primary-700'
                      : 'border-slate-200 text-slate-600 hover:border-slate-300'}
                  `}
                >
                  <Send className="w-5 h-5" />
                  <span className="text-xs font-medium">둘 다</span>
                </button>
              </div>
            </div>

            {/* 이메일 입력 (이메일 발송 시) */}
            {(method === 'email' || method === 'both') && (
              <div className="mb-5">
                <label
                  htmlFor="send-email"
                  className="text-sm font-medium text-slate-700 mb-2 block"
                >
                  이메일 주소 (선택)
                </label>
                <input
                  id="send-email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="직원 등록 이메일로 발송됩니다"
                  className="
                    w-full px-3 py-2.5 border border-slate-300 rounded-lg
                    text-sm text-slate-900 placeholder-slate-400
                    focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent
                  "
                />
                <p className="text-xs text-slate-500 mt-1">
                  비워두면 직원 등록 이메일로 발송됩니다.
                </p>
              </div>
            )}

            {/* 발송 버튼 */}
            <div className="flex gap-3">
              <button
                type="button"
                onClick={onClose}
                className="flex-1 px-4 py-2.5 text-slate-700 hover:bg-slate-100 rounded-lg font-medium transition-colors"
              >
                취소
              </button>
              <button
                type="button"
                onClick={handleSend}
                disabled={isSending}
                className="flex-1 px-4 py-2.5 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {isSending ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    발송 중...
                  </>
                ) : (
                  <>
                    <Send className="w-4 h-4" />
                    발송
                  </>
                )}
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
