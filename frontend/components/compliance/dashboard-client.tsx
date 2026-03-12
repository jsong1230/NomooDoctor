'use client';

/**
 * 컴플라이언스 대시보드 클라이언트 컴포넌트
 * 리스크 스코어, 위반 항목, 이벤트 캘린더, 향후 이벤트를 통합 표시
 */

import { useState, useEffect, useCallback } from 'react';
import {
  Shield,
  AlertCircle,
  Loader2,
  Bell,
  BarChart3,
  RefreshCw,
} from 'lucide-react';
import { complianceApi } from '@/lib/api/compliance';
import { RiskScoreCard } from './risk-score-card';
import { RiskDetails } from './risk-details';
import { EventCalendar } from './event-calendar';
import type {
  RiskScoreResponse,
  ComplianceEvent,
  MonthlyRiskScore,
} from '@/types/compliance';
import { SEVERITY_CONFIG, formatDDay, RISK_LEVEL_CONFIG } from '@/types/compliance';

export function ComplianceDashboardClient() {
  const [scoreData, setScoreData] = useState<RiskScoreResponse | null>(null);
  const [upcomingEvents, setUpcomingEvents] = useState<ComplianceEvent[]>([]);
  const [scoreHistory, setScoreHistory] = useState<MonthlyRiskScore[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const [score, upcoming, history] = await Promise.all([
        complianceApi.getRiskScore(),
        complianceApi.getUpcomingEvents({ days: 30 }),
        complianceApi.getRiskScoreHistory({ months: 6 }),
      ]);

      setScoreData(score);
      setUpcomingEvents(upcoming.events);
      setScoreHistory(history.history);
    } catch (err: any) {
      const errorMessage =
        err.response?.data?.error?.message ||
        err.message ||
        '데이터를 불러오는데 실패했습니다.';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-8 h-8 text-primary-600 animate-spin mx-auto mb-3" />
          <p className="text-sm text-slate-500">컴플라이언스 데이터를 불러오는 중...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="max-w-7xl mx-auto px-4 py-8 sm:px-6 sm:py-12">
        {/* 페이지 헤더 */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 bg-primary-100 rounded-lg">
                <Shield className="w-6 h-6 text-primary-600" />
              </div>
              <h1 className="text-2xl font-bold text-slate-900">
                컴플라이언스 대시보드
              </h1>
            </div>
            <p className="text-slate-600">
              사업장의 노무 관련 법규 준수 현황을 한눈에 확인합니다.
            </p>
          </div>
          <button
            type="button"
            onClick={loadData}
            className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            새로고침
          </button>
        </div>

        {/* 에러 메시지 */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-4 mb-6 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm text-red-700">{error}</p>
              <button
                type="button"
                onClick={loadData}
                className="text-sm text-red-600 underline mt-1 hover:text-red-800"
              >
                다시 시도
              </button>
            </div>
          </div>
        )}

        {scoreData && (
          <>
            {/* 상단: 스코어 카드 + 향후 이벤트 */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
              {/* 리스크 스코어 카드 */}
              <RiskScoreCard scoreData={scoreData} />

              {/* 향후 이벤트 (D-30 알림) */}
              <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
                <div className="px-6 py-4 border-b border-slate-100">
                  <div className="flex items-center gap-2">
                    <Bell className="w-5 h-5 text-primary-600" />
                    <h2 className="text-lg font-bold text-slate-900">
                      다가오는 이벤트
                    </h2>
                    <span className="text-xs text-slate-400 ml-auto">
                      30일 이내
                    </span>
                  </div>
                </div>

                <div className="px-6 py-4">
                  {upcomingEvents.length === 0 ? (
                    <div className="text-center py-6">
                      <Bell className="w-8 h-8 text-slate-300 mx-auto mb-2" />
                      <p className="text-sm text-slate-500">
                        30일 이내 예정된 이벤트가 없습니다.
                      </p>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {upcomingEvents.slice(0, 5).map((event) => {
                        const severityConfig = SEVERITY_CONFIG[event.severity];
                        return (
                          <div
                            key={event.id}
                            className={`flex items-start gap-3 p-3 rounded-lg ${severityConfig.bgClass} border ${
                              event.severity === 'critical'
                                ? 'border-red-200'
                                : event.severity === 'warning'
                                  ? 'border-yellow-200'
                                  : 'border-blue-200'
                            }`}
                          >
                            <div
                              className={`w-2.5 h-2.5 rounded-full ${severityConfig.dotClass} mt-1.5 flex-shrink-0`}
                            />
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2">
                                <span
                                  className={`text-sm font-semibold ${severityConfig.textClass}`}
                                >
                                  {event.title}
                                </span>
                              </div>
                              <p className="text-xs text-slate-600 mt-0.5">
                                {event.description}
                              </p>
                              <div className="flex items-center gap-2 mt-1.5">
                                <span className="text-xs text-slate-400">
                                  {event.event_date}
                                </span>
                                {event.d_day !== null && (
                                  <span
                                    className={`text-xs font-bold px-1.5 py-0.5 rounded ${
                                      event.severity === 'critical'
                                        ? 'bg-red-100 text-red-700'
                                        : event.severity === 'warning'
                                          ? 'bg-yellow-100 text-yellow-700'
                                          : 'bg-blue-100 text-blue-700'
                                    }`}
                                  >
                                    {formatDDay(event.d_day)}
                                  </span>
                                )}
                              </div>
                            </div>
                          </div>
                        );
                      })}

                      {upcomingEvents.length > 5 && (
                        <p className="text-xs text-slate-400 text-center pt-1">
                          외 {upcomingEvents.length - 5}건
                        </p>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* 중단: 위반 항목 상세 + 월별 추이 */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
              {/* 위반 항목 상세 */}
              <RiskDetails
                details={scoreData.details}
                score={scoreData.score}
                level={scoreData.level}
              />

              {/* 월별 리스크 스코어 추이 (간이 차트) */}
              <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6">
                <div className="flex items-center gap-2 mb-4">
                  <BarChart3 className="w-5 h-5 text-primary-600" />
                  <h2 className="text-lg font-bold text-slate-900">
                    월별 스코어 추이
                  </h2>
                </div>

                {scoreHistory.length === 0 ? (
                  <div className="text-center py-8">
                    <BarChart3 className="w-8 h-8 text-slate-300 mx-auto mb-2" />
                    <p className="text-sm text-slate-500">데이터가 없습니다.</p>
                  </div>
                ) : (
                  <div>
                    {/* 간이 막대 차트 */}
                    <div className="flex items-end gap-2 h-40 mb-4">
                      {scoreHistory.map((item) => {
                        const heightPct = Math.max(item.score, 5);
                        const levelConfig = RISK_LEVEL_CONFIG[item.level];
                        const barBg =
                          item.level === 'green'
                            ? 'bg-green-400'
                            : item.level === 'yellow'
                              ? 'bg-yellow-400'
                              : 'bg-red-400';

                        return (
                          <div
                            key={`${item.year}-${item.month}`}
                            className="flex-1 flex flex-col items-center gap-1"
                          >
                            <span className="text-xs font-bold text-slate-700">
                              {item.score}
                            </span>
                            <div
                              className={`w-full rounded-t-md ${barBg} transition-all duration-300`}
                              style={{ height: `${heightPct}%` }}
                            />
                            <span className="text-[10px] text-slate-400">
                              {item.month}월
                            </span>
                          </div>
                        );
                      })}
                    </div>

                    {/* 범례 */}
                    <div className="flex items-center justify-center gap-4 pt-2 border-t border-slate-100">
                      <div className="flex items-center gap-1.5">
                        <div className="w-3 h-3 rounded-sm bg-green-400" />
                        <span className="text-xs text-slate-500">양호 (80~100)</span>
                      </div>
                      <div className="flex items-center gap-1.5">
                        <div className="w-3 h-3 rounded-sm bg-yellow-400" />
                        <span className="text-xs text-slate-500">주의 (60~79)</span>
                      </div>
                      <div className="flex items-center gap-1.5">
                        <div className="w-3 h-3 rounded-sm bg-red-400" />
                        <span className="text-xs text-slate-500">위험 (0~59)</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* 하단: 이벤트 캘린더 */}
            <EventCalendar />
          </>
        )}
      </div>
    </div>
  );
}
