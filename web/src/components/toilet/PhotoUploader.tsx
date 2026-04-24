'use client';
import { useState, useRef } from 'react';
import Image from 'next/image';
import { Upload, X } from 'lucide-react';
import toast from 'react-hot-toast';
import { uploadToiletPhoto } from '@/lib/api/toilets';

interface Props {
  toiletId: string;
  onUploaded?: (url: string) => void;
  maxPhotos?: number;
  existingCount?: number;
}

const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp'];
const MAX_SIZE = 5 * 1024 * 1024;

export function PhotoUploader({ toiletId, onUploaded, maxPhotos = 5, existingCount = 0 }: Props) {
  const [previews, setPreviews] = useState<{ url: string; file: File }[]>([]);
  const [uploading, setUploading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFiles = (files: FileList) => {
    const remaining = maxPhotos - existingCount - previews.length;
    if (remaining <= 0) {
      toast.error(`최대 ${maxPhotos}장까지 업로드 가능합니다.`);
      return;
    }

    const newPreviews = Array.from(files).slice(0, remaining).filter((file) => {
      if (!ALLOWED_TYPES.includes(file.type)) {
        toast.error(`${file.name}: 지원하지 않는 파일 형식입니다.`);
        return false;
      }
      if (file.size > MAX_SIZE) {
        toast.error(`${file.name}: 파일 크기는 5MB 이하여야 합니다.`);
        return false;
      }
      return true;
    }).map((file) => ({ url: URL.createObjectURL(file), file }));

    setPreviews((prev) => [...prev, ...newPreviews]);
  };

  const removePreview = (index: number) => {
    setPreviews((prev) => {
      URL.revokeObjectURL(prev[index].url);
      return prev.filter((_, i) => i !== index);
    });
  };

  const handleUpload = async () => {
    if (previews.length === 0) return;
    setUploading(true);
    try {
      for (const { file } of previews) {
        const result = await uploadToiletPhoto(toiletId, file);
        onUploaded?.(result.image_url);
      }
      setPreviews([]);
      toast.success('사진이 업로드되었습니다.');
    } catch {
      toast.error('사진 업로드에 실패했습니다.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-3">
      <div
        className="border-2 border-dashed border-gray-300 rounded-xl p-6 text-center cursor-pointer hover:border-[#1F4E79] transition-colors"
        onClick={() => inputRef.current?.click()}
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => { e.preventDefault(); handleFiles(e.dataTransfer.files); }}
      >
        <Upload className="w-8 h-8 text-gray-400 mx-auto mb-2" />
        <p className="text-sm text-gray-500">클릭하거나 드래그로 사진 추가 (최대 {maxPhotos}장, 5MB 이하)</p>
        <input
          ref={inputRef}
          type="file"
          accept="image/jpeg,image/png,image/webp"
          multiple
          className="hidden"
          onChange={(e) => e.target.files && handleFiles(e.target.files)}
        />
      </div>

      {previews.length > 0 && (
        <div className="grid grid-cols-3 gap-2">
          {previews.map(({ url }, index) => (
            <div key={index} className="relative aspect-square rounded-lg overflow-hidden">
              <Image src={url} alt={`미리보기 ${index + 1}`} fill className="object-cover" />
              <button
                type="button"
                onClick={() => removePreview(index)}
                className="absolute top-1 right-1 bg-black/50 text-white rounded-full p-0.5"
              >
                <X className="w-3 h-3" />
              </button>
            </div>
          ))}
        </div>
      )}

      {previews.length > 0 && (
        <button
          type="button"
          onClick={handleUpload}
          disabled={uploading}
          className="w-full bg-[#1F4E79] text-white rounded-lg py-2 text-sm font-medium disabled:opacity-60"
        >
          {uploading ? '업로드 중...' : `${previews.length}장 업로드`}
        </button>
      )}
    </div>
  );
}
