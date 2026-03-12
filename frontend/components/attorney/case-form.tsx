'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { attorneyApi } from '@/lib/api/attorney';
import {
  CASE_TYPE_LABELS,
  URGENCY_LABELS,
  CONSULTATION_TYPE_LABELS,
  type CaseType,
  type Urgency,
  type ConsultationType,
  type Attorney,
} from '@/types/attorney';

interface CaseFormProps {
  attorney: Attorney;
  onSuccess: () => void;
  onCancel: () => void;
}

export function CaseForm({ attorney, onSuccess, onCancel }: CaseFormProps) {
  const [caseType, setCaseType] = useState<CaseType>('other');
  const [urgency, setUrgency] = useState<Urgency>('medium');
  const [consultationType, setConsultationType] = useState<ConsultationType>('video');
  const [description, setDescription] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);
    try {
      await attorneyApi.createCase({
        attorney_id: attorney.id,
        case_type: caseType,
        urgency,
        consultation_type: consultationType,
        description: description || undefined,
      });
      onSuccess();
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { error?: { message?: string } } } };
      setError(axiosErr.response?.data?.error?.message || '상담 신청에 실패했습니다.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      <div className="rounded-lg bg-slate-50 p-4">
        <p className="text-sm text-slate-500">상담 노무사</p>
        <p className="font-semibold text-slate-900">{attorney.name} ({attorney.firm_name})</p>
        <p className="text-sm text-slate-600">
          상담료: {attorney.consultation_fee.toLocaleString()}원
        </p>
      </div>

      {error && (
        <div className="rounded-lg bg-red-50 border border-red-200 p-3 text-sm text-red-600">
          {error}
        </div>
      )}

      {/* 상담 유형 */}
      <div>
        <Label>상담 유형</Label>
        <div className="mt-1.5 grid grid-cols-3 gap-2">
          {(Object.entries(CASE_TYPE_LABELS) as [CaseType, string][]).map(([value, label]) => (
            <button
              key={value}
              type="button"
              className={`rounded-lg border px-3 py-2 text-sm transition-colors ${
                caseType === value
                  ? 'border-blue-500 bg-blue-50 text-blue-700'
                  : 'border-slate-200 text-slate-600 hover:border-slate-300'
              }`}
              onClick={() => setCaseType(value)}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      {/* 긴급도 */}
      <div>
        <Label>긴급도</Label>
        <div className="mt-1.5 flex gap-2">
          {(Object.entries(URGENCY_LABELS) as [Urgency, string][]).map(([value, label]) => (
            <button
              key={value}
              type="button"
              className={`flex-1 rounded-lg border px-3 py-2 text-sm transition-colors ${
                urgency === value
                  ? 'border-blue-500 bg-blue-50 text-blue-700'
                  : 'border-slate-200 text-slate-600 hover:border-slate-300'
              }`}
              onClick={() => setUrgency(value)}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      {/* 상담 방법 */}
      <div>
        <Label>상담 방법</Label>
        <div className="mt-1.5 flex gap-2">
          {(Object.entries(CONSULTATION_TYPE_LABELS) as [ConsultationType, string][]).map(
            ([value, label]) => (
              <button
                key={value}
                type="button"
                className={`flex-1 rounded-lg border px-3 py-2 text-sm transition-colors ${
                  consultationType === value
                    ? 'border-blue-500 bg-blue-50 text-blue-700'
                    : 'border-slate-200 text-slate-600 hover:border-slate-300'
                }`}
                onClick={() => setConsultationType(value)}
              >
                {label}
              </button>
            )
          )}
        </div>
      </div>

      {/* 상담 내용 */}
      <div>
        <Label>상담 내용 (선택)</Label>
        <Textarea
          className="mt-1.5"
          rows={4}
          placeholder="상담하고자 하는 내용을 간략히 작성해주세요."
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
      </div>

      {/* 버튼 */}
      <div className="flex gap-3 pt-2">
        <Button type="button" variant="outline" className="flex-1" onClick={onCancel}>
          취소
        </Button>
        <Button type="submit" className="flex-1" disabled={isSubmitting}>
          {isSubmitting ? '신청 중...' : '상담 신청'}
        </Button>
      </div>
    </form>
  );
}
