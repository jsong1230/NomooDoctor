/**
 * 퇴직금 계산기 페이지 (Server Component 래퍼)
 */

import { Metadata } from 'next';
import { RetirementClient } from './retirement-client';

export const metadata: Metadata = {
  title: '퇴직금 계산기 | 노무닥터',
  description: '직원의 퇴직금을 정확하게 계산하세요.',
};

export default function RetirementPage() {
  return <RetirementClient />;
}
