'use client';

/**
 * 사업장 선택 드롭다운 컴포넌트
 * 현재 선택된 사업장 컨텍스트 변경
 */

import { useState, useEffect } from 'react';
import { Building2, ChevronDown, Check, Loader2 } from 'lucide-react';
import { companyApi } from '@/lib/api/company';
import type { Company } from '@/types/company';
import { companyStore } from '@/lib/stores/company-store';
import { authStore } from '@/lib/stores/auth-store';

interface CompanySelectorProps {
  className?: string;
}

export function CompanySelector({ className = '' }: CompanySelectorProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [companies, setCompanies] = useState<Company[]>([]);
  const [error, setError] = useState<string | null>(null);

  const currentCompany = companyStore((state) => state.currentCompany);
  const setCurrentCompany = companyStore((state) => state.setCurrentCompany);
  const updateUser = authStore((state) => state.updateUser);

  // 사업장 목록 로드
  useEffect(() => {
    const loadCompanies = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const response = await companyApi.getCompanies();
        setCompanies(response.companies);

        // 스토어에 저장
        companyStore.getState().setCompanies(response.companies);

        // 현재 선택된 사업장이 없고 목록에 사업장이 있는 경우 첫 번째 선택
        if (!currentCompany && response.companies.length > 0) {
          setCurrentCompany(response.companies[0]);
        }
      } catch (err: any) {
        const errorMessage = err.response?.data?.detail || err.message || '사업장 목록을 불러오는데 실패했습니다';
        setError(errorMessage);
      } finally {
        setIsLoading(false);
      }
    };

    loadCompanies();
  }, []);

  // 사업장 선택 핸들러
  const handleSelectCompany = async (company: Company) => {
    if (company.id === currentCompany?.id) {
      setIsOpen(false);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      // 사업장 선택 API 호출 (토큰 재발급)
      const response = await companyApi.selectCompany(company.id);

      // 새 토큰 저장
      authStore.getState().setTokens(response.access_token, response.refresh_token);

      // 스토어 업데이트
      setCurrentCompany(company);
      updateUser({ company_id: company.id });

      setIsOpen(false);
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || '사업장 변경에 실패했습니다';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  // 드롭다운 외부 클릭 처리
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      if (!target.closest('.company-selector')) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [isOpen]);

  return (
    <div className={`company-selector relative ${className}`}>
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        disabled={isLoading}
        className="
          flex items-center justify-between gap-3
          w-full px-4 py-2.5
          bg-white border border-slate-200 rounded-lg
          hover:border-primary-300
          transition-all duration-200
          disabled:opacity-50 disabled:cursor-not-allowed
        "
      >
        <div className="flex items-center gap-3 min-w-0">
          <Building2 className="w-5 h-5 text-slate-500 flex-shrink-0" />
          {isLoading ? (
            <Loader2 className="w-5 h-5 text-slate-400 animate-spin" />
          ) : currentCompany ? (
            <span className="text-sm font-medium text-slate-900 truncate">
              {currentCompany.business_name}
            </span>
          ) : (
            <span className="text-sm text-slate-500">사업장을 선택해주세요</span>
          )}
        </div>
        <ChevronDown className={`w-4 h-4 text-slate-400 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {/* 드롭다운 메뉴 */}
      {isOpen && companies.length > 0 && (
        <div className="
          absolute top-full left-0 right-0 z-50
          mt-1
          bg-white border border-slate-200 rounded-lg
          shadow-lg
          max-h-64 overflow-y-auto
          animate-in fade-in slide-in-from-top-2
        ">
          {companies.map((company) => (
            <button
              key={company.id}
              type="button"
              onClick={() => handleSelectCompany(company)}
              disabled={isLoading}
              className="
                w-full px-4 py-3
                flex items-center gap-3
                hover:bg-slate-50
                transition-colors duration-150
                disabled:opacity-50 disabled:cursor-not-allowed
                border-b border-slate-100 last:border-b-0
              "
            >
              <Building2 className="w-5 h-5 text-slate-500 flex-shrink-0" />
              <span className="text-sm text-slate-900 truncate flex-1 text-left">
                {company.business_name}
              </span>
              {company.id === currentCompany?.id && (
                <Check className="w-5 h-5 text-primary-600 flex-shrink-0" />
              )}
            </button>
          ))}
        </div>
      )}

      {/* 에러 메시지 */}
      {error && (
        <div className="mt-2 p-2 bg-error-50 border border-error-200 rounded-lg">
          <p className="text-xs text-error-700">{error}</p>
        </div>
      )}

      {/* 사업장이 없는 경우 */}
      {!isLoading && companies.length === 0 && (
        <div className="absolute top-full left-0 right-0 z-50 mt-1 bg-white border border-slate-200 rounded-lg shadow-lg p-4">
          <p className="text-sm text-slate-600 mb-3">등록된 사업장이 없습니다.</p>
          <a
            href="/company/new"
            className="block w-full px-4 py-2 text-center bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors duration-200 text-sm font-medium"
          >
            사업장 등록하기
          </a>
        </div>
      )}
    </div>
  );
}
