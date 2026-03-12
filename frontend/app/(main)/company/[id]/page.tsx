/**
 * 사업장 상세 페이지
 */

import { Metadata } from 'next';
import { notFound } from 'next/navigation';
import { CompanyDetailClient } from './company-detail-client';

interface CompanyPageProps {
  params: Promise<{ id: string }>;
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
}

export async function generateMetadata({ params }: CompanyPageProps): Promise<Metadata> {
  const { id } = await params;
  return {
    title: '사업장 정보 | 노무닥터',
    description: '사업장 정보입니다.',
  };
}

export default async function CompanyPage({ params }: CompanyPageProps) {
  const { id } = await params;

  return <CompanyDetailClient companyId={id} />;
}
