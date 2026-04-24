export interface APIResponse<T = unknown> {
  success: boolean;
  data: T | null;
  error: {
    code: string;
    message: string;
  } | null;
}

export interface PaginatedResult<T> {
  results: T[];
  total: number;
}
