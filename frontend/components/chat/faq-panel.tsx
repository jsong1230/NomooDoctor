'use client';

/**
 * FAQ 빠른 질문 패널
 */

import type { FAQItem } from '@/types/chat';
import {
  Banknote,
  Clock,
  Calendar,
  UserX,
  FileText,
  Shield,
  HeartPulse,
  HelpCircle,
} from 'lucide-react';

interface FAQPanelProps {
  items: FAQItem[];
  onSelect: (question: string) => void;
}

const CATEGORY_ICONS: Record<string, typeof Banknote> = {
  '임금': Banknote,
  '근로시간': Clock,
  '휴가': Calendar,
  '해고': UserX,
  '계약': FileText,
  '4대보험': Shield,
  '산재': HeartPulse,
};

export function FAQPanel({ items, onSelect }: FAQPanelProps) {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3 p-4">
      {items.map((item) => {
        const Icon = CATEGORY_ICONS[item.category] || HelpCircle;
        return (
          <button
            key={item.category}
            type="button"
            onClick={() => onSelect(item.question)}
            className="
              flex flex-col items-center gap-2 p-4
              bg-white border border-slate-200 rounded-xl
              hover:border-primary-300 hover:bg-primary-50
              transition-all text-center group
            "
          >
            <div className="p-2 bg-slate-100 rounded-lg group-hover:bg-primary-100 transition-colors">
              <Icon className="w-5 h-5 text-slate-600 group-hover:text-primary-600" />
            </div>
            <span className="text-xs font-medium text-slate-700 group-hover:text-primary-700">
              {item.category}
            </span>
            <p className="text-[10px] text-slate-400 line-clamp-2">
              {item.description}
            </p>
          </button>
        );
      })}
    </div>
  );
}
