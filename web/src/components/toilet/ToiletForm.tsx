'use client';
import { useEffect } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { CleanlinessRating } from './CleanlinessRating';
import { Button } from '@/components/common/Button';

const toiletSchema = z.object({
  toilet_type: z.enum(['간이', '개방', '공중', '이동']).optional(),
  location: z.object({ lat: z.number().min(-90).max(90), lng: z.number().min(-180).max(180) }),
  address: z.string().min(1, '주소를 입력하세요').max(500),
  address_jibun: z.string().max(500).optional(),
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
  male_seat_count: z.number().int().min(0),
  male_urinal_count: z.number().int().min(0),
  male_disabled_seat_count: z.number().int().min(0),
  male_disabled_urinal_count: z.number().int().min(0),
  male_children_seat_count: z.number().int().min(0),
  male_children_urinal_count: z.number().int().min(0),
  female_seat_count: z.number().int().min(0),
  female_disabled_seat_count: z.number().int().min(0),
  female_children_seat_count: z.number().int().min(0),
  open_hours: z.string().max(200).optional(),
  has_emergency_bell: z.boolean(),
  emergency_bell_location: z.string().max(200).optional(),
  has_entrance_cctv: z.boolean(),
  has_diaper_table: z.boolean(),
  diaper_table_location: z.string().max(200).optional(),
  remodeling_date: z.string().regex(/^\d{4}-(0[1-9]|1[0-2])$/, 'YYYY-MM 형식으로 입력하세요').optional().or(z.literal('')),
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
  autoAddress?: string;
}

export function ToiletForm({ defaultValues, onSubmit, isLoading, selectedLocation, autoAddress }: Props) {
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
      male_seat_count: 0,
      male_urinal_count: 0,
      male_disabled_seat_count: 0,
      male_disabled_urinal_count: 0,
      male_children_seat_count: 0,
      male_children_urinal_count: 0,
      female_seat_count: 0,
      female_disabled_seat_count: 0,
      female_children_seat_count: 0,
      has_emergency_bell: false,
      has_entrance_cctv: false,
      has_diaper_table: false,
      payment_type: 'FREE',
      location: selectedLocation || { lat: 0, lng: 0 },
      ...defaultValues,
    },
  });

  const hasPassword = watch('has_password');
  const paymentType = watch('payment_type');
  const isUnisex = watch('is_unisex');
  const hasEmergencyBell = watch('has_emergency_bell');
  const hasDiaperTable = watch('has_diaper_table');

  if (selectedLocation) {
    setValue('location', selectedLocation);
  }

  useEffect(() => {
    if (autoAddress) setValue('address', autoAddress);
  }, [autoAddress, setValue]);

  const inputCls = 'w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#1F4E79]';
  const numCls = 'w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2';

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">

      {/* 구분 */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">구분 (선택)</label>
        <select {...register('toilet_type')} className={inputCls}>
          <option value="">선택 안함</option>
          <option value="간이">간이화장실</option>
          <option value="개방">개방화장실</option>
          <option value="공중">공중화장실</option>
          <option value="이동">이동화장실</option>
        </select>
      </div>

      {/* 도로명 주소 */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">소재지 도로명 주소 *</label>
        <input
          {...register('address')}
          className={inputCls}
          placeholder="도로명 주소를 입력하세요"
        />
        {errors.address && <p className="mt-1 text-xs text-red-500">{errors.address.message}</p>}
      </div>

      {/* 지번 주소 */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">소재지 지번 주소 (선택)</label>
        <input
          {...register('address_jibun')}
          className={inputCls}
          placeholder="지번 주소를 입력하세요"
        />
      </div>

      {/* 화장실 이름 */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">화장실 이름 (선택)</label>
        <input
          {...register('name')}
          className={inputCls}
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

      {/* 기본 시설 */}
      <div className="grid grid-cols-2 gap-4">
        <div className="flex items-center gap-2">
          <input type="checkbox" id="is_unisex" {...register('is_unisex')} className="w-4 h-4 rounded" />
          <label htmlFor="is_unisex" className="text-sm font-medium text-gray-700">남녀공용</label>
        </div>
        <div className="flex items-center gap-2">
          <input type="checkbox" id="is_accessible" {...register('is_accessible')} className="w-4 h-4 rounded" />
          <label htmlFor="is_accessible" className="text-sm font-medium text-gray-700">장애인 가능</label>
        </div>
      </div>

      {/* 변기 수 */}
      {isUnisex ? (
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">좌변기 수 (공용)</label>
            <input type="number" min={0} {...register('seat_count', { valueAsNumber: true })} className={inputCls} />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">소변기 수 (공용)</label>
            <input type="number" min={0} {...register('urinal_count', { valueAsNumber: true })} className={inputCls} />
          </div>
        </div>
      ) : (
        <div className="space-y-3">
          {/* 남자 화장실 */}
          <div className="bg-blue-50 rounded-lg p-3">
            <p className="text-sm font-semibold text-blue-800 mb-2">🚹 남자 화장실</p>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs text-gray-600 mb-1">대변기 수</label>
                <input type="number" min={0} {...register('male_seat_count', { valueAsNumber: true })}
                  className={`${numCls} focus:ring-blue-400`} />
              </div>
              <div>
                <label className="block text-xs text-gray-600 mb-1">소변기 수</label>
                <input type="number" min={0} {...register('male_urinal_count', { valueAsNumber: true })}
                  className={`${numCls} focus:ring-blue-400`} />
              </div>
              <div>
                <label className="block text-xs text-gray-600 mb-1">장애인용 대변기</label>
                <input type="number" min={0} {...register('male_disabled_seat_count', { valueAsNumber: true })}
                  className={`${numCls} focus:ring-blue-400`} />
              </div>
              <div>
                <label className="block text-xs text-gray-600 mb-1">장애인용 소변기</label>
                <input type="number" min={0} {...register('male_disabled_urinal_count', { valueAsNumber: true })}
                  className={`${numCls} focus:ring-blue-400`} />
              </div>
              <div>
                <label className="block text-xs text-gray-600 mb-1">어린이용 대변기</label>
                <input type="number" min={0} {...register('male_children_seat_count', { valueAsNumber: true })}
                  className={`${numCls} focus:ring-blue-400`} />
              </div>
              <div>
                <label className="block text-xs text-gray-600 mb-1">어린이용 소변기</label>
                <input type="number" min={0} {...register('male_children_urinal_count', { valueAsNumber: true })}
                  className={`${numCls} focus:ring-blue-400`} />
              </div>
            </div>
          </div>

          {/* 여자 화장실 */}
          <div className="bg-pink-50 rounded-lg p-3">
            <p className="text-sm font-semibold text-pink-800 mb-2">🚺 여자 화장실</p>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs text-gray-600 mb-1">대변기 수</label>
                <input type="number" min={0} {...register('female_seat_count', { valueAsNumber: true })}
                  className={`${numCls} focus:ring-pink-400`} />
              </div>
              <div>
                <label className="block text-xs text-gray-600 mb-1">장애인용 대변기</label>
                <input type="number" min={0} {...register('female_disabled_seat_count', { valueAsNumber: true })}
                  className={`${numCls} focus:ring-pink-400`} />
              </div>
              <div>
                <label className="block text-xs text-gray-600 mb-1">어린이용 대변기</label>
                <input type="number" min={0} {...register('female_children_seat_count', { valueAsNumber: true })}
                  className={`${numCls} focus:ring-pink-400`} />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 개방시간 */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">개방시간 (선택)</label>
        <input
          {...register('open_hours')}
          className={inputCls}
          placeholder="예: 06:00~23:00"
        />
      </div>

      {/* 안전 시설 */}
      <div className="space-y-3">
        <p className="text-sm font-medium text-gray-700">안전 시설</p>
        <div className="grid grid-cols-1 gap-3">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <input type="checkbox" id="has_emergency_bell" {...register('has_emergency_bell')} className="w-4 h-4 rounded" />
              <label htmlFor="has_emergency_bell" className="text-sm text-gray-700">비상벨 설치</label>
            </div>
            {hasEmergencyBell && (
              <input
                {...register('emergency_bell_location')}
                className={inputCls}
                placeholder="비상벨 설치 장소"
              />
            )}
          </div>
          <div className="flex items-center gap-2">
            <input type="checkbox" id="has_entrance_cctv" {...register('has_entrance_cctv')} className="w-4 h-4 rounded" />
            <label htmlFor="has_entrance_cctv" className="text-sm text-gray-700">화장실 입구 CCTV 설치</label>
          </div>
        </div>
      </div>

      {/* 기저귀교환대 */}
      <div>
        <div className="flex items-center gap-2 mb-1">
          <input type="checkbox" id="has_diaper_table" {...register('has_diaper_table')} className="w-4 h-4 rounded" />
          <label htmlFor="has_diaper_table" className="text-sm font-medium text-gray-700">기저귀교환대 있음</label>
        </div>
        {hasDiaperTable && (
          <input
            {...register('diaper_table_location')}
            className={inputCls}
            placeholder="기저귀교환대 장소"
          />
        )}
      </div>

      {/* 리모델링연월 */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">리모델링 연월 (선택)</label>
        <input
          {...register('remodeling_date')}
          className={inputCls}
          placeholder="예: 2023-06"
          maxLength={7}
        />
        {errors.remodeling_date && <p className="mt-1 text-xs text-red-500">{errors.remodeling_date.message}</p>}
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
              className={inputCls}
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
              className={inputCls}
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
