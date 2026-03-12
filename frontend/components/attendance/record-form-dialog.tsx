'use client';

/**
 * 근무 기록 폼 다이얼로그 래퍼
 */

import { useState } from 'react';
import { X, Loader2 } from 'lucide-react';
import { RecordForm } from './record-form';
import { attendanceApi } from '@/lib/api/attendance';
import { attendanceStore } from '@/lib/stores/attendance-store';
import type { WorkRecord, WorkRecordCreate, WorkRecordUpdate } from '@/types/attendance';
import type { Employee } from '@/types/employee';

interface RecordFormDialogProps {
  isOpen: boolean;
  employees: Employee[];
  record?: WorkRecord;
  mode?: 'create' | 'edit';
  onClose: () => void;
  onSuccess?: () => void;
}

export function RecordFormDialog({
  isOpen,
  employees,
  record,
  mode = 'create',
  onClose,
  onSuccess,
}: RecordFormDialogProps) {
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (data: WorkRecordCreate | WorkRecordUpdate) => {
    setIsLoading(true);

    try {
      if (mode === 'edit' && record) {
        // 수정 모드
        const updated = await attendanceApi.updateWorkRecord(
          record.id,
          data as WorkRecordUpdate
        );
        attendanceStore.getState().updateWorkRecord(record.id, updated);
      } else {
        // 등록 모드
        const created = await attendanceApi.createWorkRecord(
          data as WorkRecordCreate
        );
        attendanceStore.getState().addWorkRecord(created);
      }

      onClose();
      onSuccess?.();
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />
      <div className="relative bg-white rounded-lg shadow-xl max-w-md w-full mx-4 p-6 max-h-[90vh] overflow-y-auto">
        {/* 헤더 */}
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-semibold text-slate-900">
            {mode === 'edit' ? '근무 기록 수정' : '근무 기록 등록'}
          </h2>
          <button
            type="button"
            onClick={onClose}
            className="p-1 hover:bg-slate-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* 폼 */}
        <RecordForm
          employees={employees}
          record={record}
          mode={mode}
          onSubmit={handleSubmit}
          isLoading={isLoading}
        />
      </div>
    </div>
  );
}
