'use client';

/**
 * 퇴직금 계산 폼 컴포넌트
 * 직원 선택, 퇴직일, 추가 정보 입력 후 계산
 */

import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { AlertCircle, Loader2 } from 'lucide-react';
import { calculateSeverance, createSeverance } from '@/lib/api/retirement';
import { retirementStore } from '@/lib/stores/retirement-store';
import { SeveranceResultCard } from './severance-result-card';
import { MonthlyWageInput } from './monthly-wage-input';
import type { SeveranceCalculateRequest, MonthlyWageInput as MonthlyWageType } from '@/types/retirement';

// 유효성 검증 스키마
const severanceSchema = z.object({
  employee_id: z.string().min(1, '직원을 선택해주세요'),
  resign_date: z.string().min(1, '퇴직일을 입력해주세요'),
  annual_bonus: z.coerce.number().min(0, '상여금은 0 이상이어야 합니다').default(0),
  unused_annual_leave_days: z.coerce
    .number()
    .min(0, '미사용 연차는 0 이상이어야 합니다')
    .max(40, '미사용 연차는 40일 이하여야 합니다')
    .default(0),
});

type SeveranceFormValues = z.infer<typeof severanceSchema>;

interface SeveranceCalculatorProps {
  employees?: Array<{ id: string; name: string }>;
  onCalculated?: () => void;
}

export function SeveranceCalculator({
  employees = [],
  onCalculated
}: SeveranceCalculatorProps) {
  const [manualWages, setManualWages] = useState<MonthlyWageType[]>([]);
  const [showWageInput, setShowWageInput] = useState(false);

  const {
    calculationResult,
    savedRecord,
    isCalculating,
    calculateError,
    setCalculationResult,
    setSavedRecord,
    setIsCalculating,
    setCalculateError,
  } = retirementStore();

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting },
    reset,
  } = useForm<SeveranceFormValues>({
    resolver: zodResolver(severanceSchema),
    defaultValues: {
      employee_id: '',
      resign_date: '',
      annual_bonus: 0,
      unused_annual_leave_days: 0,
    },
  });

  const resignDate = watch('resign_date');
  const employeeId = watch('employee_id');

  // 퇴직금 계산 처리
  const onSubmit = async (values: SeveranceFormValues) => {
    setIsCalculating(true);
    setCalculateError(null);

    try {
      const request: SeveranceCalculateRequest = {
        employee_id: values.employee_id,
        resign_date: values.resign_date,
        annual_bonus: values.annual_bonus,
        unused_annual_leave_days: values.unused_annual_leave_days,
        ...(manualWages.length > 0 && { monthly_wages: manualWages }),
      };

      const result = await calculateSeverance(request);
      setCalculationResult(result);
      setSavedRecord(null);
      onCalculated?.();
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : '계산 중 오류가 발생했습니다.';
      setCalculateError(errorMessage);
      setCalculationResult(null);
    } finally {
      setIsCalculating(false);
    }
  };

  // 퇴직금 확정 저장
  const handleSave = async () => {
    if (!calculationResult) return;

    setIsCalculating(true);
    setCalculateError(null);

    try {
      const request: SeveranceCalculateRequest = {
        employee_id: calculationResult.employee_id,
        resign_date: calculationResult.resign_date,
        annual_bonus: calculationResult.bonus_included,
        unused_annual_leave_days: 0,
        ...(manualWages.length > 0 && { monthly_wages: manualWages }),
      };

      const record = await createSeverance(request);
      setSavedRecord(record);
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : '저장 중 오류가 발생했습니다.';
      setCalculateError(errorMessage);
    } finally {
      setIsCalculating(false);
    }
  };

  // 새로운 계산 시작
  const handleNewCalculation = () => {
    reset();
    setCalculationResult(null);
    setSavedRecord(null);
    setManualWages([]);
    setShowWageInput(false);
    setCalculateError(null);
  };

  // 저장 완료 후 상태 표시
  if (savedRecord) {
    return (
      <div className="space-y-6">
        <div className="bg-green-50 border border-green-200 rounded-lg p-6 text-center">
          <h3 className="font-semibold text-green-900 mb-2">퇴직금이 저장되었습니다</h3>
          <p className="text-green-700 text-sm mb-4">
            기록 ID: {savedRecord.id}
          </p>
          <button
            onClick={handleNewCalculation}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition"
          >
            새로운 계산하기
          </button>
        </div>
      </div>
    );
  }

  // 계산 결과 표시
  if (calculationResult && !savedRecord) {
    return (
      <div className="space-y-6">
        <SeveranceResultCard
          result={calculationResult}
          onSave={handleSave}
          isSaving={isCalculating}
        />
        <button
          onClick={handleNewCalculation}
          className="w-full px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
        >
          다시 계산하기
        </button>
      </div>
    );
  }

  // 계산 폼
  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {/* 오류 메시지 */}
      {calculateError && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex gap-2">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-medium text-red-900">계산 오류</p>
            <p className="text-sm text-red-700">{calculateError}</p>
          </div>
        </div>
      )}

      {/* 직원 선택 */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          직원 <span className="text-red-600">*</span>
        </label>
        <select
          {...register('employee_id')}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">직원을 선택해주세요</option>
          {employees.map(emp => (
            <option key={emp.id} value={emp.id}>
              {emp.name}
            </option>
          ))}
        </select>
        {errors.employee_id && (
          <p className="text-red-600 text-sm mt-1">{errors.employee_id.message}</p>
        )}
      </div>

      {/* 퇴직일 */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          퇴직예정일 <span className="text-red-600">*</span>
        </label>
        <input
          type="date"
          {...register('resign_date')}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        {errors.resign_date && (
          <p className="text-red-600 text-sm mt-1">{errors.resign_date.message}</p>
        )}
      </div>

      {/* 상여금 */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          연간 상여금 (선택)
        </label>
        <input
          type="number"
          {...register('annual_bonus')}
          placeholder="0"
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        {errors.annual_bonus && (
          <p className="text-red-600 text-sm mt-1">{errors.annual_bonus.message}</p>
        )}
      </div>

      {/* 미사용 연차 */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          미사용 연차 일수 (선택)
        </label>
        <input
          type="number"
          {...register('unused_annual_leave_days')}
          placeholder="0"
          min={0}
          max={40}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        {errors.unused_annual_leave_days && (
          <p className="text-red-600 text-sm mt-1">{errors.unused_annual_leave_days.message}</p>
        )}
      </div>

      {/* 수동 급여 입력 토글 */}
      {(employeeId || resignDate) && (
        <div>
          <button
            type="button"
            onClick={() => setShowWageInput(!showWageInput)}
            className="text-blue-600 hover:text-blue-700 font-medium text-sm"
          >
            {showWageInput ? '급여 데이터 자동 조회로 변경' : '급여 데이터 수동 입력 (선택)'}
          </button>
        </div>
      )}

      {/* 급여 입력 폼 */}
      {showWageInput && (
        <MonthlyWageInput
          onWagesChange={setManualWages}
          initialWages={manualWages}
        />
      )}

      {/* 계산 버튼 */}
      <button
        type="submit"
        disabled={isSubmitting || isCalculating}
        className="w-full px-4 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:bg-blue-400 transition flex justify-center items-center gap-2"
      >
        {isCalculating ? (
          <>
            <Loader2 className="w-4 h-4 animate-spin" />
            계산 중...
          </>
        ) : (
          '퇴직금 계산하기'
        )}
      </button>
    </form>
  );
}
