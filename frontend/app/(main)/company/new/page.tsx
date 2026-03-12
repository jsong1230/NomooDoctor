/**
 * 사업장 등록 페이지
 */

import { CompanyForm } from '@/components/company/company-form';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: '사업장 등록 | 노무닥터',
  description: '새로운 사업장을 등록하세요.',
};

export default function NewCompanyPage() {
  return (
    <div className="min-h-screen bg-slate-50">
      <div className="max-w-2xl mx-auto px-4 py-8 sm:px-6 sm:py-12">
        {/* 페이지 헤더 */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900 mb-2">
            사업장 등록
          </h1>
          <p className="text-slate-600">
            사업장 정보를 입력하여 등록하세요.
          </p>
        </div>

        {/* 사업장 등록 폼 */}
        <div className="bg-white border border-slate-200 rounded-xl p-6 sm:p-8 shadow-sm">
          <CompanyForm mode="create" />
        </div>
      </div>
    </div>
  );
}
