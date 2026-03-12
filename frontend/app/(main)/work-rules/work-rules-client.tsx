'use client';

/**
 * 취업규칙 관리 페이지 - Client 컴포넌트
 */

import { WorkRuleList } from '@/components/work-rule/work-rule-list';
import { useEffect, useState } from 'react';
import { authStore } from '@/lib/stores/auth-store';
import { useRouter } from 'next/navigation';

export function WorkRuleListClient() {
  const router = useRouter();
  const { user } = authStore();
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    // company_id가 없으면 사업장 선택 페이지로 리다이렉트
    if (!user?.company_id) {
      router.push('/company');
    } else {
      setIsReady(true);
    }
  }, [user?.company_id, router]);

  if (!isReady) {
    return <div className="flex items-center justify-center py-12">로드 중...</div>;
  }

  return (
    <div className="min-h-screen bg-slate-50 px-4 py-8 sm:px-6 sm:py-12">
      <div className="mx-auto max-w-4xl">
        <WorkRuleList companyId={user!.company_id!} />
      </div>
    </div>
  );
}
