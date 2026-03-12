/**
 * 계약서 및 전자서명 관련 타입 정의
 */

export type ContractStatus = 'draft' | 'sent' | 'signed' | 'expired' | 'terminated';

export const CONTRACT_STATUS_LABELS: Record<ContractStatus, string> = {
  draft: '초안',
  sent: '서명 요청됨',
  signed: '서명 완료',
  expired: '만료',
  terminated: '해지',
};

export const CONTRACT_STATUS_COLORS: Record<ContractStatus, string> = {
  draft: 'bg-slate-100 text-slate-600',
  sent: 'bg-yellow-100 text-yellow-800',
  signed: 'bg-green-100 text-green-800',
  expired: 'bg-red-100 text-red-600',
  terminated: 'bg-slate-100 text-slate-500',
};

export interface Contract {
  id: string;
  company_id: string;
  employee_id: string;
  employee_name?: string;
  contract_type: string;
  start_date: string;
  end_date: string | null;
  status: ContractStatus;
  signed_at: string | null;
  sign_service_ref: string | null;
  created_at: string;
}

export interface SignRequestData {
  signer_name: string;
  signer_email: string;
  signer_phone?: string;
}

export interface SignRequestResult {
  contract_id: string;
  sign_service_ref: string;
  status: string;
  signing_url: string;
}

export interface SignStatusResult {
  contract_id: string;
  status: string;
  sign_service_ref: string | null;
  signed_at: string | null;
}
