import { useQuery } from '@tanstack/react-query'

import { clearTokens, getAccessToken, getRefreshToken, setTokens } from '../auth/tokens'
import { api } from './client'
import type { Token, User, UserCreate } from './types'

export const meKey = ['users', 'me']

export function useMe() {
  return useQuery({
    queryKey: meKey,
    queryFn: () => api<User>('/users/me'),
    enabled: getAccessToken() !== null,
  })
}

// login - имя пользователя или почта, бэкенд принимает оба варианта
export async function login(loginOrEmail: string, password: string) {
  const form = new URLSearchParams({ username: loginOrEmail, password })
  setTokens(await api<Token>('/auth/login', { form, auth: false }))
}

export function register(payload: UserCreate) {
  return api<{ detail: string }>('/auth/register', { json: payload, auth: false })
}

export function requestPasswordReset(email: string) {
  return api<{ detail: string }>('/auth/forgot-password', {
    json: { email },
    auth: false,
  })
}

export function verifyPasswordResetCode(email: string, code: string) {
  return api<{ reset_token: string }>('/auth/forgot-password/verify-code', {
    json: { email, code },
    auth: false,
  })
}

export function resetPassword(reset_token: string, new_password: string) {
  return api<void>('/auth/forgot-password/reset', {
    json: { reset_token, new_password },
    auth: false,
  })
}

export function requestEmailChange(old_email: string, new_email: string) {
  return api<{ detail: string }>('/auth/change-email', { json: { old_email, new_email } })
}

export function confirmEmailChange(email: string, code: string) {
  return api<void>('/auth/change-email/confirm', { json: { email, code } })
}

export function changePassword(old_password: string, new_password: string) {
  return api<void>('/auth/change-password', { json: { old_password, new_password } })
}

export function updateUsername(username: string) {
  return api<User>('/users/me', { method: 'PATCH', json: { username } })
}

export function deleteAccount() {
  return api<void>('/users/me', { method: 'DELETE' })
}

export async function confirmRegistration(email: string, code: string) {
  setTokens(await api<Token>('/auth/register/confirm', { json: { email, code }, auth: false }))
}

export async function logout(allDevices: boolean) {
  const refresh_token = getRefreshToken()
  try {
    if (refresh_token) {
      await api(allDevices ? '/auth/logout-all' : '/auth/logout', { json: { refresh_token }, auth: false })
    }
  } finally {
    clearTokens()
  }
}
