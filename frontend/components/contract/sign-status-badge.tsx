'use client';

import { useEffect, useState } from 'react';
import { Download, RefreshCw } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { contractApi } from '@/lib/api/contract';
import {
  CONTRACT_STATUS_LABELS,
  CONTRACT_STATUS_COLORS,
  type ContractStatus,
  type SignStatusResult,
} from '@/types/contract';

interface SignStatusBadgeProps {
  contractId: string;
  initialStatus: ContractStatus;
  signServiceRef: string | null;
}

export function SignStatusBadge({ contractId, initialStatus, signServiceRef }: SignStatusBadgeProps) {
  const [status, setStatus] = useState<ContractStatus>(initialStatus);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleRefresh = async () => {
    if (!signServiceRef) return;
    setIsRefreshing(true);
    try {
      const result = await contractApi.getSignStatus(contractId);
      setStatus(result.status as ContractStatus);
    } catch {
      // silent
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleDownload = async () => {
    try {
      const blob = await contractApi.downloadSignedPdf(contractId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `contract_${contractId}_signed.pdf`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch {
      // silent
    }
  };

  return (
    <div className="flex items-center gap-2">
      <Badge className={CONTRACT_STATUS_COLORS[status]}>
        {CONTRACT_STATUS_LABELS[status]}
      </Badge>

      {status === 'sent' && (
        <Button
          variant="ghost"
          size="sm"
          onClick={handleRefresh}
          disabled={isRefreshing}
        >
          <RefreshCw className={`h-3.5 w-3.5 ${isRefreshing ? 'animate-spin' : ''}`} />
        </Button>
      )}

      {status === 'signed' && (
        <Button variant="ghost" size="sm" onClick={handleDownload}>
          <Download className="h-3.5 w-3.5 mr-1" />
          PDF
        </Button>
      )}
    </div>
  );
}
