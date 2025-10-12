export type HttpMethod = 'GET' | 'POST' | 'PATCH' | 'DELETE';

export interface RequestOptions {
  query?: Record<string, string | number | boolean | undefined>;
  body?: Record<string, unknown>;
  headers?: HeadersInit;
  credentials?: RequestCredentials;
}
