/**
 * 퇴직금/해고 계산기 상태 관리 스토어 (Zustand)
 * 계산 결과 및 해고 절차 가이드 관리
 */

import { create } from 'zustand';
import type {
  SeveranceResult,
  SeveranceRecord,
  SeveranceSummary,
  TerminationGuide,
} from '@/types/retirement';

interface RetirementState {
  // 퇴직금 계산
  calculationResult: SeveranceResult | null;
  savedRecord: SeveranceRecord | null;
  isCalculating: boolean;
  calculateError: string | null;

  // 해고 절차 가이드
  terminationGuide: TerminationGuide | null;
  isGeneratingGuide: boolean;
  guideError: string | null;

  // 목록
  records: SeveranceSummary[];
  isLoadingRecords: boolean;

  // Actions
  setCalculationResult: (result: SeveranceResult | null) => void;
  setSavedRecord: (record: SeveranceRecord | null) => void;
  setIsCalculating: (isCalculating: boolean) => void;
  setCalculateError: (error: string | null) => void;

  setTerminationGuide: (guide: TerminationGuide | null) => void;
  setIsGeneratingGuide: (isGenerating: boolean) => void;
  setGuideError: (error: string | null) => void;

  setRecords: (records: SeveranceSummary[]) => void;
  setIsLoadingRecords: (isLoading: boolean) => void;

  reset: () => void;
}

export const retirementStore = create<RetirementState>((set) => ({
  // 초기 상태
  calculationResult: null,
  savedRecord: null,
  isCalculating: false,
  calculateError: null,

  terminationGuide: null,
  isGeneratingGuide: false,
  guideError: null,

  records: [],
  isLoadingRecords: false,

  // Actions
  setCalculationResult: (result) => set({ calculationResult: result }),

  setSavedRecord: (record) => set({ savedRecord: record }),

  setIsCalculating: (isCalculating) => set({ isCalculating }),

  setCalculateError: (error) => set({ calculateError: error }),

  setTerminationGuide: (guide) => set({ terminationGuide: guide }),

  setIsGeneratingGuide: (isGenerating) => set({ isGeneratingGuide: isGenerating }),

  setGuideError: (error) => set({ guideError: error }),

  setRecords: (records) => set({ records }),

  setIsLoadingRecords: (isLoading) => set({ isLoadingRecords: isLoading }),

  reset: () =>
    set({
      calculationResult: null,
      savedRecord: null,
      isCalculating: false,
      calculateError: null,
      terminationGuide: null,
      isGeneratingGuide: false,
      guideError: null,
      records: [],
      isLoadingRecords: false,
    }),
}));
