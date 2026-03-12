/**
 * 컴플라이언스 대시보드 페이지
 */

import { Metadata } from 'next';
import { ComplianceDashboardClient } from '@/components/compliance/dashboard-client';

export const metadata: Metadata = {
  title: '컴플라이언스 대시보드 | 노무닥터',
  description: '사업장의 노무 관련 법규 준수 현황을 확인합니다.',
};

export default function DashboardPage() {
  return <ComplianceDashboardClient />;
}
