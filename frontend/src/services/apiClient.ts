import type { HttpMethod, RequestOptions } from '../types/http';
import { buildUrl } from '../utils/url';

const REQUEST_TIMEOUT = 6000;

const DEFAULT_HEADERS: HeadersInit = {
  'Content-Type': 'application/json'
};

const getBaseUrl = () => {
  return (
    import.meta.env.VITE_API_BASE_URL ||
    (window as unknown as { __API_BASE_URL__?: string }).__API_BASE_URL__ ||
    '/api'
  );
};

export const createApiClient = () => {
  const baseUrl = getBaseUrl();
  const inFlight = new Map<string, AbortController>();

  const request = async <T>(method: HttpMethod, path: string, options: RequestOptions = {}) => {
    const url = buildUrl(baseUrl, path, options.query);
    const key = `${method}:${url}:${options.body ? JSON.stringify(options.body) : ''}`;

    if (inFlight.has(key)) {
      inFlight.get(key)?.abort();
      inFlight.delete(key);
    }

    const controller = new AbortController();
    inFlight.set(key, controller);

    const timeoutId = window.setTimeout(() => controller.abort('timeout'), REQUEST_TIMEOUT);

    try {
      const response = await fetch(url, {
        method,
        headers: { ...DEFAULT_HEADERS, ...(options.headers ?? {}) },
        body: options.body ? JSON.stringify(options.body) : undefined,
        signal: controller.signal,
        credentials: options.credentials ?? 'include'
      });

      if (!response.ok) {
        const errorBody = await safeJson(response);
        throw createHttpError(response.status, errorBody);
      }

      if (response.status === 204) {
        return undefined as T;
      }

      const json = (await response.json()) as T;
      return json;
    } catch (error) {
      if ((error instanceof DOMException && error.name === 'AbortError') || error === 'timeout') {
        throw createHttpError(408, { detail: '요청이 제한시간을 초과했습니다.' });
      }
      throw error;
    } finally {
      window.clearTimeout(timeoutId);
      inFlight.delete(key);
    }
  };

  return {
    get: <T>(path: string, options?: RequestOptions) => request<T>('GET', path, options),
    post: <T>(path: string, options?: RequestOptions) => request<T>('POST', path, options),
    patch: <T>(path: string, options?: RequestOptions) => request<T>('PATCH', path, options),
    del: <T>(path: string, options?: RequestOptions) => request<T>('DELETE', path, options)
  };
};

const safeJson = async (response: Response) => {
  try {
    return await response.json();
  } catch (error) {
    console.warn('JSON 파싱에 실패했습니다.', error);
    return null;
  }
};

const createHttpError = (status: number, body: unknown) => {
  const error = new Error('HTTP Error') as Error & {
    status: number;
    body: unknown;
  };
  error.status = status;
  error.body = body;
  return error;
};
