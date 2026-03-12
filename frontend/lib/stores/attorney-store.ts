/**
 * 노무사 마켓플레이스 상태 관리 스토어
 */

import { create } from 'zustand';
import type { Attorney, AttorneyCase } from '@/types/attorney';

interface AttorneyState {
  attorneys: Attorney[];
  totalCount: number;
  myCases: AttorneyCase[];
  myCasesTotal: number;
  isLoading: boolean;
  error: string | null;

  setAttorneys: (attorneys: Attorney[], total: number) => void;
  setMyCases: (cases: AttorneyCase[], total: number) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  reset: () => void;
}

export const attorneyStore = create<AttorneyState>()((set) => ({
  attorneys: [],
  totalCount: 0,
  myCases: [],
  myCasesTotal: 0,
  isLoading: false,
  error: null,

  setAttorneys: (attorneys, total) => set({ attorneys, totalCount: total }),
  setMyCases: (cases, total) => set({ myCases: cases, myCasesTotal: total }),
  setLoading: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error }),
  reset: () =>
    set({
      attorneys: [],
      totalCount: 0,
      myCases: [],
      myCasesTotal: 0,
      isLoading: false,
      error: null,
    }),
}));
