import { format, formatDistanceToNow } from 'date-fns';
import { ko } from 'date-fns/locale';

export function formatDate(dateString: string): string {
  return format(new Date(dateString), 'yyyy년 MM월 dd일', { locale: ko });
}

export function formatRelativeDate(dateString: string): string {
  return formatDistanceToNow(new Date(dateString), { addSuffix: true, locale: ko });
}

export function formatCost(cost: number | null | undefined): string {
  if (cost == null || cost === 0) return '무료';
  return `${cost.toLocaleString()}원`;
}

export function formatPaymentType(type: 'FREE' | 'PAID', cost: number | null): string {
  return type === 'FREE' ? '무료' : formatCost(cost);
}
