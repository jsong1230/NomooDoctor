/**
 * 취업규칙 상세/편집 페이지
 * Server Component 래퍼
 */

import { Metadata } from 'next';
import { WorkRuleDetailClient } from './work-rule-detail-client';

interface WorkRuleDetailPageProps {
  params: Promise<{ id: string }>;
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
}

export async function generateMetadata({ params }: WorkRuleDetailPageProps): Promise<Metadata> {
  const { id } = await params;
  return {
    title: '취업규칙 상세 | 노무닥터',
    description: '취업규칙을 조회하고 편집합니다.',
  };
}

export default async function WorkRuleDetailPage({ params }: WorkRuleDetailPageProps) {
  const { id } = await params;

  return <WorkRuleDetailClient workRuleId={id} />;
}
