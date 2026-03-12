'use client';

import { useEffect, useState } from 'react';
import { FileText, Clock, X } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { attorneyApi } from '@/lib/api/attorney';
import {
  CASE_TYPE_LABELS,
  CASE_STATUS_LABELS,
  CASE_STATUS_COLORS,
  type AttorneyCase,
  type CaseType,
  type CaseStatus,
} from '@/types/attorney';

interface MyCasesProps {
  onReview: (caseItem: AttorneyCase) => void;
}

export function MyCases({ onReview }: MyCasesProps) {
  const [cases, setCases] = useState<AttorneyCase[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);

  const fetchCases = async () => {
    setIsLoading(true);
    try {
      const data = await attorneyApi.listMyCases({ limit: 20 });
      setCases(data.cases);
      setTotal(data.total_count);
    } catch {
      // silent
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchCases();
  }, []);

  const handleCancel = async (caseId: string) => {
    try {
      await attorneyApi.cancelCase(caseId);
      fetchCases();
    } catch {
      // silent
    }
  };

  if (isLoading) {
    return (
      <div className="flex h-40 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent" />
      </div>
    );
  }

  if (cases.length === 0) {
    return (
      <div className="rounded-xl border border-slate-200 bg-white p-12 text-center">
        <FileText className="mx-auto h-12 w-12 text-slate-300" />
        <p className="mt-4 text-slate-500">상담 신청 내역이 없습니다.</p>
        <p className="text-sm text-slate-400">노무사를 선택하여 상담을 신청해보세요.</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <p className="text-sm text-slate-500">
        총 <span className="font-medium text-slate-700">{total}</span>건
      </p>
      {cases.map((item) => (
        <Card key={item.case_id}>
          <CardContent className="p-4">
            <div className="flex items-start justify-between">
              <div>
                <div className="flex items-center gap-2">
                  <Badge className={CASE_STATUS_COLORS[item.status as CaseStatus]}>
                    {CASE_STATUS_LABELS[item.status as CaseStatus] || item.status}
                  </Badge>
                  <Badge variant="secondary">
                    {CASE_TYPE_LABELS[item.case_type as CaseType] || item.case_type}
                  </Badge>
                </div>
                <p className="mt-2 font-medium text-slate-900">{item.attorney_name} 노무사</p>
                {item.description && (
                  <p className="mt-1 text-sm text-slate-500 line-clamp-2">{item.description}</p>
                )}
                <div className="mt-2 flex items-center gap-3 text-xs text-slate-400">
                  <span className="flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {new Date(item.created_at).toLocaleDateString('ko-KR')}
                  </span>
                  <span>{item.consultation_fee.toLocaleString()}원</span>
                </div>
              </div>

              <div className="flex gap-2">
                {item.status === 'pending' && (
                  <Button
                    variant="ghost"
                    size="sm"
                    className="text-red-500 hover:text-red-600"
                    onClick={() => handleCancel(item.case_id)}
                  >
                    <X className="h-4 w-4 mr-1" />
                    취소
                  </Button>
                )}
                {(item.status === 'completed' || item.status === 'in_progress') && (
                  <Button variant="outline" size="sm" onClick={() => onReview(item)}>
                    리뷰 작성
                  </Button>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
