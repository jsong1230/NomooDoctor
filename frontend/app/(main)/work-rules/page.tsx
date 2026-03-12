/**
 * 취업규칙 관리 페이지
 * Server Component 래퍼
 */

import { Metadata } from 'next';
import { WorkRuleListClient } from './work-rules-client';

export const metadata: Metadata = {
  title: '취업규칙 관리 | 노무닥터',
  description: '사업장의 취업규칙을 작성하고 관리합니다.',
};

interface WorkRulesPageProps {
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
}

export default async function WorkRulesPage({ searchParams }: WorkRulesPageProps) {
  const params = await searchParams;

  return <WorkRuleListClient />;
}
