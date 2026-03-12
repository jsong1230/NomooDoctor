'use client';

import { useState } from 'react';
import { Send, CheckCircle, ExternalLink } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { contractApi } from '@/lib/api/contract';
import type { SignRequestResult } from '@/types/contract';

interface SignRequestFormProps {
  contractId: string;
  contractStatus: string;
  onSuccess?: () => void;
}

export function SignRequestForm({ contractId, contractStatus, onSuccess }: SignRequestFormProps) {
  const [signerName, setSignerName] = useState('');
  const [signerEmail, setSignerEmail] = useState('');
  const [signerPhone, setSignerPhone] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [result, setResult] = useState<SignRequestResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const canSign = contractStatus === 'draft';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!signerName || !signerEmail) return;

    setIsSubmitting(true);
    setError(null);
    try {
      const res = await contractApi.sendSignRequest(contractId, {
        signer_name: signerName,
        signer_email: signerEmail,
        signer_phone: signerPhone || undefined,
      });
      setResult(res);
      onSuccess?.();
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { error?: { message?: string } } } };
      setError(axiosErr.response?.data?.error?.message || '전자서명 요청에 실패했습니다.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (result) {
    return (
      <Card className="border-green-200 bg-green-50">
        <CardContent className="p-6 text-center">
          <CheckCircle className="mx-auto h-12 w-12 text-green-500 mb-3" />
          <h3 className="font-semibold text-green-800 mb-1">전자서명 요청 완료</h3>
          <p className="text-sm text-green-600 mb-4">
            서명 요청이 발송되었습니다. 서명자가 이메일을 확인하면 서명을 진행합니다.
          </p>
          <a
            href={result.signing_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 text-sm text-blue-600 hover:underline"
          >
            서명 페이지 열기
            <ExternalLink className="h-3.5 w-3.5" />
          </a>
        </CardContent>
      </Card>
    );
  }

  if (!canSign) {
    return null;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base">
          <Send className="h-4 w-4" />
          전자서명 요청
        </CardTitle>
      </CardHeader>
      <CardContent>
        {error && (
          <div className="mb-4 rounded-lg bg-red-50 border border-red-200 p-3 text-sm text-red-600">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label>서명자 이름</Label>
            <Input
              className="mt-1"
              placeholder="홍길동"
              value={signerName}
              onChange={(e) => setSignerName(e.target.value)}
              required
            />
          </div>
          <div>
            <Label>서명자 이메일</Label>
            <Input
              className="mt-1"
              type="email"
              placeholder="hong@example.com"
              value={signerEmail}
              onChange={(e) => setSignerEmail(e.target.value)}
              required
            />
          </div>
          <div>
            <Label>서명자 전화번호 (선택)</Label>
            <Input
              className="mt-1"
              placeholder="01012345678"
              value={signerPhone}
              onChange={(e) => setSignerPhone(e.target.value)}
            />
          </div>
          <Button type="submit" className="w-full" disabled={isSubmitting}>
            {isSubmitting ? '요청 중...' : '전자서명 요청 발송'}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
