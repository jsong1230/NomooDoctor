'use client';

/**
 * 근무 기록 입력/수정 폼 컴포넌트
 * react-hook-form + zod 검증
 */

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useState, useMemo } from 'react';
import { AlertCircle, Loader2 } from 'lucide-react';
import type { WorkRecord, WorkRecordCreate, WorkRecordUpdate } from '@/types/attendance';
import type { Employee } from '@/types/employee';

// 시간 형식 검증 (HH:MM)
const timeRegex = /^([01]\d|2[0-3]):([0-5]\d)$/;

const workRecordSchema = z.object({
  employee_id: z.string().min(1, '직원을 선택해주세요'),
  work_date: z.string().min(1, '근무일을 선택해주세요'),
  scheduled_start: z
    .string()
    .min(1, '예정 출근시간을 입력해주세요')
    .regex(timeRegex, '시간 형식이 올바르지 않습니다. (HH:MM)'),
  scheduled_end: z
    .string()
    .min(1, '예정 퇴근시간을 입력해주세요')
    .regex(timeRegex, '시간 형식이 올바르지 않습니다. (HH:MM)'),
  actual_start: z
    .string()
    .refine(
      (val) => val === '' || timeRegex.test(val),
      '시간 형식이 올바르지 않습니다. (HH:MM)'
    )
    .optional(),
  actual_end: z
    .string()
    .refine(
      (val) => val === '' || timeRegex.test(val),
      '시간 형식이 올바르지 않습니다. (HH:MM)'
    )
    .optional(),
  break_minutes: z
    .number()
    .int('휴게시간은 정수로 입력해주세요')
    .min(0, '휴게시간은 0 이상이어야 합니다')
    .max(480, '휴게시간은 480분 이하여야 합니다'),
  is_holiday: z.boolean().default(false),
  memo: z.string().max(500, '비고는 500자 이내로 입력해주세요').optional(),
});

type WorkRecordFormValues = z.infer<typeof workRecordSchema>;

interface RecordFormProps {
  employees: Employee[];
  record?: WorkRecord;
  mode?: 'create' | 'edit';
  onSuccess?: () => void;
  onSubmit: (data: WorkRecordCreate | WorkRecordUpdate) => Promise<void>;
  isLoading?: boolean;
}

/**
 * 시간 문자열을 분으로 변환
 */
function timeToMinutes(time: string): number {
  if (!time) return 0;
  const [hours, minutes] = time.split(':').map(Number);
  return hours * 60 + minutes;
}

/**
 * 근무시간 계산
 * 실제 출퇴근 - 휴게시간
 */
function calculateWorkMinutes(
  actualStart: string | null,
  actualEnd: string | null,
  breakMinutes: number
): number {
  if (!actualStart || !actualEnd) return 0;

  let startMin = timeToMinutes(actualStart);
  let endMin = timeToMinutes(actualEnd);

  // 자정을 넘기는 경우
  if (endMin <= startMin) {
    endMin += 24 * 60;
  }

  return Math.max(0, endMin - startMin - breakMinutes);
}

/**
 * 야간근무시간 계산 (22:00 ~ 06:00)
 */
function calculateNightMinutes(
  actualStart: string | null,
  actualEnd: string | null
): number {
  if (!actualStart || !actualEnd) return 0;

  const startMin = timeToMinutes(actualStart);
  const endMin = timeToMinutes(actualEnd);
  const night_start = 22 * 60; // 22:00
  const night_end = 6 * 60; // 06:00 (다음날)

  // 당일 야간대 (22:00~24:00)
  const overlap1 = Math.max(
    0,
    Math.min(endMin > startMin ? endMin : 24 * 60, 24 * 60) -
      Math.max(startMin, night_start)
  );

  // 다음날 야간대 (0:00~6:00)
  let overlap2 = 0;
  if (endMin > 24 * 60 || (endMin <= startMin)) {
    const nextDayEnd = endMin > 24 * 60 ? endMin - 24 * 60 : endMin;
    const nextDayStart = startMin > 24 * 60 ? startMin - 24 * 60 : 0;
    overlap2 = Math.max(0, Math.min(nextDayEnd, night_end) - nextDayStart);
  }

  return Math.max(0, overlap1 + overlap2);
}

