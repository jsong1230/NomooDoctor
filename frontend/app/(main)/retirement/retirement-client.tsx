'use client';

/**
 * 퇴직금 계산기 클라이언트 컴포넌트
 */

import { useEffect, useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { SeveranceCalculator } from '@/components/retirement/severance-calculator';
import { TerminationGuideForm } from '@/components/retirement/termination-guide-form';
import { listSeverances } from '@/lib/api/retirement';
import { retirementStore } from '@/lib/stores/retirement-store';
import type { SeveranceSummary } from '@/types/retirement';

interface Employee {
  id: string;
  name: string;
}

export function RetirementClient() {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [records, setRecords] = useState<SeveranceSummary[]>([]);
  const [isLoadingRecords, setIsLoadingRecords] = useState(false);

  const { setRecords: setStoreRecords } = retirementStore();

  // 직원 목록 로드 (Mock 데이터)
  useEffect(() => {
    // TODO: API에서 실제 직원 목록 로드
    setEmployees([
      { id: '1', name: '홍길동' },
      { id: '2', name: '김영희' },
      { id: '3', name: '이순신' },
    ]);
  }, []);

  // 퇴직금 기록 로드
  const loadRecords = async () => {
    setIsLoadingRecords(true);
    try {
      const result = await listSeverances({ limit: 50, offset: 0 });
      setRecords(result.data);
      setStoreRecords(result.data);
    } catch (error) {
      console.error('Failed to load records:', error);
    } finally {
      setIsLoadingRecords(false);
    }
  };

  useEffect(() => {
    loadRecords();
  }, [setStoreRecords]);

  const handleCalculated = () => {
    loadRecords();
  };

  const handleGenerated = () => {
    // 절차 가이드 생성 후 필요시 처리
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const formatCurrency = (amount: number) => {
    return amount.toLocaleString('ko-KR');
  };

  return (
    <div className="w-full max-w-6xl mx-auto">
      {/* 헤더 */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">퇴직금 계산기</h1>
        <p className="text-gray-600">직원의 퇴직금과 해고 절차를 안내합니다.</p>
      </div>

      {/* 탭 */}
      <Tabs defaultValue="calculator" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="calculator">퇴직금 계산</TabsTrigger>
          <TabsTrigger value="termination">해고 절차</TabsTrigger>
          <TabsTrigger value="history">계산 기록</TabsTrigger>
        </TabsList>

        {/* 퇴직금 계산 탭 */}
        <TabsContent value="calculator" className="mt-6">
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <SeveranceCalculator
              employees={employees}
              onCalculated={handleCalculated}
            />
          </div>
        </TabsContent>

        {/* 해고 절차 탭 */}
        <TabsContent value="termination" className="mt-6">
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <TerminationGuideForm
              employees={employees}
              onGenerated={handleGenerated}
            />
          </div>
        </TabsContent>

        {/* 계산 기록 탭 */}
        <TabsContent value="history" className="mt-6">
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">계산 기록</h2>

            {isLoadingRecords ? (
              <div className="text-center py-12">
                <p className="text-gray-500">로드 중...</p>
              </div>
            ) : records.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-gray-500">계산된 기록이 없습니다.</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-200">
                      <th className="text-left py-3 px-4 font-medium text-gray-700">
                        직원명
                      </th>
                      <th className="text-left py-3 px-4 font-medium text-gray-700">
                        퇴직예정일
                      </th>
                      <th className="text-right py-3 px-4 font-medium text-gray-700">
                        총 지급액
                      </th>
                      <th className="text-left py-3 px-4 font-medium text-gray-700">
                        지급 기한
                      </th>
                      <th className="text-left py-3 px-4 font-medium text-gray-700">
                        상태
                      </th>
                      <th className="text-left py-3 px-4 font-medium text-gray-700">
                        생성일
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {records.map(record => (
                      <tr
                        key={record.id}
                        className="border-b border-gray-200 hover:bg-gray-50 transition"
                      >
                        <td className="py-3 px-4 text-gray-900 font-medium">
                          {record.employee_name}
                        </td>
                        <td className="py-3 px-4 text-gray-600">
                          {formatDate(record.resign_date)}
                        </td>
                        <td className="py-3 px-4 text-gray-900 font-medium text-right">
                          {formatCurrency(record.total_payment)}원
                        </td>
                        <td className="py-3 px-4 text-gray-600">
                          {formatDate(record.payment_deadline)}
                        </td>
                        <td className="py-3 px-4">
                          <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                            record.status === 'paid'
                              ? 'bg-green-100 text-green-800'
                              : record.status === 'calculated'
                              ? 'bg-blue-100 text-blue-800'
                              : 'bg-red-100 text-red-800'
                          }`}>
                            {record.status === 'paid'
                              ? '지급완료'
                              : record.status === 'calculated'
                              ? '계산완료'
                              : '기한초과'}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-gray-600">
                          {formatDate(record.created_at)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
