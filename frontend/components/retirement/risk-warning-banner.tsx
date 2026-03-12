'use client';

/**
 * 위험 경고 배너 컴포넌트
 * 높은 위험도의 경우 배너 표시
 */

import { AlertTriangle, AlertCircle, Info } from 'lucide-react';
import type { RiskWarning } from '@/types/retirement';
import { WARNING_SEVERITY_COLOR_MAP } from '@/types/retirement';

interface RiskWarningBannerProps {
  warnings: RiskWarning[];
  riskLevel?: string;
}

export function RiskWarningBanner({
  warnings,
  riskLevel = 'MEDIUM'
}: RiskWarningBannerProps) {
  if (warnings.length === 0) {
    return null;
  }

  const getIcon = (severity: string) => {
    switch (severity) {
      case 'EMERGENCY':
        return <AlertTriangle className="w-5 h-5" />;
      case 'HIGH':
        return <AlertCircle className="w-5 h-5" />;
      default:
        return <Info className="w-5 h-5" />;
    }
  };

  return (
    <div className="space-y-3">
      {warnings.map((warning, index) => (
        <div
          key={index}
          className={`border-l-4 rounded-lg p-4 flex gap-3 ${
            WARNING_SEVERITY_COLOR_MAP[warning.severity] ||
            'bg-yellow-50 border-yellow-200 text-yellow-800'
          }`}
        >
          <div className="flex-shrink-0 pt-0.5">
            {getIcon(warning.severity)}
          </div>
          <div className="flex-1">
            <h4 className="font-semibold mb-1">{warning.type}</h4>
            <p className="text-sm mb-2">{warning.message}</p>
            <p className="text-sm font-medium">
              조치: {warning.recommendation}
            </p>
          </div>
        </div>
      ))}
    </div>
  );
}
