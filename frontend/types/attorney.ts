/**
 * 노무사 마켓플레이스 타입 정의
 */

// 케이스 유형
export type CaseType = 'dismissal' | 'wage' | 'leave' | 'industrial_accident' | 'harassment' | 'other';

// 긴급도
export type Urgency = 'low' | 'medium' | 'high' | 'emergency';

// 상담 방식
export type ConsultationType = 'video' | 'phone' | 'visit';

// 케이스 상태
export type CaseStatus = 'pending' | 'accepted' | 'in_progress' | 'completed' | 'cancelled';

// 라벨 매핑
export const CASE_TYPE_LABELS: Record<CaseType, string> = {
  dismissal: '해고/퇴직',
  wage: '임금/수당',
  leave: '휴가/휴직',
  industrial_accident: '산업재해',
  harassment: '직장 내 괴롭힘',
  other: '기타',
};

export const URGENCY_LABELS: Record<Urgency, string> = {
  low: '낮음',
  medium: '보통',
  high: '높음',
  emergency: '긴급',
};

export const CONSULTATION_TYPE_LABELS: Record<ConsultationType, string> = {
  video: '화상 상담',
  phone: '전화 상담',
  visit: '방문 상담',
};

export const CASE_STATUS_LABELS: Record<CaseStatus, string> = {
  pending: '대기중',
  accepted: '수락됨',
  in_progress: '진행중',
  completed: '완료',
  cancelled: '취소됨',
};

export const CASE_STATUS_COLORS: Record<CaseStatus, string> = {
  pending: 'bg-yellow-100 text-yellow-800',
  accepted: 'bg-blue-100 text-blue-800',
  in_progress: 'bg-indigo-100 text-indigo-800',
  completed: 'bg-green-100 text-green-800',
  cancelled: 'bg-slate-100 text-slate-500',
};

// 노무사 정보
export interface Attorney {
  id: string;
  name: string;
  firm_name: string;
  specialties: string[];
  regions: string[];
  consultation_fee: number;
  experience_years: number;
  rating: number;
  review_count: number;
  response_rate: number;
  bio: string | null;
  profile_image_url: string | null;
  verified: boolean;
}

// 노무사 상세 (리뷰 포함)
export interface AttorneyDetail {
  attorney: Attorney;
  recent_reviews: Review[];
}

// 리뷰
export interface Review {
  id: string;
  rating: number;
  comment: string | null;
  user_name: string;
  created_at: string;
}

// 케이스
export interface AttorneyCase {
  case_id: string;
  attorney_id: string;
  attorney_name: string;
  case_type: CaseType;
  urgency: Urgency;
  status: CaseStatus;
  consultation_type: string | null;
  description: string | null;
  consultation_fee: number;
  created_at: string;
}

// 상담 신청 요청
export interface CreateCaseRequest {
  attorney_id: string;
  case_type: CaseType;
  urgency: Urgency;
  consultation_type?: ConsultationType;
  description?: string;
}

// 상담 신청 결과
export interface CreateCaseResult {
  case_id: string;
  status: string;
  attorney_name: string;
  case_summary: string | null;
  consultation_fee: number;
}

// 리뷰 작성 요청
export interface CreateReviewRequest {
  rating: number;
  comment?: string;
}

// 노무사 목록 응답
export interface AttorneyListData {
  attorneys: Attorney[];
  total_count: number;
}

// 케이스 목록 응답
export interface CaseListData {
  cases: AttorneyCase[];
  total_count: number;
}

// 리뷰 목록 응답
export interface ReviewListData {
  reviews: Review[];
  total_count: number;
}