/**
 * 연장근무시간 계산
 */
function calculateOvertimeMinutes(
  actualStart: string | null,
  actualEnd: string | null,
  scheduledStart: string,
  scheduledEnd: string,
  breakMinutes: number,
  isHoliday: boolean
): number {
  if (isHoliday || !actualStart || !actualEnd) return 0;

  const actualWork = calculateWorkMinutes(actualStart, actualEnd, breakMinutes);
  const scheduledWork = calculateWorkMinutes(scheduledStart, scheduledEnd, breakMinutes);

  return Math.max(0, actualWork - scheduledWork);
}

export function RecordForm({
  employees,
  record,
  mode = 'create',
  onSubmit,
  isLoading = false,
}: RecordFormProps) {
  const isEditMode = mode === 'edit' && record;
  const [submitError, setSubmitError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<WorkRecordFormValues>({
    resolver: zodResolver(workRecordSchema),
    defaultValues: record
      ? {
          employee_id: record.employee_id,
          work_date: record.work_date,
          scheduled_start: record.scheduled_start,
          scheduled_end: record.scheduled_end,
          actual_start: record.actual_start || '',
          actual_end: record.actual_end || '',
          break_minutes: record.break_minutes,
          is_holiday: record.is_holiday,
          memo: record.memo || '',
        }
      : {
          employee_id: '',
          work_date: new Date().toISOString().split('T')[0],
          scheduled_start: '09:00',
          scheduled_end: '18:00',
          actual_start: '',
          actual_end: '',
          break_minutes: 60,
          is_holiday: false,
          memo: '',
        },
  });

  const actualStart = watch('actual_start');
  const actualEnd = watch('actual_end');
  const scheduledStart = watch('scheduled_start');
  const scheduledEnd = watch('scheduled_end');
  const breakMinutes = watch('break_minutes');
  const isHoliday = watch('is_holiday');

  // 실시간 계산
  const preview = useMemo(() => {
    const totalWork = calculateWorkMinutes(actualStart, actualEnd, breakMinutes);
    const overtime = calculateOvertimeMinutes(
      actualStart,
      actualEnd,
      scheduledStart,
      scheduledEnd,
      breakMinutes,
      isHoliday
    );
    const night = calculateNightMinutes(actualStart, actualEnd);

    return { totalWork, overtime, night };
  }, [actualStart, actualEnd, scheduledStart, scheduledEnd, breakMinutes, isHoliday]);

  const handleFormSubmit = async (data: WorkRecordFormValues) => {
    setSubmitError(null);

    try {
      const submitData = isEditMode
        ? ({
            work_date: data.work_date,
            scheduled_start: data.scheduled_start,
            scheduled_end: data.scheduled_end,
            actual_start: data.actual_start || null,
            actual_end: data.actual_end || null,
            break_minutes: data.break_minutes,
            is_holiday: data.is_holiday,
            memo: data.memo || null,
          } as WorkRecordUpdate)
        : ({
            employee_id: data.employee_id,
            work_date: data.work_date,
            scheduled_start: data.scheduled_start,
            scheduled_end: data.scheduled_end,
            actual_start: data.actual_start || null,
            actual_end: data.actual_end || null,
            break_minutes: data.break_minutes,
            is_holiday: data.is_holiday,
            memo: data.memo || null,
          } as WorkRecordCreate);

      await onSubmit(submitData);
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || '요청에 실패했습니다';
      setSubmitError(errorMessage);
    }
  };

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className="flex flex-col gap-5">
      {/* 전체 에러 메시지 */}
      {submitError && (
        <div className="p-3 bg-error-50 border border-error-200 rounded-lg text-error-700 text-sm flex items-start gap-2">
          <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
          <span>{submitError}</span>
        </div>
      )}

      {/* 직원 선택 */}
      <div className="flex flex-col gap-1">
        <label htmlFor="employee_id" className="text-sm font-medium text-slate-700">
          직원 <span className="text-error-600">*</span>
        </label>
        <select
          id="employee_id"
          {...register('employee_id')}
          disabled={isLoading || isSubmitting || isEditMode}
          className={`
            w-full px-3 py-2.5
            border rounded-lg
            text-slate-900 bg-white
            focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent
            disabled:bg-slate-100 disabled:text-slate-500 disabled:cursor-not-allowed
            transition-shadow duration-200
            ${errors.employee_id ? 'border-error-500' : 'border-slate-300'}
          `}
        >
          <option value="">직원을 선택해주세요</option>
          {employees.map((emp) => (
            <option key={emp.id} value={emp.id}>
              {emp.name}
            </option>
          ))}
        </select>
        {errors.employee_id && (
          <p className="text-sm text-error-600">{errors.employee_id.message}</p>
        )}
      </div>

      {/* 근무일 */}
      <div className="flex flex-col gap-1">
        <label htmlFor="work_date" className="text-sm font-medium text-slate-700">
          근무일 <span className="text-error-600">*</span>
        </label>
        <input
          id="work_date"
          type="date"
          {...register('work_date')}
          disabled={isLoading || isSubmitting}
          className={`
            w-full px-3 py-2.5
            border rounded-lg
            text-slate-900 bg-white
            focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent
            disabled:bg-slate-100 disabled:text-slate-500 disabled:cursor-not-allowed
            transition-shadow duration-200
            ${errors.work_date ? 'border-error-500' : 'border-slate-300'}
          `}
        />
        {errors.work_date && (
          <p className="text-sm text-error-600">{errors.work_date.message}</p>
        )}
      </div>

      {/* 예정 시간 (2열 레이아웃) */}
      <div className="grid grid-cols-2 gap-4">
        <div className="flex flex-col gap-1">
          <label htmlFor="scheduled_start" className="text-sm font-medium text-slate-700">
            예정 출근 <span className="text-error-600">*</span>
          </label>
          <input
            id="scheduled_start"
            type="text"
            placeholder="HH:MM"
            {...register('scheduled_start')}
            disabled={isLoading || isSubmitting}
            maxLength={5}
            className={`
              w-full px-3 py-2.5
              border rounded-lg
              text-slate-900 bg-white font-mono
              focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent
              disabled:bg-slate-100 disabled:text-slate-500 disabled:cursor-not-allowed
              transition-shadow duration-200
              ${errors.scheduled_start ? 'border-error-500' : 'border-slate-300'}
            `}
          />
          {errors.scheduled_start && (
            <p className="text-sm text-error-600">{errors.scheduled_start.message}</p>
          )}
        </div>

        <div className="flex flex-col gap-1">
          <label htmlFor="scheduled_end" className="text-sm font-medium text-slate-700">
            예정 퇴근 <span className="text-error-600">*</span>
          </label>
          <input
            id="scheduled_end"
            type="text"
            placeholder="HH:MM"
            {...register('scheduled_end')}
            disabled={isLoading || isSubmitting}
            maxLength={5}
            className={`
              w-full px-3 py-2.5
              border rounded-lg
              text-slate-900 bg-white font-mono
              focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent
              disabled:bg-slate-100 disabled:text-slate-500 disabled:cursor-not-allowed
              transition-shadow duration-200
              ${errors.scheduled_end ? 'border-error-500' : 'border-slate-300'}
            `}
          />
          {errors.scheduled_end && (
            <p className="text-sm text-error-600">{errors.scheduled_end.message}</p>
          )}
        </div>
      </div>

      {/* 실제 시간 (2열 레이아웃) */}
      <div className="grid grid-cols-2 gap-4">
        <div className="flex flex-col gap-1">
          <label htmlFor="actual_start" className="text-sm font-medium text-slate-700">
            실제 출근
          </label>
          <input
            id="actual_start"
            type="text"
            placeholder="HH:MM"
            {...register('actual_start')}
            disabled={isLoading || isSubmitting}
            maxLength={5}
            className={`
              w-full px-3 py-2.5
              border rounded-lg
              text-slate-900 bg-white font-mono
              focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent
              disabled:bg-slate-100 disabled:text-slate-500 disabled:cursor-not-allowed
              transition-shadow duration-200
              ${errors.actual_start ? 'border-error-500' : 'border-slate-300'}
            `}
          />
          {errors.actual_start && (
            <p className="text-sm text-error-600">{errors.actual_start.message}</p>
          )}
        </div>

        <div className="flex flex-col gap-1">
          <label htmlFor="actual_end" className="text-sm font-medium text-slate-700">
            실제 퇴근
          </label>
          <input
            id="actual_end"
            type="text"
            placeholder="HH:MM"
            {...register('actual_end')}
            disabled={isLoading || isSubmitting}
            maxLength={5}
            className={`
              w-full px-3 py-2.5
              border rounded-lg
              text-slate-900 bg-white font-mono
              focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent
              disabled:bg-slate-100 disabled:text-slate-500 disabled:cursor-not-allowed
              transition-shadow duration-200
              ${errors.actual_end ? 'border-error-500' : 'border-slate-300'}
            `}
          />
          {errors.actual_end && (
            <p className="text-sm text-error-600">{errors.actual_end.message}</p>
          )}
        </div>
      </div>

      {/* 휴게시간 */}
      <div className="flex flex-col gap-1">
        <label htmlFor="break_minutes" className="text-sm font-medium text-slate-700">
          휴게시간 (분)
        </label>
        <input
          id="break_minutes"
          type="number"
          min="0"
          max="480"
          {...register('break_minutes', { valueAsNumber: true })}
          disabled={isLoading || isSubmitting}
          className={`
            w-full px-3 py-2.5
            border rounded-lg
            text-slate-900 bg-white
            focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent
            disabled:bg-slate-100 disabled:text-slate-500 disabled:cursor-not-allowed
            transition-shadow duration-200
            ${errors.break_minutes ? 'border-error-500' : 'border-slate-300'}
          `}
        />
        {errors.break_minutes && (
          <p className="text-sm text-error-600">{errors.break_minutes.message}</p>
        )}
      </div>

      {/* 휴일 여부 */}
      <div className="flex items-center gap-3">
        <input
          id="is_holiday"
          type="checkbox"
          {...register('is_holiday')}
          disabled={isLoading || isSubmitting}
          className="w-4 h-4 rounded border-slate-300 text-primary-600 focus:ring-2 focus:ring-primary-500"
        />
        <label htmlFor="is_holiday" className="text-sm font-medium text-slate-700">
          휴일 근무
        </label>
      </div>

      {/* 비고 */}
      <div className="flex flex-col gap-1">
        <label htmlFor="memo" className="text-sm font-medium text-slate-700">
          비고
        </label>
        <textarea
          id="memo"
          {...register('memo')}
          disabled={isLoading || isSubmitting}
          placeholder="특이사항을 입력해주세요"
          rows={3}
          className={`
            w-full px-3 py-2.5
            border rounded-lg
            text-slate-900 placeholder-slate-400 bg-white
            focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent
            disabled:bg-slate-100 disabled:text-slate-500 disabled:cursor-not-allowed
            transition-shadow duration-200
            resize-none
            ${errors.memo ? 'border-error-500' : 'border-slate-300'}
          `}
        />
        {errors.memo && (
          <p className="text-sm text-error-600">{errors.memo.message}</p>
        )}
      </div>

      {/* 실시간 미리보기 */}
      {(actualStart || actualEnd) && (
        <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg text-sm text-blue-900 space-y-1">
          <div>근무시간: {Math.floor(preview.totalWork / 60)}시간 {preview.totalWork % 60}분</div>
          {preview.overtime > 0 && <div>연장근무: {Math.floor(preview.overtime / 60)}시간 {preview.overtime % 60}분</div>}
          {preview.night > 0 && <div>야간근무: {Math.floor(preview.night / 60)}시간 {preview.night % 60}분</div>}
        </div>
      )}

      {/* 제출 버튼 */}
      <button
        type="submit"
        disabled={isLoading || isSubmitting}
        className="
          w-full py-3
          bg-primary-600 hover:bg-primary-700 active:bg-primary-800
          text-white font-semibold
          rounded-lg
          transition-colors duration-200
          disabled:bg-slate-300 disabled:cursor-not-allowed
          flex items-center justify-center gap-2
        "
      >
        {isLoading || isSubmitting ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin" />
            {isEditMode ? '수정 중...' : '등록 중...'}
          </>
        ) : (
          isEditMode ? '근무 기록 수정' : '근무 기록 등록'
        )}
      </button>
    </form>
  );
}
