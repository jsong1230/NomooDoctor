'use client';

/**
 * 월별 요약 카드 컴포넌트
 */

import { Users, Clock, AlertCircle } from 'lucide-react';
import type { MonthlySummary } from '@/types/attendance';

interface MonthlySummaryProps {
  summary: MonthlySummary;
}

/**
 * 분을 시간으로 변환하는 함수
 */
function minutesToHours(minutes: number): string {
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  if (mins === 0) {
    return `${hours}시간`;
  }
  return `${hours}시간 ${mins}분`;
}

export function MonthlySummaryComponent({ summary }: MonthlySummaryProps) {
  return (
    <div className="space-y-6">
      {/* 회사 전체 통계 */}
      <div className="p-6 bg-gradient-to-br from-slate-50 to-slate-100 border border-slate-200 rounded-lg">
        <h3 className="text-lg font-semibold text-slate-900 mb-4">사업장 전체 통계</h3>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div className="text-center p-3 bg-white rounded-lg border border-slate-200">
            <div className="text-sm text-slate-600">직원 수</div>
            <div className="text-2xl font-bold text-slate-900 mt-1">
              {summary.company_total.total_employees}명
            </div>
          </div>

          <div className="text-center p-3 bg-white rounded-lg border border-slate-200">
            <div className="text-sm text-slate-600">일평균 근무시간</div>
            <div className="text-2xl font-bold text-slate-900 mt-1">
              {Math.floor(summary.company_total.avg_work_minutes_per_day / 60)}시간
            </div>
          </div>

          <div className="text-center p-3 bg-white rounded-lg border border-slate-200">
            <div className="text-sm text-slate-600">총 연장근무</div>
            <div className="text-2xl font-bold text-warning-600 mt-1">
              {minutesToHours(summary.company_total.total_overtime_minutes)}
            </div>
          </div>

          <div className="text-center p-3 bg-white rounded-lg border border-slate-200">
            <div className="text-sm text-slate-600">총 야간근무</div>
            <div className="text-2xl font-bold text-indigo-600 mt-1">
              {minutesToHours(summary.company_total.total_night_minutes)}
            </div>
          </div>

          <div className="text-center p-3 bg-white rounded-lg border border-slate-200">
            <div className="text-sm text-slate-600">총 휴일근무</div>
            <div className="text-2xl font-bold text-error-600 mt-1">
              {minutesToHours(summary.company_total.total_holiday_minutes)}
            </div>
          </div>
        </div>
      </div>

      {/* 직원별 요약 테이블 */}
      <div>
        <h3 className="text-lg font-semibold text-slate-900 mb-4">직원별 요약</h3>
        <div className="w-full overflow-x-auto border rounded-lg">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b bg-slate-50">
                <th className="px-4 py-3 text-left font-medium text-slate-700">직원명</th>
                <th className="px-4 py-3 text-center font-medium text-slate-700">근무일</th>
                <th className="px-4 py-3 text-center font-medium text-slate-700">총 근무</th>
                <th className="px-4 py-3 text-center font-medium text-slate-700">연장</th>
                <th className="px-4 py-3 text-center font-medium text-slate-700">야간</th>
                <th className="px-4 py-3 text-center font-medium text-slate-700">휴일</th>
                <th className="px-4 py-3 text-center font-medium text-slate-700">지각</th>
                <th className="px-4 py-3 text-center font-medium text-slate-700">조퇴</th>
                <th className="px-4 py-3 text-center font-medium text-slate-700">결근</th>
              </tr>
            </thead>
            <tbody>
              {summary.employees.length === 0 ? (
                <tr>
                  <td colSpan={9} className="px-4 py-8 text-center text-slate-500">
                    직원 데이터가 없습니다
                  </td>
                </tr>
              ) : (
                summary.employees.map((emp) => (
                  <tr key={emp.employee_id} className="border-b hover:bg-slate-50 transition-colors">
                    <td className="px-4 py-3">
                      <div className="font-medium text-slate-900">{emp.employee_name}</div>
                      <div className="text-xs text-slate-500">{emp.employment_type}</div>
                    </td>
                    <td className="px-4 py-3 text-center text-slate-700">
                      {emp.total_work_days}일
                    </td>
                    <td className="px-4 py-3 text-center text-slate-700">
                      {minutesToHours(emp.total_work_minutes)}
                    </td>
                    <td className="px-4 py-3 text-center">
                      {emp.total_overtime_minutes > 0 ? (
                        <span className="font-semibold text-warning-600">
                          {minutesToHours(emp.total_overtime_minutes)}
                        </span>
                      ) : (
                        <span className="text-slate-400">-</span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-center">
                      {emp.total_night_minutes > 0 ? (
                        <span className="font-semibold text-indigo-600">
                          {minutesToHours(emp.total_night_minutes)}
                        </span>
                      ) : (
                        <span className="text-slate-400">-</span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-center">
                      {emp.total_holiday_minutes > 0 ? (
                        <span className="font-semibold text-error-600">
                          {minutesToHours(emp.total_holiday_minutes)}
                        </span>
                      ) : (
                        <span className="text-slate-400">-</span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-center">
                      {emp.late_count > 0 ? (
                        <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-yellow-100 text-yellow-700 font-semibold text-xs">
                          {emp.late_count}
                        </span>
                      ) : (
                        <span className="text-slate-400">-</span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-center">
                      {emp.early_leave_count > 0 ? (
                        <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-orange-100 text-orange-700 font-semibold text-xs">
                          {emp.early_leave_count}
                        </span>
                      ) : (
                        <span className="text-slate-400">-</span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-center">
                      {emp.absent_count > 0 ? (
                        <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-error-100 text-error-700 font-semibold text-xs">
                          {emp.absent_count}
                        </span>
                      ) : (
                        <span className="text-slate-400">-</span>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
