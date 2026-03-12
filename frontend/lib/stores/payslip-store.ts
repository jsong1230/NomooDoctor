/**
 * 급여명세서 상태 관리 스토어 (Zustand)
 * 급여명세서 목록 및 선택된 명세서 상태 관리
 */

import { create } from 'zustand';
import type { Payslip } from '@/types/payslip';

interface PayslipState {
  payslips: Payslip[];
  selectedPayslip: Payslip | null;

  // Actions
  setPayslips: (payslips: Payslip[]) => void;
  setSelectedPayslip: (payslip: Payslip | null) => void;
  addPayslip: (payslip: Payslip) => void;
  updatePayslip: (id: string, updates: Partial<Payslip>) => void;
}

export const payslipStore = create<PayslipState>()((set, get) => ({
  payslips: [],
  selectedPayslip: null,

  setPayslips: (payslips) => set({ payslips }),

  setSelectedPayslip: (payslip) => set({ selectedPayslip: payslip }),

  addPayslip: (payslip) =>
    set((state) => ({
      payslips: [...state.payslips, payslip],
    })),

  updatePayslip: (id, updates) =>
    set((state) => ({
      payslips: state.payslips.map((p) =>
        p.id === id ? { ...p, ...updates } : p
      ),
      selectedPayslip:
        state.selectedPayslip?.id === id
          ? { ...state.selectedPayslip, ...updates }
          : state.selectedPayslip,
    })),
}));
