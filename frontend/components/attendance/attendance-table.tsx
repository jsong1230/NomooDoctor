'use client';

/**
 * 근무 기록 테이블 컴포넌트
 * DataTable 기반 - 상태 배지 포함
 */

import { format } from 'date-fns';
import { formatInTimeZone } from 'date-fns-tz';
import { Badge } from '@/components/ui/badge';
import { Clock, AlertCircle, CheckCircle, LogOut } from 'lucide-react';
import type { WorkRecord } from '@/types/attendance';

interface AttendanceTableProps {
  records: WorkRecord[];
  onRowClick?: (record: WorkRecord) => void;
}

/**
 * 상태 배지를 반환하는 함수
 * 지각/조퇴/결근 판정 로직
 */
function getStatusBadge(record: WorkRecord) {
  if (!record.actual_start || !record.actual_end) {
    return (
      <Badge className="bg-red-100 text-red-800 hover:bg-red-100">
        <AlertCircle className="w-3 h-3 mr-1" />
        결근
      </Badge>
    );
  }

  const isLate = record.actual_start > record.scheduled_start;
  const isEarlyLeave = record.actual_end < record.scheduled_end;

  if (isLate && isEarlyLeave) {
    return (
      <Badge className="bg-orange-100 text-orange-800 hover:bg-orange-100">
        <AlertCircle className="w-3 h-3 mr-1" />
        지각/조퇴
      </Badge>
    );
  }

  if (isLate) {
    return (
      <Badge className="bg-yellow-100 text-yellow-800 hover:bg-yellow-100">
        <AlertCircle className="w-3 h-3 mr-1" />
        지각
      </Badge>
    );
  }

  if (isEarlyLeave) {
    return (
      <Badge className="bg-orange-100 text-orange-800 hover:bg-orange-100">
        <LogOut className="w-3 h-3 mr-1" />
        조퇴
      </Badge>
    );
  }

  return (
    <Badge className="bg-green-100 text-green-800 hover:bg-green-100">
      <CheckCircle className="w-3 h-3 mr-1" />
      정상
    </Badge>
  );
}

/**
 * 시간을 분 단위로 변환
 */
function minutesToHours(minutes: number): string {
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  if (mins === 0) {
    return `${hours}시간`;
  }
  return `${hours}시간 ${mins}분`;
}

export function AttendanceTable({ records, onRowClick }: AttendanceTableProps) {
  return (
    <div className="w-full overflow-x-auto border rounded-lg">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b bg-slate-50">
            <th className="px-4 py-3 text-left font-medium text-slate-700">날짜</th>
            <th className="px-4 py-3 text-left font-medium text-slate-700">직원명</th>
            <th className="px-4 py-3 text-center font-medium text-slate-700">출근</th>
            <th className="px-4 py-3 text-center font-medium text-slate-700">퇴근</th>
            <th className="px-4 py-3 text-center font-medium text-slate-700">근무시간</th>
            <th className="px-4 py-3 text-center font-medium text-slate-700">연장</th>
            <th className="px-4 py-3 text-center font-medium text-slate-700">야간</th>
            <th className="px-4 py-3 text-center font-medium text-slate-700">휴일</th>
            <th className="px-4 py-3 text-center font-medium text-slate-700">상태</th>
          </tr>
        </thead>
        <tbody>
          {records.length === 0 ? (
            <tr>
              <td colSpan={9} className="px-4 py-8 text-center text-slate-500">
                근무 기록이 없습니다
              </td>
            </tr>
          ) : (
            records.map((record) => (
              <tr
                key={record.id}
                onClick={() => onRowClick?.(record)}
                className="border-b hover:bg-slate-50 cursor-pointer transition-colors"
              >
                <td className="px-4 py-3">
                  <span className="font-medium text-slate-900">
                    {format(new Date(record.work_date), 'yyyy-MM-dd')}
                  </span>
                </td>
                <td className="px-4 py-3 text-slate-700">{record.employee_name}</td>
                <td className="px-4 py-3 text-center text-slate-700">
                  {record.actual_start ? (
                    <span>{record.actual_start}</span>
                  ) : (
                    <span className="text-slate-400">-</span>
                  )}
                </td>
                <td className="px-4 py-3 text-center text-slate-700">
                  {record.actual_end ? (
                    <span>{record.actual_end}</span>
                  ) : (
                    <span className="text-slate-400">-</span>
                  )}
                </td>
                <td className="px-4 py-3 text-center text-slate-700">
                  <div className="flex items-center justify-center gap-1">
                    <Clock className="w-4 h-4" />
                    {minutesToHours(record.total_work_minutes)}
                  </div>
                </td>
                <td className="px-4 py-3 text-center text-slate-700">
                  {record.overtime_minutes > 0 ? (
                    <span className="font-semibold text-warning-600">
                      {minutesToHours(record.overtime_minutes)}
                    </span>
                  ) : (
                    <span className="text-slate-400">-</span>
                  )}
                </td>
                <td className="px-4 py-3 text-center text-slate-700">
                  {record.night_minutes > 0 ? (
                    <span className="font-semibold text-indigo-600">
                      {minutesToHours(record.night_minutes)}
                    </span>
                  ) : (
                    <span className="text-slate-400">-</span>
                  )}
                </td>
                <td className="px-4 py-3 text-center text-slate-700">
                  {record.holiday_minutes > 0 ? (
                    <span className="font-semibold text-error-600">
                      {minutesToHours(record.holiday_minutes)}
                    </span>
                  ) : (
                    <span className="text-slate-400">-</span>
                  )}
                </td>
                <td className="px-4 py-3 text-center">
                  {getStatusBadge(record)}
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
