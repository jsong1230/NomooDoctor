/**
 * 급여명세서 목록 페이지
 */

import { Metadata } from 'next';
import { PayslipListClient } from '@/components/payslip/payslip-list-client';

export const metadata: Metadata = {
  title: '급여명세서 | 노무닥터',
  description: '급여명세서를 조회하고 관리합니다.',
};

export default function PayslipsPage() {
  return <PayslipListClient />;
}
