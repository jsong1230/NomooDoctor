/**
 * 취업규칙 상태 관리 스토어 (Zustand)
 */

import { create } from 'zustand';
import type {
  WorkRule,
  WorkRuleListItem,
  WorkRuleCreate,
  WorkRuleUpdate,
  WorkRuleGenerateRequest,
  WorkRuleReviseRequest,
  ConsentChecklistResponse,
  TemplateResponse,
} from '@/types/work-rule';
import { workRuleApi } from '../api/work-rule';

interface WorkRuleState {
  // 상태
  workRules: WorkRuleListItem[];
  currentWorkRule: WorkRule | null;
  templates: TemplateResponse[];
  consentChecklist: ConsentChecklistResponse | null;
  isLoading: boolean;
  error: string | null;

  // 액션
  setWorkRules: (rules: WorkRuleListItem[]) => void;
  setCurrentWorkRule: (rule: WorkRule | null) => void;
  setTemplates: (templates: TemplateResponse[]) => void;
  setConsentChecklist: (checklist: ConsentChecklistResponse | null) => void;
  setError: (error: string | null) => void;

  // 비동기 액션
  fetchWorkRules: (params?: { status?: string; page?: number; per_page?: number }) => Promise<void>;
  fetchWorkRule: (id: string) => Promise<void>;
  fetchTemplates: (industryType?: string) => Promise<void>;
  fetchConsentChecklist: () => Promise<void>;
  createWorkRule: (data: WorkRuleCreate) => Promise<WorkRule>;
  updateWorkRule: (id: string, data: WorkRuleUpdate) => Promise<void>;
  deleteWorkRule: (id: string) => Promise<void>;
  generateAiDraft: (id: string, data: WorkRuleGenerateRequest) => Promise<void>;
  reviseWorkRule: (id: string, data: WorkRuleReviseRequest) => Promise<WorkRule>;
}

export const workRuleStore = create<WorkRuleState>((set) => ({
  // 초기 상태
  workRules: [],
  currentWorkRule: null,
  templates: [],
  consentChecklist: null,
  isLoading: false,
  error: null,

  // 상태 설정 액션
  setWorkRules: (rules) => set({ workRules: rules }),
  setCurrentWorkRule: (rule) => set({ currentWorkRule: rule }),
  setTemplates: (templates) => set({ templates }),
  setConsentChecklist: (checklist) => set({ consentChecklist: checklist }),
  setError: (error) => set({ error }),

  // 비동기 액션
  fetchWorkRules: async (params) => {
    set({ isLoading: true, error: null });
    try {
      const rules = await workRuleApi.getWorkRules(params);
      set({ workRules: rules, isLoading: false });
    } catch (error) {
      const message = error instanceof Error ? error.message : '취업규칙 목록을 불러올 수 없습니다.';
      set({ error: message, isLoading: false });
      throw error;
    }
  },

  fetchWorkRule: async (id) => {
    set({ isLoading: true, error: null });
    try {
      const rule = await workRuleApi.getWorkRule(id);
      set({ currentWorkRule: rule, isLoading: false });
    } catch (error) {
      const message = error instanceof Error ? error.message : '취업규칙을 불러올 수 없습니다.';
      set({ error: message, isLoading: false });
      throw error;
    }
  },

  fetchTemplates: async (industryType) => {
    try {
      const templates = await workRuleApi.getTemplates(industryType);
      set({ templates });
    } catch (error) {
      const message = error instanceof Error ? error.message : '템플릿을 불러올 수 없습니다.';
      set({ error: message });
      throw error;
    }
  },

  fetchConsentChecklist: async () => {
    try {
      const checklist = await workRuleApi.getConsentChecklist();
      set({ consentChecklist: checklist });
    } catch (error) {
      const message = error instanceof Error ? error.message : '체크리스트를 불러올 수 없습니다.';
      set({ error: message });
      throw error;
    }
  },

  createWorkRule: async (data) => {
    set({ isLoading: true, error: null });
    try {
      const rule = await workRuleApi.createWorkRule(data);
      set((state) => ({
        workRules: [...state.workRules, { ...rule, created_at: rule.created_at, updated_at: rule.updated_at }],
        isLoading: false,
      }));
      return rule;
    } catch (error) {
      const message = error instanceof Error ? error.message : '취업규칙을 생성할 수 없습니다.';
      set({ error: message, isLoading: false });
      throw error;
    }
  },

  updateWorkRule: async (id, data) => {
    set({ isLoading: true, error: null });
    try {
      const rule = await workRuleApi.updateWorkRule(id, data);
      set((state) => ({
        currentWorkRule: rule,
        workRules: state.workRules.map((r) => (r.id === id ? { ...rule, created_at: rule.created_at, updated_at: rule.updated_at } : r)),
        isLoading: false,
      }));
    } catch (error) {
      const message = error instanceof Error ? error.message : '취업규칙을 수정할 수 없습니다.';
      set({ error: message, isLoading: false });
      throw error;
    }
  },

  deleteWorkRule: async (id) => {
    set({ isLoading: true, error: null });
    try {
      await workRuleApi.deleteWorkRule(id);
      set((state) => ({
        workRules: state.workRules.filter((r) => r.id !== id),
        currentWorkRule: state.currentWorkRule?.id === id ? null : state.currentWorkRule,
        isLoading: false,
      }));
    } catch (error) {
      const message = error instanceof Error ? error.message : '취업규칙을 삭제할 수 없습니다.';
      set({ error: message, isLoading: false });
      throw error;
    }
  },

  generateAiDraft: async (id, data) => {
    set({ isLoading: true, error: null });
    try {
      const rule = await workRuleApi.generateAiDraft(id, data);
      set({ currentWorkRule: rule, isLoading: false });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'AI 초안을 생성할 수 없습니다.';
      set({ error: message, isLoading: false });
      throw error;
    }
  },

  reviseWorkRule: async (id, data) => {
    set({ isLoading: true, error: null });
    try {
      const rule = await workRuleApi.reviseWorkRule(id, data);
      set((state) => ({
        workRules: [...state.workRules, { ...rule, created_at: rule.created_at, updated_at: rule.updated_at }],
        isLoading: false,
      }));
      return rule;
    } catch (error) {
      const message = error instanceof Error ? error.message : '취업규칙을 개정할 수 없습니다.';
      set({ error: message, isLoading: false });
      throw error;
    }
  },
}));
