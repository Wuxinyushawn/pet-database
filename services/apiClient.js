const DEFAULT_TIMEOUT = 10000;

export class ApiError extends Error {
  constructor(message, { status, code, details } = {}) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

const DEFAULT_ERROR_MESSAGE = 'Request failed. Please try again.';

function joinUrl(baseURL, path) {
  if (/^https?:\/\//.test(path)) return path;
  return `${baseURL.replace(/\/$/, '')}/${path.replace(/^\//, '')}`;
}

function mapError(status, payload) {
  const message = payload?.message || payload?.error || DEFAULT_ERROR_MESSAGE;
  if (status === 400) return new ApiError(message || 'Invalid request.', { status, code: 'BAD_REQUEST', details: payload });
  if (status === 401 || status === 403) return new ApiError(message || 'Unauthorized.', { status, code: 'UNAUTHORIZED', details: payload });
  if (status === 404) return new ApiError(message || 'Resource not found.', { status, code: 'NOT_FOUND', details: payload });
  if (status === 409) return new ApiError(message || 'Conflict detected, refresh and retry.', { status, code: 'CONFLICT', details: payload });
  if (status >= 500) return new ApiError(message || 'Server error, please retry later.', { status, code: 'SERVER_ERROR', details: payload });
  return new ApiError(message, { status, code: 'HTTP_ERROR', details: payload });
}

export function createApiClient({ baseURL = '/api', timeout = DEFAULT_TIMEOUT } = {}) {
  async function request(path, { method = 'GET', headers = {}, body, signal } = {}) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeout);
    const combinedSignal = signal || controller.signal;

    try {
      const response = await fetch(joinUrl(baseURL, path), {
        method,
        headers: {
          Accept: 'application/json',
          ...(body ? { 'Content-Type': 'application/json' } : {}),
          ...headers
        },
        body: body ? JSON.stringify(body) : undefined,
        signal: combinedSignal
      });

      const contentType = response.headers.get('content-type') || '';
      const payload = contentType.includes('application/json') ? await response.json() : null;

      if (!response.ok) throw mapError(response.status, payload);
      return payload;
    } catch (error) {
      if (error.name === 'AbortError') {
        throw new ApiError('Request timeout, please retry.', { code: 'TIMEOUT' });
      }
      if (error instanceof ApiError) throw error;
      throw new ApiError(error.message || 'Network error, please check your connection.', { code: 'NETWORK_ERROR' });
    } finally {
      clearTimeout(timer);
    }
  }

  return {
    get: (path, options) => request(path, { ...options, method: 'GET' }),
    post: (path, body, options) => request(path, { ...options, method: 'POST', body }),
    patch: (path, body, options) => request(path, { ...options, method: 'PATCH', body }),
    put: (path, body, options) => request(path, { ...options, method: 'PUT', body }),
    delete: (path, options) => request(path, { ...options, method: 'DELETE' })
  };
}
