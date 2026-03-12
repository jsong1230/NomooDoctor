'use client';

import { useState } from 'react';
import { Star } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { attorneyApi } from '@/lib/api/attorney';

interface ReviewFormProps {
  caseId: string;
  attorneyName: string;
  onSuccess: () => void;
  onCancel: () => void;
}

export function ReviewForm({ caseId, attorneyName, onSuccess, onCancel }: ReviewFormProps) {
  const [rating, setRating] = useState(5);
  const [hoverRating, setHoverRating] = useState(0);
  const [comment, setComment] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);
    try {
      await attorneyApi.createReview(caseId, {
        rating,
        comment: comment || undefined,
      });
      onSuccess();
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { error?: { message?: string } } } };
      setError(axiosErr.response?.data?.error?.message || '리뷰 작성에 실패했습니다.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      <div className="rounded-lg bg-slate-50 p-4">
        <p className="text-sm text-slate-500">리뷰 대상</p>
        <p className="font-semibold text-slate-900">{attorneyName} 노무사</p>
      </div>

      {error && (
        <div className="rounded-lg bg-red-50 border border-red-200 p-3 text-sm text-red-600">
          {error}
        </div>
      )}

      {/* 별점 */}
      <div>
        <Label>평점</Label>
        <div className="mt-1.5 flex gap-1">
          {[1, 2, 3, 4, 5].map((i) => (
            <button
              key={i}
              type="button"
              onMouseEnter={() => setHoverRating(i)}
              onMouseLeave={() => setHoverRating(0)}
              onClick={() => setRating(i)}
            >
              <Star
                className={`h-8 w-8 transition-colors ${
                  i <= (hoverRating || rating)
                    ? 'text-amber-400 fill-amber-400'
                    : 'text-slate-200'
                }`}
              />
            </button>
          ))}
          <span className="ml-2 self-center text-sm text-slate-500">{rating}점</span>
        </div>
      </div>

      {/* 코멘트 */}
      <div>
        <Label>후기 (선택)</Label>
        <Textarea
          className="mt-1.5"
          rows={4}
          placeholder="상담 경험을 공유해주세요."
          value={comment}
          onChange={(e) => setComment(e.target.value)}
        />
      </div>

      {/* 버튼 */}
      <div className="flex gap-3 pt-2">
        <Button type="button" variant="outline" className="flex-1" onClick={onCancel}>
          취소
        </Button>
        <Button type="submit" className="flex-1" disabled={isSubmitting}>
          {isSubmitting ? '등록 중...' : '리뷰 등록'}
        </Button>
      </div>
    </form>
  );
}
