import { Metadata } from 'next';
import { AttorneyDetailClient } from './attorney-detail-client';

export const metadata: Metadata = {
  title: '노무사 상세 | 노무닥터',
};

export default function AttorneyDetailPage({
  params,
}: {
  params: { id: string };
}) {
  return <AttorneyDetailClient attorneyId={params.id} />;
}
