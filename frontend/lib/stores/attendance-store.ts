/**
 * 근태 관리 상태 관리 스토어 (Zustand)
 * 근무 기록, 월별 요약, 패턴 분석 데이터 관리
 */

import { create } from 'zustand';
import type {
  WorkRecord,
  MonthlySummary,
  EmployeeAnalysis,
  ImportResult,
} from '@/types/attendance';

interface AttendanceState {
  // 근무 기록
  workRecords: WorkRecord[];
  currentRecord: WorkRecord | null;

  // 월별 요약
  monthlySummary: MonthlySummary | null;

  // 패턴 분석
  employeeAnalysis: EmployeeAnalysis | null;

  // 엑셀 업로드
  importResult: ImportResult | null;

  // 필터/상태
  selectedEmployeeId: string | null;
  selectedYear: number;
  selectedMonth: number;

  // Actions
  setWorkRecords: (records: WorkRecord[]) => void;
  addWorkRecord: (record: WorkRecord) => void;
  updateWorkRecord: (id: string, record: WorkRecord) => void;
  removeWorkRecord: (id: string) => void;
  setCurrentRecord: (record: WorkRecord | null) => void;

  setMonthlySummary: (summary: MonthlySummary | null) => void;
  setEmployeeAnalysis: (analysis: EmployeeAnalysis | null) => void;
  setImportResult: (result: ImportResult | null) => void;

  setSelectedEmployeeId: (id: string | null) => void;
  setSelectedYear: (year: number) => void;
  setSelectedMonth: (month: number) => void;

  clearAll: () => void;
}

const currentDate = new Date();

export const attendanceStore = create<AttendanceState>((set) => ({
  workRecords: [],
  currentRecord: null,
  monthlySummary: null,
  employeeAnalysis: null,
  importResult: null,
  selectedEmployeeId: null,
  selectedYear: currentDate.getFullYear(),
  selectedMonth: currentDate.getMonth() + 1,

  setWorkRecords: (records) => set({ workRecords: records }),

  addWorkRecord: (record) =>
    set((state) => ({
      workRecords: [...state.workRecords, record],
    })),

  updateWorkRecord: (id, record) =>
    set((state) => ({
      workRecords: state.workRecords.map((r) =>
        r.id === id ? record : r
      ),
      currentRecord: state.currentRecord?.id === id ? record : state.currentRecord,
    })),

  removeWorkRecord: (id) =>
    set((state) => ({
      workRecords: state.workRecords.filter((r) => r.id !== id),
      currentRecord: state.currentRecord?.id === id ? null : state.currentRecord,
    })),

  setCurrentRecord: (record) => set({ currentRecord: record }),

  setMonthlySummary: (summary) => set({ monthlySummary: summary }),
  setEmployeeAnalysis: (analysis) => set({ employeeAnalysis: analysis }),
  setImportResult: (result) => set({ importResult: result }),

  setSelectedEmployeeId: (id) => set({ selectedEmployeeId: id }),
  setSelectedYear: (year) => set({ selectedYear: year }),
  setSelectedMonth: (month) => set({ selectedMonth: month }),

  clearAll: () =>
    set({
      workRecords: [],
      currentRecord: null,
      monthlySummary: null,
      employeeAnalysis: null,
      importResult: null,
      selectedEmployeeId: null,
    }),
}));
