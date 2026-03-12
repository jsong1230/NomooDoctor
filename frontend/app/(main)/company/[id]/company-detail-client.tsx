'use client';

/**
 * 사업장 상세 페이지 클라이언트 컴포넌트
 */

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { WorkRuleNotice } from '@/components/company/work-rule-notice';
import { companyApi } from '@/lib/api/company';
import type { Company } from '@/types/company';
import { getIndustryLabel } from '@/types/company';
import {
  Building2,
  User,
  Briefcase,
  Users,
  MapPin,
  Phone,
  Calendar,
  Pencil,
  FileText,
  DollarSign,
  Loader2,
  AlertCircle,
  X,
} from 'lucide-react';

interface CompanyDetailClientProps {
  companyId: string;
}

export function CompanyDetailClient({ companyId }: CompanyDetailClientProps) {
  const router = useRouter();
  const [company, setCompany] = useState<Company | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deleteConfirmation, setDeleteConfirmation] = useState('');
  const [isDeleting, setIsDeleting] = useState(false);

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

  const handleDelete = async () => {
    if (!company || deleteConfirmation !== company.business_name) {
      return;
    }

    setIsDeleting(true);
    setError(null);

    try {
      await companyApi.deleteCompany(companyId, { confirmation: deleteConfirmation });
      // 스토어에서 제거
      const { companyStore: store } = await import('@/lib/stores/company-store');
      store.getState().removeCompany(companyId);
      router.push('/company/new');
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || '삭제에 실패했습니다';
      setError(errorMessage);
    } finally {
      setIsDeleting(false);
    }
  };

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
          <button
            onClick={() => router.back()}
            className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors duration-200"
          >
            이전으로
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* 삭제 확인 모달 */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" />
          <div className="relative bg-white rounded-2xl shadow-xl max-w-md w-full mx-4 p-6 animate-in fade-in slide-in-from-bottom-4">
            <button
              type="button"
              onClick={() => {
                setShowDeleteConfirm(false);
                setDeleteConfirmation('');
              }}
              className="absolute top-4 right-4 text-slate-400 hover:text-slate-600"
              aria-label="닫기"
            >
              <X className="w-5 h-5" />
            </button>
            <div className="flex items-start gap-3 mb-4">
              <div className="p-2 bg-error-100 rounded-lg">
                <AlertCircle className="w-6 h-6 text-error-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-slate-900">
                  사업장 삭제
                </h3>
                <p className="text-sm text-slate-600 mt-2">
                  사업장을 삭제하면 관련된 모든 데이터도 함께 삭제됩니다.
                  이 작업은 되돌릴 수 없습니다.
                </p>
              </div>
            </div>
            <div className="mb-4">
              <label htmlFor="confirmation" className="text-sm font-medium text-slate-700 mb-2 block">
                삭제하려면 "{company.business_name}"을 입력해주세요
              </label>
              <input
                id="confirmation"
                type="text"
                value={deleteConfirmation}
                onChange={(e) => setDeleteConfirmation(e.target.value)}
                placeholder={company.business_name}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-error-500"
              />
            </div>
            <div className="flex gap-3">
              <button
                type="button"
                onClick={() => {
                  setShowDeleteConfirm(false);
                  setDeleteConfirmation('');
                }}
                disabled={isDeleting}
                className="flex-1 px-4 py-2 text-slate-700 hover:bg-slate-100 rounded-lg font-medium transition-colors duration-200 disabled:opacity-50"
              >
                취소
              </button>
              <button
                type="button"
                onClick={handleDelete}
                disabled={deleteConfirmation !== company.business_name || isDeleting}
                className="flex-1 px-4 py-2 bg-error-600 text-white rounded-lg font-medium hover:bg-error-700 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {isDeleting ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    삭제 중...
                  </>
                ) : (
                  '삭제'
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="max-w-4xl mx-auto px-4 py-8 sm:px-6 sm:py-12">
        {/* 페이지 헤더 */}
        <div className="mb-8">
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-3xl font-bold text-slate-900 mb-2">
                {company.business_name}
              </h1>
              <p className="text-slate-600">
                사업장 상세 정보 및 관리
              </p>
            </div>
            <div className="flex items-center gap-2">
              <a
                href={`/company/${companyId}/edit`}
                className="
                  flex items-center gap-2 px-4 py-2
                  bg-white border border-slate-200 text-slate-700
                  rounded-lg hover:border-primary-300 hover:text-primary-700
                  transition-colors duration-200
                "
              >
                <Pencil className="w-4 h-4" />
                <span className="hidden sm:inline">수정</span>
              </a>
              <button
                type="button"
                onClick={() => setShowDeleteConfirm(true)}
                className="
                  flex items-center gap-2 px-4 py-2
                  bg-white border border-error-200 text-error-600
                  rounded-lg hover:border-error-300 hover:bg-error-50
                  transition-colors duration-200
                "
              >
                <AlertCircle className="w-4 h-4" />
                <span className="hidden sm:inline">삭제</span>
              </button>
            </div>
          </div>
        </div>

        {/* 취업규칙 의무 안내 */}
        {company.work_rule_required && (
          <div className="mb-6">
            <WorkRuleNotice employeeCount={company.employee_count} />
          </div>
        )}

        {/* 사업장 정보 카드 */}
        <div className="bg-white border border-slate-200 rounded-xl p-6 sm:p-8 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900 mb-6">
            사업장 정보
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* 사업자등록번호 */}
            <div className="flex items-start gap-3">
              <Building2 className="w-5 h-5 text-slate-500 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-xs text-slate-500 mb-1">사업자등록번호</p>
                <p className="text-sm font-medium text-slate-900 font-mono">
                  {company.business_number}
                </p>
              </div>
            </div>

            {/* 대표자명 */}
            <div className="flex items-start gap-3">
              <User className="w-5 h-5 text-slate-500 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-xs text-slate-500 mb-1">대표자명</p>
                <p className="text-sm font-medium text-slate-900">
                  {company.representative_name}
                </p>
              </div>
            </div>

            {/* 업종 */}
            <div className="flex items-start gap-3">
              <Briefcase className="w-5 h-5 text-slate-500 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-xs text-slate-500 mb-1">업종</p>
                <p className="text-sm font-medium text-slate-900">
                  {getIndustryLabel(company.industry_type)}
                </p>
              </div>
            </div>

            {/* 직원 수 */}
            <div className="flex items-start gap-3">
              <Users className="w-5 h-5 text-slate-500 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-xs text-slate-500 mb-1">직원 수</p>
                <p className="text-sm font-medium text-slate-900">
                  {company.employee_count}명
                </p>
              </div>
            </div>

            {/* 주소 */}
            {company.address && (
              <div className="flex items-start gap-3 md:col-span-2">
                <MapPin className="w-5 h-5 text-slate-500 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-xs text-slate-500 mb-1">주소</p>
                  <p className="text-sm font-medium text-slate-900">
                    {company.address}
                    {company.postal_code && ` (${company.postal_code})`}
                  </p>
                </div>
              </div>
            )}

            {/* 전화번호 */}
            {company.phone && (
              <div className="flex items-start gap-3">
                <Phone className="w-5 h-5 text-slate-500 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-xs text-slate-500 mb-1">대표 전화번호</p>
                  <p className="text-sm font-medium text-slate-900">
                    {company.phone}
                  </p>
                </div>
              </div>
            )}

            {/* 등록일 */}
            <div className="flex items-start gap-3">
              <Calendar className="w-5 h-5 text-slate-500 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-xs text-slate-500 mb-1">등록일</p>
                <p className="text-sm font-medium text-slate-900">
                  {new Date(company.created_at).toLocaleDateString('ko-KR', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                  })}
                </p>
              </div>
            </div>
          </div>

          {/* 취업규칙 의무 상태 */}
          <div className="mt-6 pt-6 border-t border-slate-200">
            <div className="flex items-center gap-3">
              <div className={`p-2 rounded-lg ${company.work_rule_required ? 'bg-warning-100' : 'bg-success-100'}`}>
                <Users className={`w-5 h-5 ${company.work_rule_required ? 'text-warning-600' : 'text-success-600'}`} />
              </div>
              <div>
                <p className="text-sm font-medium text-slate-900">
                  취업규칙 작성 {company.work_rule_required ? '필수' : '선택'}
                </p>
                <p className="text-xs text-slate-600">
                  {company.work_rule_required
                    ? '10인 이상 사업장은 근로기준법에 따라 취업규칙 작성이 의무입니다.'
                    : '10인 미만 사업장은 취업규칙 작성이 선택사항입니다.'}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* 관리 메뉴 */}
        <div className="mt-6 bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">
            사업장 관리
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <a
              href={`/work-rules?company_id=${companyId}`}
              className="
                flex items-center gap-3 p-4
                border border-slate-200 rounded-lg
                hover:border-primary-300 hover:bg-primary-50
                transition-all duration-200
              "
            >
              <FileText className="w-5 h-5 text-slate-600" />
              <div>
                <p className="text-sm font-medium text-slate-900">취업규칙 관리</p>
                <p className="text-xs text-slate-600">취업규칙을 작성하고 관리합니다</p>
              </div>
            </a>
            <a
              href={`/employees?company_id=${companyId}`}
              className="
                flex items-center gap-3 p-4
                border border-slate-200 rounded-lg
                hover:border-primary-300 hover:bg-primary-50
                transition-all duration-200
              "
            >
              <Users className="w-5 h-5 text-slate-600" />
              <div>
                <p className="text-sm font-medium text-slate-900">직원 관리</p>
                <p className="text-xs text-slate-600">직원 정보를 등록하고 관리합니다</p>
              </div>
            </a>
            <a
              href={`/contracts?company_id=${companyId}`}
              className="
                flex items-center gap-3 p-4
                border border-slate-200 rounded-lg
                hover:border-primary-300 hover:bg-primary-50
                transition-all duration-200
              "
            >
              <FileText className="w-5 h-5 text-slate-600" />
              <div>
                <p className="text-sm font-medium text-slate-900">계약서 관리</p>
                <p className="text-xs text-slate-600">근로계약서를 작성하고 관리합니다</p>
              </div>
            </a>
            <a
              href={`/payroll?company_id=${companyId}`}
              className="
                flex items-center gap-3 p-4
                border border-slate-200 rounded-lg
                hover:border-primary-300 hover:bg-primary-50
                transition-all duration-200
              "
            >
              <DollarSign className="w-5 h-5 text-slate-600" />
              <div>
                <p className="text-sm font-medium text-slate-900">급여 관리</p>
                <p className="text-xs text-slate-600">급여를 계산하고 지급합니다</p>
              </div>
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
