/**
 * 구독 상태 관리 스토어 (Zustand)
 */

import { create } from 'zustand';
import type {
  PlanInfo,
  Subscription,
  UsageInfo,
  PaymentHistoryItem,
} from '@/types/subscription';

interface SubscriptionState {
  plans: PlanInfo[];
  subscription: Subscription | null;
  usage: UsageInfo | null;
  payments: PaymentHistoryItem[];
  isLoading: boolean;

  // Actions
  setPlans: (plans: PlanInfo[]) => void;
  setSubscription: (subscription: Subscription | null) => void;
  setUsage: (usage: UsageInfo) => void;
  setPayments: (payments: PaymentHistoryItem[]) => void;
  setLoading: (loading: boolean) => void;
  reset: () => void;
}

export const subscriptionStore = create<SubscriptionState>()((set) => ({
  plans: [],
  subscription: null,
  usage: null,
  payments: [],
  isLoading: false,

  setPlans: (plans) => set({ plans }),
  setSubscription: (subscription) => set({ subscription }),
  setUsage: (usage) => set({ usage }),
  setPayments: (payments) => set({ payments }),
  setLoading: (loading) => set({ isLoading: loading }),
  reset: () =>
    set({
      plans: [],
      subscription: null,
      usage: null,
      payments: [],
      isLoading: false,
    }),
}));
