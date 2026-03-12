'use client';

/**
 * 노무 이벤트 캘린더 컴포넌트
 * 간단한 월간 뷰로 이벤트를 표시
 */

import { useState, useCallback, useEffect } from 'react';
import {
  Calendar,
  ChevronLeft,
  ChevronRight,
  Clock,
  FileText,
  Wallet,
  AlertCircle,
  Loader2,
} from 'lucide-react';
import { complianceApi } from '@/lib/api/compliance';
import type { ComplianceEvent, ComplianceEventType } from '@/types/compliance';
import {
  EVENT_TYPE_LABELS,
  SEVERITY_CONFIG,
  formatDDay,
} from '@/types/compliance';

function getEventIcon(eventType: ComplianceEventType) {
  switch (eventType) {
    case 'contract_expiry':
      return <FileText className="w-3.5 h-3.5" />;
    case 'payroll_date':
      return <Wallet className="w-3.5 h-3.5" />;
    default:
      return <Clock className="w-3.5 h-3.5" />;
  }
}

interface EventCalendarProps {
  initialYear?: number;
  initialMonth?: number;
}

export function EventCalendar({ initialYear, initialMonth }: EventCalendarProps) {
  const now = new Date();
  const [year, setYear] = useState(initialYear ?? now.getFullYear());
  const [month, setMonth] = useState(initialMonth ?? now.getMonth() + 1);
  const [events, setEvents] = useState<ComplianceEvent[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadEvents = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const data = await complianceApi.getComplianceEvents({ year, month });
      setEvents(data.events);
    } catch (err: any) {
      const errorMessage =
        err.response?.data?.error?.message ||
        err.message ||
        '이벤트를 불러오는데 실패했습니다.';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, [year, month]);

  useEffect(() => {
    loadEvents();
  }, [loadEvents]);

  const goToPrevMonth = () => {
    if (month === 1) {
      setMonth(12);
      setYear(year - 1);
    } else {
      setMonth(month - 1);
    }
  };

  const goToNextMonth = () => {
    if (month === 12) {
      setMonth(1);
      setYear(year + 1);
    } else {
      setMonth(month + 1);
    }
  };

  const goToToday = () => {
    setYear(now.getFullYear());
    setMonth(now.getMonth() + 1);
  };

  // 월의 날짜 정보 계산
  const daysInMonth = new Date(year, month, 0).getDate();
  const firstDayOfWeek = new Date(year, month - 1, 1).getDay(); // 0=일, 1=월, ...
  const dayNames = ['일', '월', '화', '수', '목', '금', '토'];

  // 이벤트를 날짜별로 그룹핑
  const eventsByDate: Record<number, ComplianceEvent[]> = {};
  events.forEach((event) => {
    const eventDate = new Date(event.event_date);
    if (eventDate.getFullYear() === year && eventDate.getMonth() + 1 === month) {
      const day = eventDate.getDate();
      if (!eventsByDate[day]) {
        eventsByDate[day] = [];
      }
      eventsByDate[day].push(event);
    }
  });

  const today = new Date();
  const isCurrentMonth =
    today.getFullYear() === year && today.getMonth() + 1 === month;

  return (
    <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
      {/* 캘린더 헤더 */}
      <div className="px-6 py-4 border-b border-slate-100">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Calendar className="w-5 h-5 text-primary-600" />
            <h2 className="text-lg font-bold text-slate-900">노무 이벤트 캘린더</h2>
          </div>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={goToPrevMonth}
              className="p-1.5 rounded-lg hover:bg-slate-100 text-slate-400 hover:text-slate-600 transition-colors"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button
              type="button"
              onClick={goToToday}
              className="px-3 py-1 text-sm font-medium text-slate-700 hover:bg-slate-100 rounded-lg transition-colors"
            >
              {year}년 {month}월
            </button>
            <button
              type="button"
              onClick={goToNextMonth}
              className="p-1.5 rounded-lg hover:bg-slate-100 text-slate-400 hover:text-slate-600 transition-colors"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* 로딩 */}
      {isLoading && (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-6 h-6 text-primary-600 animate-spin" />
        </div>
      )}

      {/* 에러 */}
      {error && !isLoading && (
        <div className="px-6 py-4">
          <div className="bg-red-50 border border-red-200 rounded-lg p-3 flex items-start gap-2">
            <AlertCircle className="w-4 h-4 text-red-600 mt-0.5 flex-shrink-0" />
            <p className="text-sm text-red-700">{error}</p>
          </div>
        </div>
      )}

      {/* 캘린더 그리드 */}
      {!isLoading && !error && (
        <div className="px-4 py-3">
          {/* 요일 헤더 */}
          <div className="grid grid-cols-7 mb-1">
            {dayNames.map((name, idx) => (
              <div
                key={name}
                className={`text-center text-xs font-medium py-2 ${
                  idx === 0 ? 'text-red-400' : idx === 6 ? 'text-blue-400' : 'text-slate-400'
                }`}
              >
                {name}
              </div>
            ))}
          </div>

          {/* 날짜 그리드 */}
          <div className="grid grid-cols-7 gap-px">
            {/* 빈 칸 (월 시작일 이전) */}
            {Array.from({ length: firstDayOfWeek }).map((_, idx) => (
              <div key={`empty-${idx}`} className="min-h-[72px] p-1" />
            ))}

            {/* 날짜 셀 */}
            {Array.from({ length: daysInMonth }).map((_, idx) => {
              const day = idx + 1;
              const dayEvents = eventsByDate[day] || [];
              const isToday = isCurrentMonth && today.getDate() === day;
              const dayOfWeek = (firstDayOfWeek + idx) % 7;
              const isSunday = dayOfWeek === 0;
              const isSaturday = dayOfWeek === 6;

              return (
                <div
                  key={day}
                  className={`min-h-[72px] p-1 rounded-lg ${
                    isToday ? 'bg-primary-50 ring-1 ring-primary-200' : 'hover:bg-slate-50'
                  } transition-colors`}
                >
                  <div
                    className={`text-xs font-medium mb-0.5 ${
                      isToday
                        ? 'text-primary-700'
                        : isSunday
                          ? 'text-red-400'
                          : isSaturday
                            ? 'text-blue-400'
                            : 'text-slate-600'
                    }`}
                  >
                    {day}
                  </div>
                  {dayEvents.slice(0, 2).map((event) => {
                    const severityConfig = SEVERITY_CONFIG[event.severity];
                    return (
                      <div
                        key={event.id}
                        className={`flex items-center gap-1 px-1 py-0.5 rounded text-[10px] leading-tight mb-0.5 ${severityConfig.bgClass} ${severityConfig.textClass}`}
                        title={`${event.title}\n${event.description}`}
                      >
                        {getEventIcon(event.event_type)}
                        <span className="truncate">{EVENT_TYPE_LABELS[event.event_type]}</span>
                      </div>
                    );
                  })}
                  {dayEvents.length > 2 && (
                    <div className="text-[10px] text-slate-400 px-1">
                      +{dayEvents.length - 2}건
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* 이벤트 목록 (캘린더 아래) */}
      {!isLoading && !error && events.length > 0 && (
        <div className="px-6 py-4 border-t border-slate-100">
          <h3 className="text-sm font-semibold text-slate-700 mb-3">
            {month}월 예정 이벤트 ({events.length}건)
          </h3>
          <div className="space-y-2">
            {events.map((event) => {
              const severityConfig = SEVERITY_CONFIG[event.severity];
              return (
                <div
                  key={event.id}
                  className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-slate-50 transition-colors"
                >
                  <div className={`w-2 h-2 rounded-full ${severityConfig.dotClass} flex-shrink-0`} />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium text-slate-900 truncate">
                        {event.title}
                      </span>
                      {event.d_day !== null && (
                        <span
                          className={`text-xs font-medium px-1.5 py-0.5 rounded ${severityConfig.bgClass} ${severityConfig.textClass} flex-shrink-0`}
                        >
                          {formatDDay(event.d_day)}
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-slate-500 truncate mt-0.5">
                      {event.event_date} {event.description && `- ${event.description}`}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {!isLoading && !error && events.length === 0 && (
        <div className="px-6 py-8 text-center border-t border-slate-100">
          <Calendar className="w-8 h-8 text-slate-300 mx-auto mb-2" />
          <p className="text-sm text-slate-500">
            {month}월에 예정된 이벤트가 없습니다.
          </p>
        </div>
      )}
    </div>
  );
}
