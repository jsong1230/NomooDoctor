'use client';

/**
 * 해고 절차 가이드 클라이언트 컴포넌트
 */

import { useEffect, useState } from 'react';
import { TerminationGuideForm } from '@/components/retirement/termination-guide-form';

interface Employee {
  id: string;
  name: string;
}

export function TerminationClient() {
  const [employees, setEmployees] = useState<Employee[]>([]);

  // 직원 목록 로드 (Mock 데이터)
  useEffect(() => {
    // TODO: API에서 실제 직원 목록 로드
    setEmployees([
      { id: '1', name: '홍길동' },
      { id: '2', name: '김영희' },
      { id: '3', name: '이순신' },
    ]);
  }, []);

  const handleGenerated = () => {
    // 절차 가이드 생성 후 필요시 처리
  };

  return (
    <div className="w-full max-w-4xl mx-auto">
      {/* 헤더 */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">해고 절차 가이드</h1>
        <p className="text-gray-600">
          직원 해고/퇴직 절차를 법적으로 안전하게 진행하세요. AI 기반 전문 가이드가 제공됩니다.
        </p>
      </div>

      {/* 가이드 폼 */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <TerminationGuideForm
          employees={employees}
          onGenerated={handleGenerated}
        />
      </div>

      {/* 정보 */}
      <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="font-semibold text-blue-900 mb-3">안내</h3>
        <ul className="space-y-2 text-sm text-blue-800">
          <li className="flex gap-2">
            <span>•</span>
            <span>본 가이드는 참고용이며, 구체적인 사안에 대해서는 반드시 전문 노무사와 상담하세요.</span>
          </li>
          <li className="flex gap-2">
            <span>•</span>
            <span>위험 요소가 감지된 경우 즉시 노무사 상담을 강력히 권장합니다.</span>
          </li>
          <li className="flex gap-2">
            <span>•</span>
            <span>모든 절차는 근로기준법 등 관련 법규를 준수해야 합니다.</span>
          </li>
        </ul>
      </div>
    </div>
  );
}
