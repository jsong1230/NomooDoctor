import { Metadata } from 'next';
import { AttorneysClient } from './attorneys-client';

export const metadata: Metadata = {
  title: '노무사 마켓플레이스 | 노무닥터',
  description: '전문 노무사를 찾고 상담을 신청하세요.',
};

export default function AttorneysPage() {
  return <AttorneysClient />;
}
