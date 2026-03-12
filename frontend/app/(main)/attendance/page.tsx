/**
 * 근태 관리 메인 페이지
 * 근무 기록, 월별 요약, 패턴 분석 탭
 */

import { Metadata } from 'next';
import { AttendanceClient } from '@/components/attendance/attendance-client';

export const metadata: Metadata = {
  title: '근태 관리 | 노무닥터',
  description: '직원의 근무 기록, 월별 근태 요약, 근무 패턴을 분석합니다.',
};

export default function AttendancePage() {
  return <AttendanceClient />;
}
