'use client';

import Link from 'next/link';
import { Star, MapPin, Briefcase, CheckCircle } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import type { Attorney } from '@/types/attorney';
import { CASE_TYPE_LABELS, type CaseType } from '@/types/attorney';

interface AttorneyCardProps {
  attorney: Attorney;
}

export function AttorneyCard({ attorney }: AttorneyCardProps) {
  return (
    <Link href={`/attorneys/${attorney.id}`}>
      <Card className="transition-shadow hover:shadow-md cursor-pointer">
        <CardContent className="p-5">
          <div className="flex items-start gap-4">
            {/* 프로필 이미지 */}
            <div className="h-14 w-14 shrink-0 rounded-full bg-slate-200 flex items-center justify-center text-lg font-bold text-slate-500">
              {attorney.name.charAt(0)}
            </div>

            <div className="min-w-0 flex-1">
              {/* 이름 + 인증 */}
              <div className="flex items-center gap-2">
                <h3 className="text-base font-semibold text-slate-900 truncate">
                  {attorney.name}
                </h3>
                {attorney.verified && (
                  <CheckCircle className="h-4 w-4 text-blue-500 shrink-0" />
                )}
              </div>

              {/* 사무소명 */}
              <p className="text-sm text-slate-500 truncate">{attorney.firm_name}</p>

              {/* 평점 + 경력 */}
              <div className="mt-2 flex items-center gap-3 text-sm text-slate-600">
                <span className="flex items-center gap-1">
                  <Star className="h-4 w-4 text-amber-400 fill-amber-400" />
                  {attorney.rating.toFixed(1)}
                  <span className="text-slate-400">({attorney.review_count})</span>
                </span>
                <span className="flex items-center gap-1">
                  <Briefcase className="h-3.5 w-3.5" />
                  {attorney.experience_years}년
                </span>
                <span className="flex items-center gap-1">
                  <MapPin className="h-3.5 w-3.5" />
                  {attorney.regions.slice(0, 2).join(', ')}
                </span>
              </div>

              {/* 전문분야 */}
              <div className="mt-2 flex flex-wrap gap-1">
                {attorney.specialties.map((s) => (
                  <Badge key={s} variant="secondary" className="text-xs">
                    {CASE_TYPE_LABELS[s as CaseType] || s}
                  </Badge>
                ))}
              </div>
            </div>

            {/* 상담료 */}
            <div className="text-right shrink-0">
              <p className="text-lg font-bold text-slate-900">
                {attorney.consultation_fee.toLocaleString()}원
              </p>
              <p className="text-xs text-slate-400">상담료</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}
