'use client';

/**
 * 패턴 분석 차트 컴포넌트
 * 간단한 bar 차트 형태의 시각화
 */

import { AlertCircle } from 'lucide-react';
import type { EmployeeAnalysis } from '@/types/attendance';

interface AnalysisChartProps {
  analysis: EmployeeAnalysis;
}

/**
 * 분을 시간으로 변환
 */
function minutesToHours(minutes: number): string {
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  if (mins === 0) {
    return `${hours}h`;
  }
  return `${hours}h ${mins}m`;
}

/**
 * 최대값 기준 백분율 계산
 */
function getPercentage(value: number, max: number): number {
  if (max === 0) return 0;
  return (value / max) * 100;
}

export function AnalysisChart({ analysis }: AnalysisChartProps) {
  const overtimeTrend = analysis.pattern.overtime_trend;
  const weekdayDist = analysis.pattern.weekday_distribution;

  // 차트 최대값 계산
  const maxOvertime = Math.max(...overtimeTrend.map((t) => t.total_minutes), 1);
  const maxWeekday = Math.max(...Object.values(weekdayDist), 1);

  // 요일명
  const weekdayLabels: Record<string, string> = {
    mon: '월',
    tue: '화',
    wed: '수',
    thu: '목',
    fri: '금',
    sat: '토',
    sun: '일',
  };

  return (
    <div className="space-y-8">
      {/* 기본 패턴 정보 */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="p-4 bg-slate-50 border border-slate-200 rounded-lg">
          <div className="text-sm text-slate-600">평균 출근시간</div>
          <div className="text-2xl font-bold text-slate-900 mt-1">
            {analysis.pattern.avg_start_time}
          </div>
        </div>

        <div className="p-4 bg-slate-50 border border-slate-200 rounded-lg">
          <div className="text-sm text-slate-600">평균 퇴근시간</div>
          <div className="text-2xl font-bold text-slate-900 mt-1">
            {analysis.pattern.avg_end_time}
          </div>
        </div>

        <div className="p-4 bg-slate-50 border border-slate-200 rounded-lg">
          <div className="text-sm text-slate-600">일평균 근무</div>
          <div className="text-2xl font-bold text-slate-900 mt-1">
            {minutesToHours(analysis.pattern.avg_work_minutes_per_day)}
          </div>
        </div>

        <div className="p-4 bg-slate-50 border border-slate-200 rounded-lg">
          <div className="text-sm text-slate-600">월평균 연장</div>
          <div className="text-2xl font-bold text-warning-600 mt-1">
            {minutesToHours(analysis.pattern.avg_overtime_minutes_per_month)}
          </div>
        </div>
      </div>

      {/* 연장근무 추세 차트 */}
      <div>
        <h3 className="text-lg font-semibold text-slate-900 mb-4">연장근무 추세</h3>
        <div className="space-y-3">
          {overtimeTrend.map((trend) => (
            <div key={`${trend.year}-${trend.month}`} className="flex items-center gap-4">
              <div className="w-20 text-sm font-medium text-slate-700">
                {trend.year}년 {trend.month}월
              </div>
              <div className="flex-1 bg-slate-200 rounded-full h-8 relative overflow-hidden">
                <div
                  className="bg-warning-500 h-full rounded-full transition-all duration-300 flex items-center justify-end pr-3"
                  style={{
                    width: `${getPercentage(trend.total_minutes, maxOvertime)}%`,
                  }}
                >
                  {trend.total_minutes > 0 && (
                    <span className="text-xs font-semibold text-white">
                      {minutesToHours(trend.total_minutes)}
                    </span>
                  )}
                </div>
              </div>
              <div className="w-20 text-right text-sm text-slate-600">
                {minutesToHours(trend.total_minutes)}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 요일별 분포 차트 */}
      <div>
        <h3 className="text-lg font-semibold text-slate-900 mb-4">요일별 근무 분포</h3>
        <div className="grid grid-cols-7 gap-2">
          {Object.entries(weekdayDist).map(([day, value]) => (
            <div key={day} className="text-center">
              <div className="flex flex-col items-center gap-2">
                <div className="w-full bg-slate-200 rounded h-32 relative flex flex-col-reverse">
                  <div
                    className="bg-blue-500 rounded w-full transition-all duration-300"
                    style={{
                      height: `${getPercentage(value, maxWeekday)}%`,
                    }}
                  />
                </div>
                <div className="text-sm font-medium text-slate-700">
                  {weekdayLabels[day]}
                </div>
                <div className="text-xs text-slate-600">{value}%</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 경고 알림 */}
      {analysis.alerts.length > 0 && (
        <div className="p-4 bg-warning-50 border border-warning-200 rounded-lg">
          <div className="flex items-start gap-3 mb-3">
            <AlertCircle className="w-5 h-5 text-warning-600 flex-shrink-0 mt-0.5" />
            <h4 className="font-semibold text-warning-900">근무 패턴 분석 결과</h4>
          </div>
          <ul className="space-y-2">
            {analysis.alerts.map((alert, idx) => (
              <li key={idx} className="text-sm text-warning-800">
                <span className="font-medium">{alert.type}: </span>
                {alert.message}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* 주 52시간 경고 */}
      {analysis.pattern.weekly_hours_warning && (
        <div className="p-4 bg-error-50 border border-error-200 rounded-lg flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-error-600 flex-shrink-0 mt-0.5" />
          <div>
            <h4 className="font-semibold text-error-900">주 52시간 경고</h4>
            <p className="text-sm text-error-800 mt-1">
              근로자의 주당 근무시간이 52시간을 초과하고 있습니다.
              근로기준법 준수를 위해 근무시간 조정이 필요합니다.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
