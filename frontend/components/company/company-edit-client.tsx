'use client';

/**
 * 사업장 수정 페이지 클라이언트 컴포넌트
 */

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { CompanyForm } from '@/components/company/company-form';
import { companyApi } from '@/lib/api/company';
import type { Company } from '@/types/company';
import { Loader2, AlertCircle, ArrowLeft } from 'lucide-react';
import Link from 'next/link';

interface CompanyEditClientProps {
  companyId: string;
}

export function CompanyEditClient({ companyId }: CompanyEditClientProps) {
  const router = useRouter();
  const [company, setCompany] = useState<Company | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadCompany = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const data = await companyApi.getCompany(companyId);
        setCompany(data);
      } catch (err: any) {
        const errorMessage = err.response?.data?.detail || err.message || '사업장 정보를 불러오는데 실패했습니다';
        setError(errorMessage);
      } finally {
        setIsLoading(false);
      }
    };

    loadCompany();
  }, [companyId]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-primary-600 animate-spin" />
      </div>
    );
  }

  if (error || !company) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center px-4">
        <div className="bg-white border border-slate-200 rounded-xl p-6 max-w-md text-center">
          <AlertCircle className="w-12 h-12 text-error-600 mx-auto mb-4" />
          <h2 className="text-lg font-semibold text-slate-900 mb-2">오류 발생</h2>
          <p className="text-slate-600 mb-4">{error || '사업장을 찾을 수 없습니다.'}</p>
          <Link
            href={`/company/${companyId}`}
            className="inline-flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors duration-200"
          >
            <ArrowLeft className="w-4 h-4" />
            사업장 정보로
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="max-w-2xl mx-auto px-4 py-8 sm:px-6 sm:py-12">
        {/* 페이지 헤더 */}
        <div className="mb-8">
          <div className="flex items-center gap-4 mb-2">
            <Link
              href={`/company/${companyId}`}
              className="p-2 hover:bg-slate-200 rounded-lg transition-colors duration-200"
              aria-label="뒤로가기"
            >
              <ArrowLeft className="w-5 h-5 text-slate-600" />
            </Link>
            <h1 className="text-3xl font-bold text-slate-900">
              사업장 정보 수정
            </h1>
          </div>
          <p className="text-slate-600 ml-14">
            {company.business_name}의 정보를 수정하세요.
          </p>
        </div>

        {/* 사업장 수정 폼 */}
        <div className="bg-white border border-slate-200 rounded-xl p-6 sm:p-8 shadow-sm">
          <CompanyForm company={company} mode="edit" />
        </div>
      </div>
    </div>
  );
}
