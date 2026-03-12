/**
 * 구독 관리 페이지 (Server Component 래퍼)
 */

import { Metadata } from 'next';
import { SubscriptionClient } from './subscription-client';

export const metadata: Metadata = {
  title: '구독 관리 | 노무닥터',
  description: '플랜을 선택하고 구독을 관리하세요.',
};

export default function SubscriptionPage() {
  return <SubscriptionClient />;
}
