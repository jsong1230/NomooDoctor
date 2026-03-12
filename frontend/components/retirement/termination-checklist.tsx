'use client';

/**
 * 해고/퇴직 절차 체크리스트 컴포넌트
 */

import { CheckCircle2, Circle } from 'lucide-react';
import { useState } from 'react';
import type { ChecklistItem } from '@/types/retirement';

interface TerminationChecklistProps {
  items: ChecklistItem[];
  onChange?: (items: ChecklistItem[]) => void;
  readonly?: boolean;
}

export function TerminationChecklist({
  items,
  onChange,
  readonly = false
}: TerminationChecklistProps) {
  const [checklist, setChecklist] = useState<ChecklistItem[]>(items);

  const handleToggle = (index: number) => {
    if (readonly) return;

    const updated = [...checklist];
    updated[index] = {
      ...updated[index],
      completed: !updated[index].completed,
    };
    setChecklist(updated);
    onChange?.(updated);
  };

  const completedCount = checklist.filter(item => item.completed).length;
  const totalRequired = checklist.filter(item => item.required).length;

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="font-semibold text-gray-900">진행 체크리스트</h3>
        <span className="text-sm text-gray-600">
          {completedCount} / {totalRequired} 완료
        </span>
      </div>

      {/* 진행도 바 */}
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className="bg-blue-600 h-2 rounded-full transition-all duration-300"
          style={{
            width: totalRequired > 0 ? `${(completedCount / totalRequired) * 100}%` : '0%',
          }}
        />
      </div>

      {/* 체크리스트 항목들 */}
      <div className="space-y-2">
        {checklist.map((item, index) => (
          <button
            key={index}
            onClick={() => handleToggle(index)}
            disabled={readonly}
            className="w-full text-left border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition disabled:cursor-not-allowed"
          >
            <div className="flex gap-3">
              <div className="flex-shrink-0 pt-0.5">
                {item.completed ? (
                  <CheckCircle2 className="w-5 h-5 text-green-600" />
                ) : (
                  <Circle className="w-5 h-5 text-gray-400" />
                )}
              </div>
              <div className="flex-1">
                <div className="flex justify-between items-start gap-2">
                  <div>
                    <h4 className={`font-medium ${
                      item.completed ? 'text-gray-500 line-through' : 'text-gray-900'
                    }`}>
                      {item.step}. {item.title}
                    </h4>
                    <p className="text-sm text-gray-600 mt-1">
                      {item.description}
                    </p>
                  </div>
                  {item.required && (
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800 flex-shrink-0">
                      필수
                    </span>
                  )}
                </div>
              </div>
            </div>
          </button>
        ))}
      </div>

      {/* 완료 상태 */}
      {completedCount === totalRequired && totalRequired > 0 && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-center">
          <p className="text-green-800 font-medium">
            모든 필수 항목을 완료했습니다!
          </p>
        </div>
      )}
    </div>
  );
}
