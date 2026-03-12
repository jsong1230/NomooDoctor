/**
 * 사업장 수정 페이지
 */

import { Metadata } from 'next';
import { notFound } from 'next/navigation';
import { CompanyEditClient } from '@/components/company/company-edit-client';

interface CompanyEditPageProps {
  params: Promise<{ id: string }>;
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
}

export async function generateMetadata({ params }: CompanyEditPageProps): Promise<Metadata> {
  return {
    title: '사업장 정보 수정 | 노무닥터',
    description: '사업장 정보를 수정하세요.',
  };
}

export default async function CompanyEditPage({ params }: CompanyEditPageProps) {
  const { id } = await params;

  return <CompanyEditClient companyId={id} />;
}
