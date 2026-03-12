'use client';

/**
 * 엑셀 업로드 컴포넌트
 * 드래그앤드롭 + 파일 선택 + 결과 표시
 */

import { useState } from 'react';
import { Upload, Download, AlertCircle, CheckCircle, X, Loader2 } from 'lucide-react';
import { attendanceApi } from '@/lib/api/attendance';
import { attendanceStore } from '@/lib/stores/attendance-store';
import type { ImportResult, ImportError } from '@/types/attendance';

interface ExcelUploadProps {
  onSuccess?: () => void;
}

export function ExcelUpload({ onSuccess }: ExcelUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [uploadResult, setUploadResult] = useState<ImportResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleUploadFile = async (file: File) => {
    // 파일 형식 확인
    if (!['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'text/csv'].includes(
      file.type
    )) {
      setError('Excel(xlsx) 또는 CSV 파일만 업로드 가능합니다.');
      return;
    }

    // 파일 크기 확인 (10MB)
    if (file.size > 10 * 1024 * 1024) {
      setError('파일 크기는 10MB 이하여야 합니다.');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const result = await attendanceApi.importWorkRecords(file);
      setUploadResult(result);
      attendanceStore.getState().setImportResult(result);
      onSuccess?.();
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || '업로드에 실패했습니다';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      handleUploadFile(files[0]);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.currentTarget.files;
    if (files && files.length > 0) {
      handleUploadFile(files[0]);
    }
    // input 리셋
    e.currentTarget.value = '';
  };

  const downloadTemplate = async () => {
    try {
      const blob = await attendanceApi.downloadTemplate();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = '근무기록_템플릿.xlsx';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err: any) {
      setError('템플릿 다운로드에 실패했습니다');
    }
  };

  if (uploadResult && !error) {
    return (
      <div className="space-y-4">
        {/* 결과 요약 */}
        <div className="p-4 bg-slate-50 rounded-lg border border-slate-200">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div>
              <div className="text-sm text-slate-600">전체 행</div>
              <div className="text-2xl font-bold text-slate-900">
                {uploadResult.total_rows}
              </div>
            </div>
            <div>
              <div className="text-sm text-slate-600">생성됨</div>
              <div className="text-2xl font-bold text-green-600">
                {uploadResult.created}
              </div>
            </div>
            <div>
              <div className="text-sm text-slate-600">수정됨</div>
              <div className="text-2xl font-bold text-blue-600">
                {uploadResult.updated}
              </div>
            </div>
            <div>
              <div className="text-sm text-slate-600">스킵됨</div>
              <div className="text-2xl font-bold text-warning-600">
                {uploadResult.skipped}
              </div>
            </div>
          </div>
        </div>

        {/* 에러 목록 */}
        {uploadResult.errors.length > 0 && (
          <div className="p-4 bg-error-50 border border-error-200 rounded-lg">
            <div className="flex items-center gap-2 mb-3">
              <AlertCircle className="w-5 h-5 text-error-600" />
              <h3 className="font-semibold text-error-900">
                오류 발생 ({uploadResult.errors.length}건)
              </h3>
            </div>
            <div className="max-h-40 overflow-y-auto space-y-2">
              {uploadResult.errors.map((err, idx) => (
                <div key={idx} className="text-sm text-error-800 border-b border-error-200 pb-2 last:border-0">
                  <div className="font-medium">행 {err.row}</div>
                  {err.column && <div className="text-xs text-error-700">컬럼: {err.column}</div>}
                  <div className="text-xs text-error-700">{err.reason}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 초기화 버튼 */}
        <button
          type="button"
          onClick={() => setUploadResult(null)}
          className="w-full py-2 px-4 bg-slate-200 hover:bg-slate-300 text-slate-900 font-medium rounded-lg transition-colors"
        >
          다시 업로드
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* 에러 메시지 */}
      {error && (
        <div className="p-3 bg-error-50 border border-error-200 rounded-lg text-error-700 text-sm flex items-start gap-2">
          <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      {/* 드래그앤드롭 영역 */}
      <div
        onDragEnter={handleDragEnter}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`
          p-8 border-2 border-dashed rounded-lg text-center
          transition-colors duration-200 cursor-pointer
          ${
            isDragging
              ? 'border-primary-500 bg-primary-50'
              : 'border-slate-300 bg-slate-50 hover:bg-slate-100'
          }
        `}
      >
        <input
          type="file"
          id="file-input"
          onChange={handleFileSelect}
          accept=".xlsx,.csv"
          disabled={isLoading}
          className="hidden"
        />

        <label htmlFor="file-input" className="block cursor-pointer">
          <div className="flex flex-col items-center gap-2">
            {isLoading ? (
              <Loader2 className="w-8 h-8 text-primary-600 animate-spin" />
            ) : (
              <Upload className="w-8 h-8 text-slate-400" />
            )}
            <div>
              <p className="font-semibold text-slate-900">
                {isLoading ? '업로드 중...' : '파일을 드래그하거나 클릭하세요'}
              </p>
              <p className="text-sm text-slate-600">Excel(xlsx) 또는 CSV</p>
            </div>
          </div>
        </label>
      </div>

      {/* 템플릿 다운로드 */}
      <button
        type="button"
        onClick={downloadTemplate}
        className="w-full flex items-center justify-center gap-2 py-2 px-4 border border-slate-300 hover:bg-slate-50 text-slate-700 font-medium rounded-lg transition-colors"
      >
        <Download className="w-4 h-4" />
        템플릿 다운로드
      </button>
    </div>
  );
}
