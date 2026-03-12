/**
 * 해고 절차 가이드 페이지 (Server Component 래퍼)
 */

import { Metadata } from 'next';
import { TerminationClient } from './termination-client';

export const metadata: Metadata = {
  title: '해고 절차 가이드 | 노무닥터',
  description: '안전하고 법적으로 적절한 해고 절차를 안내합니다.',
};

export default function TerminationPage() {
  return <TerminationClient />;
}
