'use client';

import { useEffect, useState } from 'react';
import { Search } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { AttorneyCard } from './attorney-card';
import { attorneyApi } from '@/lib/api/attorney';
import { attorneyStore } from '@/lib/stores/attorney-store';
import { CASE_TYPE_LABELS, type CaseType } from '@/types/attorney';

const SPECIALTIES: CaseType[] = ['dismissal', 'wage', 'leave', 'industrial_accident', 'harassment', 'other'];
const SORT_OPTIONS = [
  { value: 'rating', label: '평점순' },
  { value: 'experience', label: '경력순' },
  { value: 'fee', label: '상담료순' },
];

export function AttorneyList() {
  const { attorneys, totalCount, isLoading, setAttorneys, setLoading, setError } = attorneyStore();
  const [selectedSpecialty, setSelectedSpecialty] = useState<string | null>(null);
  const [sort, setSort] = useState('rating');

  const fetchAttorneys = async (specialty?: string, sortBy?: string) => {
    setLoading(true);
    try {
      const data = await attorneyApi.listAttorneys({
        specialty: specialty || undefined,
        sort: sortBy || sort,
        limit: 20,
      });
      setAttorneys(data.attorneys, data.total_count);
    } catch {
      setError('노무사 목록을 불러올 수 없습니다.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAttorneys(selectedSpecialty || undefined, sort);
  }, [selectedSpecialty, sort]);

  const handleSpecialtyClick = (s: string) => {
    setSelectedSpecialty(selectedSpecialty === s ? null : s);
  };

  return (
    <div>
      {/* 필터 바 */}
      <div className="mb-6 space-y-3">
        {/* 전문분야 필터 */}
        <div className="flex flex-wrap gap-2">
          <Badge
            variant={selectedSpecialty === null ? 'default' : 'outline'}
            className="cursor-pointer"
            onClick={() => setSelectedSpecialty(null)}
          >
            전체
          </Badge>
          {SPECIALTIES.map((s) => (
            <Badge
              key={s}
              variant={selectedSpecialty === s ? 'default' : 'outline'}
              className="cursor-pointer"
              onClick={() => handleSpecialtyClick(s)}
            >
              {CASE_TYPE_LABELS[s]}
            </Badge>
          ))}
        </div>

        {/* 정렬 */}
        <div className="flex items-center justify-between">
          <p className="text-sm text-slate-500">
            총 <span className="font-medium text-slate-700">{totalCount}</span>명의 노무사
          </p>
          <div className="flex gap-2">
            {SORT_OPTIONS.map((opt) => (
              <Button
                key={opt.value}
                variant={sort === opt.value ? 'default' : 'ghost'}
                size="sm"
                onClick={() => setSort(opt.value)}
              >
                {opt.label}
              </Button>
            ))}
          </div>
        </div>
      </div>

      {/* 로딩 */}
      {isLoading && (
        <div className="flex h-40 items-center justify-center">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent" />
        </div>
      )}

      {/* 결과 없음 */}
      {!isLoading && attorneys.length === 0 && (
        <div className="rounded-xl border border-slate-200 bg-white p-12 text-center">
          <Search className="mx-auto h-12 w-12 text-slate-300" />
          <p className="mt-4 text-slate-500">조건에 맞는 노무사가 없습니다.</p>
        </div>
      )}

      {/* 노무사 목록 */}
      {!isLoading && attorneys.length > 0 && (
        <div className="space-y-3">
          {attorneys.map((attorney) => (
            <AttorneyCard key={attorney.id} attorney={attorney} />
          ))}
        </div>
      )}
    </div>
  );
}
