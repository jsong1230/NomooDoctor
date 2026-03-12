/**
 * 사업장 상태 관리 스토어 (Zustand)
 * 현재 선택된 사업장 컨텍스트 관리
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { Company } from '@/types/company';

interface CompanyState {
  currentCompany: Company | null;
  companies: Company[];

  // Actions
  setCurrentCompany: (company: Company) => void;
  setCompanies: (companies: Company[]) => void;
  addCompany: (company: Company) => void;
  updateCompany: (id: string, updates: Partial<Company>) => void;
  removeCompany: (id: string) => void;
  clearCompany: () => void;
}

export const companyStore = create<CompanyState>()(
  persist(
    (set, get) => ({
      currentCompany: null,
      companies: [],

      setCurrentCompany: (company) => set({ currentCompany: company }),

      setCompanies: (companies) => set({ companies }),

      addCompany: (company) =>
        set((state) => ({
          companies: [...state.companies, company],
        })),

      updateCompany: (id, updates) =>
        set((state) => ({
          companies: state.companies.map((c) =>
            c.id === id ? { ...c, ...updates } : c
          ),
          currentCompany:
            state.currentCompany?.id === id
              ? { ...state.currentCompany, ...updates }
              : state.currentCompany,
        })),

      removeCompany: (id) =>
        set((state) => ({
          companies: state.companies.filter((c) => c.id !== id),
          currentCompany:
            state.currentCompany?.id === id ? null : state.currentCompany,
        })),

      clearCompany: () => set({ currentCompany: null, companies: [] }),
    }),
    {
      name: 'company-storage',
      partialize: (state) => ({
        currentCompany: state.currentCompany,
        companies: state.companies,
      }),
    }
  )
);
