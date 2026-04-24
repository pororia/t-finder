'use client';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { CleanlinessRating } from './CleanlinessRating';
import { Button } from '@/components/common/Button';

const toiletSchema = z.object({
  location: z.object({ lat: z.number().min(-90).max(90), lng: z.number().min(-180).max(180) }),
  address: z.string().min(1, '주소를 입력하세요').max(500),
  address_detail: z.string().max(200).optional(),
  name: z.string().max(200).optional(),
  cleanliness: z.number().int().min(1).max(5),
  description: z.string().optional(),
  has_password: z.boolean(),
  password_value: z.string().optional(),
  is_unisex: z.boolean(),
  is_accessible: z.boolean(),
  seat_count: z.number().int().min(0),
  urinal_count: z.number().int().min(0),
  payment_type: z.enum(['FREE', 'PAID']),
  cost: z.number().int().min(0).optional(),
}).refine((d) => !d.has_password || !!d.password_value, {
  message: '비밀번호 여부 체크 시 값을 입력하세요',
  path: ['password_value'],
}).refine((d) => d.payment_type !== 'PAID' || d.cost !== undefined, {
  message: '유료인 경우 비용을 입력하세요',
  path: ['cost'],
});

type FormData = z.infer<typeof toiletSchema>;

interface Props {
  defaultValues?: Partial<FormData>;
  onSubmit: (data: FormData) => Promise<void>;
  isLoading?: boolean;
  selectedLocation?: { lat: number; lng: number };
}

export function ToiletForm({ defaultValues, onSubmit, isLoading, selectedLocation }: Props) {
  const {
    register,
    handleSubmit,
    control,
    watch,
    setValue,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(toiletSchema),
    defaultValues: {
      cleanliness: 3,
      has_password: false,
      is_unisex: false,
      is_accessible: false,
      seat_count: 0,
      urinal_count: 0,
      payment_type: 'FREE',
      location: selectedLocation || { lat: 0, lng: 0 },
      ...defaultValues,
    },
  });

  const hasPassword = watch('has_password');
  const paymentType = watch('payment_type');

  if (selectedLocation) {
    setValue('location', selectedLocation);
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
      {/* 주소 */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">주소 *</label>
        <input
          {...register('address')}
          className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#1F4E79]"
          placeholder="도로명 주소를 입력하세요"
        />
        {errors.address && <p className="mt-1 text-xs text-red-500">{errors.address.message}</p>}
      </div>

      {/* 이름(선택) */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">화장실 이름 (선택)</label>
        <input
          {...register('name')}
          className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#1F4E79]"
          placeholder="예: 강남역 2번 출구 공중화장실"
        />
      </div>

      {/* 청결도 */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">청결도 *</label>
        <Controller
          name="cleanliness"
          control={control}
          render={({ field }) => (
            <CleanlinessRating value={field.value} onChange={field.onChange} size="lg" />
          )}
        />
        {errors.cleanliness && <p className="mt-1 text-xs text-red-500">{errors.cleanliness.message}</p>}
      </div>

      {/* 시설 정보 */}
      <div className="grid grid-cols-2 gap-4">
        <div className="flex items-center gap-2">
          <input type="checkbox" id="is_unisex" {...register('is_unisex')} className="w-4 h-4 rounded" />
          <label htmlFor="is_unisex" className="text-sm font-medium text-gray-700">남녀 공용</label>
        </div>
        <div className="flex items-center gap-2">
          <input type="checkbox" id="is_accessible" {...register('is_accessible')} className="w-4 h-4 rounded" />
          <label htmlFor="is_accessible" className="text-sm font-medium text-gray-700">장애인 가능</label>
        </div>
      </div>

      {/* 좌변기/소변기 */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">좌변기 수</label>
          <input
            type="number"
            min={0}
            {...register('seat_count', { valueAsNumber: true })}
            className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#1F4E79]"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">소변기 수</label>
          <input
            type="number"
            min={0}
            {...register('urinal_count', { valueAsNumber: true })}
            className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#1F4E79]"
          />
        </div>
      </div>

      {/* 비용 */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">비용</label>
        <div className="flex gap-4">
          <label className="flex items-center gap-2">
            <input type="radio" value="FREE" {...register('payment_type')} className="w-4 h-4" />
            <span className="text-sm">무료</span>
          </label>
          <label className="flex items-center gap-2">
            <input type="radio" value="PAID" {...register('payment_type')} className="w-4 h-4" />
            <span className="text-sm">유료</span>
          </label>
        </div>
        {paymentType === 'PAID' && (
          <div className="mt-2">
            <input
              type="number"
              min={0}
              {...register('cost', { valueAsNumber: true })}
              placeholder="금액 (원)"
              className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#1F4E79]"
            />
            {errors.cost && <p className="mt-1 text-xs text-red-500">{errors.cost.message}</p>}
          </div>
        )}
      </div>

      {/* 비밀번호 */}
      <div>
        <div className="flex items-center gap-2 mb-2">
          <input type="checkbox" id="has_password" {...register('has_password')} className="w-4 h-4 rounded" />
          <label htmlFor="has_password" className="text-sm font-medium text-gray-700">비밀번호 있음</label>
        </div>
        {hasPassword && (
          <div>
            <input
              {...register('password_value')}
              placeholder="비밀번호 입력"
              className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#1F4E79]"
            />
            {errors.password_value && <p className="mt-1 text-xs text-red-500">{errors.password_value.message}</p>}
          </div>
        )}
      </div>

      {/* 설명 */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">설명 (선택)</label>
        <textarea
          {...register('description')}
          rows={3}
          className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#1F4E79] resize-none"
          placeholder="화장실에 대한 설명을 입력하세요"
        />
      </div>

      <Button type="submit" loading={isLoading} fullWidth size="lg">
        등록하기
      </Button>
    </form>
  );
}
