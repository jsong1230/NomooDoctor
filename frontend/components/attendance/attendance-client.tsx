'use client';

/**
 * 근태 관리 클라이언트 컴포넌트
 * 탭 관리, 데이터 조회, 이벤트 핸들링
 */

import { useState, useEffect } from 'react';
import { Plus, Upload, Calendar } from 'lucide-react';
import { AttendanceTable } from './attendance-table';
import { RecordFormDialog } from './record-form-dialog';
import { MonthlySummaryComponent } from './monthly-summary';
import { AnalysisChart } from './analysis-chart';
import { ExcelUpload } from './excel-upload';
import { attendanceApi } from '@/lib/api/attendance';
import { employeeApi } from '@/lib/api/employee';
import { attendanceStore } from '@/lib/stores/attendance-store';
import type { WorkRecord } from '@/types/attendance';
import type { Employee } from '@/types/employee';

type TabType = 'records' | 'summary' | 'analysis';

interface UploadDialogState {
  isOpen: boolean;
  type: 'excel';
}

export function AttendanceClient() {
  const [activeTab, setActiveTab] = useState<TabType>('records');
  const [isLoading, setIsLoading] = useState(false);
  const [employees, setEmployees] = useState<Employee[]>([]);

  // Dialog 상태
  const [recordDialog, setRecordDialog] = useState({
    isOpen: false,
    mode: 'create' as 'create' | 'edit',
    record: null as WorkRecord | null,
  });

  const [uploadDialog, setUploadDialog] = useState<UploadDialogState>({
    isOpen: false,
    type: 'excel',
  });

  // 필터 및 상태
  const [selectedEmployeeId, setSelectedEmployeeId] = useState<string | null>(null);
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
  const [selectedMonth, setSelectedMonth] = useState(new Date().getMonth() + 1);
  const [selectedAnalysisEmployeeId, setSelectedAnalysisEmployeeId] = useState<string | null>(null);

  // 스토어에서 데이터 가져오기
  const workRecords = attendanceStore((state) => state.workRecords);
  const monthlySummary = attendanceStore((state) => state.monthlySummary);
  const employeeAnalysis = attendanceStore((state) => state.employeeAnalysis);

  // 초기화: 직원 목록 조회
  useEffect(() => {
    const loadEmployees = async () => {
      try {
        const response = await employeeApi.getEmployees({ limit: 1000 });
        setEmployees(response.data);
      } catch (err) {
        console.error('직원 목록 조회 실패:', err);
      }
    };
    loadEmployees();
  }, []);

  // 근무 기록 조회
  const loadWorkRecords = async () => {
    setIsLoading(true);
    try {
      const params = {
        employee_id: selectedEmployeeId || undefined,
        year: selectedYear,
        month: selectedMonth,
        limit: 200,
      };
      const response = await attendanceApi.getWorkRecords(params);
      attendanceStore.getState().setWorkRecords(response.data);
    } catch (err) {
      console.error('근무 기록 조회 실패:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // 월별 요약 조회
  const loadMonthlySummary = async () => {
    setIsLoading(true);
    try {
      const summary = await attendanceApi.getMonthlySummary({
        year: selectedYear,
        month: selectedMonth,
        employee_id: selectedEmployeeId || undefined,
      });
      attendanceStore.getState().setMonthlySummary(summary);
    } catch (err) {
      console.error('월별 요약 조회 실패:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // 패턴 분석 조회
  const loadEmployeeAnalysis = async (employeeId: string) => {
    setIsLoading(true);
    try {
      const analysis = await attendanceApi.getEmployeeAnalysis({
        employee_id: employeeId,
      });
      attendanceStore.getState().setEmployeeAnalysis(analysis);
    } catch (err) {
      console.error('패턴 분석 조회 실패:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // 탭 변경 시 데이터 로드
  useEffect(() => {
    if (activeTab === 'records') {
      loadWorkRecords();
    } else if (activeTab === 'summary') {
      loadMonthlySummary();
    }
  }, [activeTab, selectedEmployeeId, selectedYear, selectedMonth]);

  // 패턴 분석 탭 선택 직원 변경 시
  useEffect(() => {
    if (activeTab === 'analysis' && selectedAnalysisEmployeeId) {
      loadEmployeeAnalysis(selectedAnalysisEmployeeId);
    }
  }, [activeTab, selectedAnalysisEmployeeId]);

  // 기록 행 클릭
  const handleRowClick = (record: WorkRecord) => {
    setRecordDialog({
      isOpen: true,
      mode: 'edit',
      record,
    });
  };

  // 기록 생성
  const handleCreateRecord = () => {
    setRecordDialog({
      isOpen: true,
      mode: 'create',
      record: null,
    });
  };

  // 업로드 성공
  const handleUploadSuccess = () => {
    setUploadDialog({ isOpen: false, type: 'excel' });
    loadWorkRecords();
  };

  return (
    <div className="min-h-screen bg-slate-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* 페이지 헤더 */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-slate-900">근태 관리</h1>
          <p className="text-slate-600 mt-2">직원의 근무 기록과 근태 패턴을 관리합니다</p>
        </div>

        {/* 년/월 선택 */}
        <div className="mb-6 p-4 bg-white border border-slate-200 rounded-lg flex flex-col sm:flex-row gap-4 items-start sm:items-center">
          <div className="flex items-center gap-2">
            <Calendar className="w-5 h-5 text-slate-600" />
            <span className="text-sm font-medium text-slate-700">조회 기간:</span>
          </div>
          <div className="flex gap-3">
            <select
              value={selectedYear}
              onChange={(e) => setSelectedYear(Number(e.target.value))}
              className="px-3 py-2 border border-slate-300 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              {[2023, 2024, 2025, 2026, 2027].map((year) => (
                <option key={year} value={year}>
                  {year}년
                </option>
              ))}
            </select>
            <select
              value={selectedMonth}
              onChange={(e) => setSelectedMonth(Number(e.target.value))}
              className="px-3 py-2 border border-slate-300 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map((month) => (
                <option key={month} value={month}>
                  {month}월
                </option>
              ))}
            </select>
          </div>

          {/* 직원 필터 (근무기록/월별요약 탭) */}
          {(activeTab === 'records' || activeTab === 'summary') && (
            <div className="flex items-center gap-2 ml-auto">
              <span className="text-sm font-medium text-slate-700">직원:</span>
              <select
                value={selectedEmployeeId || ''}
                onChange={(e) => setSelectedEmployeeId(e.target.value || null)}
                className="px-3 py-2 border border-slate-300 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="">전체</option>
                {employees.map((emp) => (
                  <option key={emp.id} value={emp.id}>
                    {emp.name}
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* 직원 선택 (패턴분석 탭) */}
          {activeTab === 'analysis' && (
            <div className="flex items-center gap-2 ml-auto">
              <span className="text-sm font-medium text-slate-700">분석 대상:</span>
              <select
                value={selectedAnalysisEmployeeId || ''}
                onChange={(e) => setSelectedAnalysisEmployeeId(e.target.value || null)}
                className="px-3 py-2 border border-slate-300 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="">직원을 선택해주세요</option>
                {employees.map((emp) => (
                  <option key={emp.id} value={emp.id}>
                    {emp.name}
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>

        {/* 탭 */}
        <div className="mb-6 border-b border-slate-200 bg-white rounded-t-lg">
          <div className="flex gap-0 px-6">
            {[
              { id: 'records' as const, label: '근무 기록', icon: '📋' },
              { id: 'summary' as const, label: '월별 요약', icon: '📊' },
              { id: 'analysis' as const, label: '패턴 분석', icon: '📈' },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-3 font-medium border-b-2 transition-colors ${
                  activeTab === tab.id
                    ? 'border-primary-600 text-primary-600'
                    : 'border-transparent text-slate-600 hover:text-slate-900'
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* 탭 콘텐츠 */}
        <div className="bg-white rounded-b-lg border border-t-0 border-slate-200 p-6">
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="text-slate-600">로딩 중...</div>
            </div>
          ) : activeTab === 'records' ? (
            <div>
              {/* 액션 버튼 */}
              <div className="flex gap-3 mb-6">
                <button
                  onClick={handleCreateRecord}
                  className="flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-lg transition-colors"
                >
                  <Plus className="w-4 h-4" />
                  기록 추가
                </button>
                <button
                  onClick={() => setUploadDialog({ isOpen: true, type: 'excel' })}
                  className="flex items-center gap-2 px-4 py-2 bg-slate-200 hover:bg-slate-300 text-slate-900 font-medium rounded-lg transition-colors"
                >
                  <Upload className="w-4 h-4" />
                  엑셀 업로드
                </button>
              </div>

              {/* 근무 기록 테이블 */}
              <AttendanceTable records={workRecords} onRowClick={handleRowClick} />
            </div>
          ) : activeTab === 'summary' && monthlySummary ? (
            <MonthlySummaryComponent summary={monthlySummary} />
          ) : activeTab === 'analysis' && employeeAnalysis ? (
            <AnalysisChart analysis={employeeAnalysis} />
          ) : (
            <div className="text-center py-12 text-slate-500">
              {activeTab === 'analysis'
                ? '분석할 직원을 선택해주세요'
                : '데이터가 없습니다'}
            </div>
          )}
        </div>
      </div>

      {/* 기록 다이얼로그 */}
      <RecordFormDialog
        isOpen={recordDialog.isOpen}
        employees={employees}
        record={recordDialog.record || undefined}
        mode={recordDialog.mode}
        onClose={() => setRecordDialog({ isOpen: false, mode: 'create', record: null })}
        onSuccess={loadWorkRecords}
      />

      {/* 엑셀 업로드 다이얼로그 */}
      {uploadDialog.isOpen && uploadDialog.type === 'excel' && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div className="absolute inset-0 bg-black/50" onClick={() => setUploadDialog({ isOpen: false, type: 'excel' })} />
          <div className="relative bg-white rounded-lg shadow-xl max-w-md w-full mx-4 p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-semibold text-slate-900">엑셀 업로드</h2>
              <button
                type="button"
                onClick={() => setUploadDialog({ isOpen: false, type: 'excel' })}
                className="p-1 hover:bg-slate-100 rounded-lg transition-colors"
              >
                ✕
              </button>
            </div>
            <ExcelUpload onSuccess={handleUploadSuccess} />
          </div>
        </div>
      )}
    </div>
  );
}
