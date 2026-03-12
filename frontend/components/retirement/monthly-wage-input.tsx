'use client';

/**
 * 최근 3개월 급여 입력 폼 컴포넌트
 */

import { useState } from 'react';
import { AlertCircle } from 'lucide-react';
import type { MonthlyWageInput } from '@/types/retirement';

interface MonthlyWageInputProps {
  onWagesChange?: (wages: MonthlyWageInput[]) => void;
  initialWages?: MonthlyWageInput[];
  disabled?: boolean;
}

export function MonthlyWageInput({
  onWagesChange,
  initialWages = [],
  disabled = false
}: MonthlyWageInputProps) {
  const [wages, setWages] = useState<MonthlyWageInput[]>(
    initialWages.length > 0
      ? initialWages
      : Array.from({ length: 3 }, (_, i) => ({
          year: new Date().getFullYear(),
          month: new Date().getMonth() - (2 - i),
          total_wage: 0,
          days_in_month: 30,
        }))
  );

  const handleWageChange = (index: number, field: keyof MonthlyWageInput, value: number | string) => {
    const updated = [...wages];
    updated[index] = {
      ...updated[index],
      [field]: typeof value === 'string' ? parseInt(value) : value,
    };
    setWages(updated);
    onWagesChange?.(updated);
  };

  return (
    <div className="space-y-4">
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 flex gap-2">
        <AlertCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
        <p className="text-sm text-blue-700">
          최근 3개월의 급여 정보를 입력하면 평균임금을 정확하게 계산할 수 있습니다.
        </p>
      </div>

      <div className="grid gap-4">
        {wages.map((wage, index) => (
          <div key={index} className="border rounded-lg p-4 space-y-3">
            <div className="flex justify-between items-center">
              <h4 className="font-medium text-gray-900">
                {wage.year}년 {wage.month}월
              </h4>
              <span className="text-sm text-gray-500">
                {index === 0 ? '3개월 전' : index === 1 ? '2개월 전' : '1개월 전'}
              </span>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  총 급여액
                </label>
                <input
                  type="number"
                  value={wage.total_wage || ''}
                  onChange={(e) => handleWageChange(index, 'total_wage', e.target.value)}
                  disabled={disabled}
                  placeholder="0"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:text-gray-500"
                />
                <p className="text-xs text-gray-500 mt-1">
                  {wage.total_wage.toLocaleString('ko-KR')}원
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  해당월 일수
                </label>
                <input
                  type="number"
                  value={wage.days_in_month || ''}
                  onChange={(e) => handleWageChange(index, 'days_in_month', e.target.value)}
                  disabled={disabled}
                  min={28}
                  max={31}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:text-gray-500"
                />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
