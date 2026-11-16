import { clearTokens, getAccessToken, getRefreshToken, setTokens } from '../auth/tokens'
import type { Token } from './types'

export class ApiError extends Error {
  status: number
  // У ошибок бэкенда это строка, у 422 - объект FastAPI
  detail: unknown

  constructor(status: number, detail: unknown) {
    super(typeof detail === 'string' ? detail : `HTTP ${status}`)
    this.status = status
    this.detail = detail
  }
}

type Options = {
  method?: string
  json?: unknown
  form?: URLSearchParams
  // false - запрос без access-токена и без попытки refresh (вход, регистрация…)
  auth?: boolean
}

function request(path: string, { method, json, form, auth = true }: Options) {
  const headers: Record<string, string> = {}
  let body: BodyInit | undefined
  if (json !== undefined) {
    headers['Content-Type'] = 'application/json'
    body = JSON.stringify(json)
  } else if (form) {
    body = form
  }
  const token = auth ? getAccessToken() : null
  if (token) headers.Authorization = `Bearer ${token}`
  return fetch(`/api/v1${path}`, { method: method ?? (body ? 'POST' : 'GET'), headers, body })
}

// Бэкенд отзывает refresh-токен при обновлении, поэтому параллельные запросы
// с истёкшим access-токеном должны ждать один общий refresh, а не слать свои.
let refreshing: Promise<boolean> | null = null

function refreshTokens(): Promise<boolean> {
  refreshing ??= (async () => {
    const refresh_token = getRefreshToken()
    if (!refresh_token) return false
    const res = await request('/auth/refresh', { json: { refresh_token }, auth: false })
    if (!res.ok) return false
    setTokens((await res.json()) as Token)
    return true
  })().finally(() => {
    refreshing = null
  })
  return refreshing
}

export async function api<T>(path: string, options: Options = {}): Promise<T> {
  let res = await request(path, options)

  if (res.status === 401 && options.auth !== false && getAccessToken()) {
    if (!(await refreshTokens())) {
      clearTokens()
      window.location.assign('/login')
      throw new ApiError(401, 'Session expired')
    }
    res = await request(path, options)
  }

  if (!res.ok) {
    throw new ApiError(res.status, await res.json().catch(() => null))
  }
  return (res.status === 204 ? undefined : await res.json()) as T
}

// Общий текст для ошибок, которые страница не разбирает сама
export function commonErrorMessage(error: unknown): string {
  if (!(error instanceof ApiError) || error.status >= 500) {
    return 'Сервер недоступен. Попробуйте позже'
  }
  if (error.status === 422) return 'Проверьте введённые данные'
  return 'Не удалось выполнить запрос. Попробуйте ещё раз'
}
