'use client';
import { formatDate } from '@/lib/utils/format';
import type { ToiletHistory } from '@/types/toilet';

interface Props {
  history: ToiletHistory[];
}

const changeTypeLabel: Record<string, string> = {
  CREATE: '등록',
  UPDATE: '수정',
  DELETE: '삭제',
};

const changeTypeBadge: Record<string, string> = {
  CREATE: 'bg-green-100 text-green-700',
  UPDATE: 'bg-blue-100 text-blue-700',
  DELETE: 'bg-red-100 text-red-700',
};

const fieldLabels: Record<string, string> = {
  address: '주소', name: '이름', cleanliness: '청결도', description: '설명',
  has_password: '비밀번호 여부', is_unisex: '공용 여부', is_accessible: '장애인 가능',
  seat_count: '좌변기 수', urinal_count: '소변기 수', payment_type: '비용 유형', cost: '비용',
};

export function HistoryList({ history }: Props) {
  if (history.length === 0) {
    return <p className="text-gray-500 text-center py-8">변경 이력이 없습니다.</p>;
  }

  return (
    <div className="space-y-4">
      {history.map((item) => (
        <div key={item.id} className="border rounded-xl p-4">
          <div className="flex items-center justify-between mb-2">
            <span className={`text-xs font-medium px-2 py-1 rounded-full ${changeTypeBadge[item.change_type] || 'bg-gray-100 text-gray-700'}`}>
              {changeTypeLabel[item.change_type] || item.change_type}
            </span>
            <span className="text-xs text-gray-500">{formatDate(item.changed_at)}</span>
          </div>
          {item.changed_fields && item.changed_fields.length > 0 && (
            <div className="mt-2">
              <p className="text-xs text-gray-500 mb-1">변경된 항목:</p>
              <div className="flex flex-wrap gap-1">
                {item.changed_fields.map((field) => (
                  <span key={field} className="text-xs bg-gray-100 text-gray-700 px-2 py-0.5 rounded">
                    {fieldLabels[field] || field}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
