import { Button, Group, PasswordInput, PinInput, Stack, Text, TextInput } from '@mantine/core'
import { isEmail, matchesField, useForm } from '@mantine/form'
import { PencilSimple } from '@phosphor-icons/react'
import { useMutation } from '@tanstack/react-query'
import { useState } from 'react'
import { useNavigate } from 'react-router'

import { confirmRegistration, register } from '../api/auth'
import { ApiError, commonErrorMessage } from '../api/client'
import type { UserCreate, ValidationErrorBody } from '../api/types'
import { AuthLayout } from '../components/AuthLayout'
import { AuthSwitch } from '../components/AuthSwitch'
import { FormAlert } from '../components/FormAlert'

// Те же правила, что в backend/app/schemas/user.py
const USERNAME_RE = /^[\p{L}\p{N}_]+$/u

const fieldMessages: Record<keyof UserCreate, string> = {
  username: 'Только буквы, цифры и _, от 4 символов',
  email: 'Неверный формат почты',
  password: 'От 8 до 128 символов',
}

function registerErrorMessage(error: unknown) {
  if (error instanceof ApiError && error.status === 409) return 'Имя пользователя или почта уже заняты'
  // 422 показываем у полей
  if (error instanceof ApiError && error.status === 422) return null
  return commonErrorMessage(error)
}

export function RegisterPage() {
  const [step, setStep] = useState<'form' | 'code'>('form')
  const form = useForm({
    mode: 'uncontrolled',
    initialValues: { username: '', email: '', password: '', confirmPassword: '' },
    validate: {
      username: (value) => {
        const name = value.trim()
        if (name.length < 4) return 'Минимум 4 символа'
        if (name.length > 256) return 'Не больше 256 символов'
        return USERNAME_RE.test(name) ? null : 'Только буквы, цифры и _'
      },
      email: isEmail('Неверный формат почты'),
      password: (value) => (value.length < 8 || value.length > 128 ? 'От 8 до 128 символов' : null),
      confirmPassword: matchesField('password', 'Пароли не совпадают'),
    },
  })
  const mutation = useMutation({
    mutationFn: register,
    onSuccess: () => setStep('code'),
    onError: (error) => {
      // 422: подсвечиваем поля, которые не прошли проверку на бэкенде
      if (error instanceof ApiError && error.status === 422) {
        for (const { loc } of (error.detail as ValidationErrorBody).detail) {
          const field = loc.at(-1) as keyof UserCreate
          if (field in fieldMessages) form.setFieldError(field, fieldMessages[field])
        }
      }
    },
  })

  if (step === 'code') {
    return <ConfirmStep email={mutation.variables!.email} onBack={() => setStep('form')} />
  }

  const errorMessage = mutation.isError ? registerErrorMessage(mutation.error) : null

  return (
    <AuthLayout title="Регистрация" subtitle="На почту придёт код подтверждения">
      {errorMessage && <FormAlert>{errorMessage}</FormAlert>}
      <form
        noValidate
        onSubmit={form.onSubmit((values) =>
          mutation.mutate({
            username: values.username.trim().normalize('NFC'),
            email: values.email.trim(),
            password: values.password,
          }),
        )}
      >
        <Stack gap="lg">
          <Stack gap="md">
            <TextInput
              label="Имя пользователя"
              placeholder="Например, storyteller"
              autoComplete="username"
              key={form.key('username')}
              {...form.getInputProps('username')}
            />
            <TextInput
              label="Почта"
              placeholder="you@example.com"
              type="email"
              autoComplete="email"
              key={form.key('email')}
              {...form.getInputProps('email')}
            />
            <PasswordInput
              label="Пароль"
              placeholder="Не меньше 8 символов"
              autoComplete="new-password"
              key={form.key('password')}
              {...form.getInputProps('password')}
            />
            <PasswordInput
              label="Повторите пароль"
              autoComplete="new-password"
              key={form.key('confirmPassword')}
              {...form.getInputProps('confirmPassword')}
            />
          </Stack>
          <Button type="submit" size="lg" fullWidth loading={mutation.isPending}>
            Получить код
          </Button>
        </Stack>
      </form>
      <AuthSwitch question="Уже есть аккаунт?" link="Войти" to="/login" />
    </AuthLayout>
  )
}

function confirmErrorMessage(error: unknown) {
  if (error instanceof ApiError && error.status === 400) return 'Неверный или устаревший код'
  if (error instanceof ApiError && error.status === 429) return 'Попытки закончились. Зарегистрируйтесь заново'
  return commonErrorMessage(error)
}

function ConfirmStep({ email, onBack }: { email: string; onBack: () => void }) {
  const navigate = useNavigate()
  const [code, setCode] = useState('')
  const mutation = useMutation({
    mutationFn: (value: string) => confirmRegistration(email, value),
    onSuccess: () => navigate('/projects', { replace: true }),
    // Очищаем ячейки, чтобы новый код снова отправился сам после шестой цифры
    onError: () => setCode(''),
  })
  const submit = (value: string) => {
    if (value.length === 6 && !mutation.isPending) mutation.mutate(value)
  }

  return (
    <AuthLayout
      title="Подтвердите почту"
      subtitle={`Мы отправили шестизначный код на ${email}. Введите его ниже.`}
    >
      {mutation.isError && <FormAlert>{confirmErrorMessage(mutation.error)}</FormAlert>}
      <form
        onSubmit={(event) => {
          event.preventDefault()
          submit(code)
        }}
      >
        <Stack gap="lg">
          <Stack gap="xs">
            <Text fw={500}>Код из письма</Text>
            <PinInput
              length={6}
              size="lg"
              type="number"
              oneTimeCode
              autoFocus
              aria-label="Код из письма"
              value={code}
              onChange={setCode}
              onComplete={submit}
              error={mutation.isError}
            />
          </Stack>
          <Button type="submit" size="lg" fullWidth loading={mutation.isPending} disabled={code.length < 6}>
            Подтвердить
          </Button>
        </Stack>
      </form>
      <Group>
        <Button variant="subtle" color="gray" size="xs" leftSection={<PencilSimple size={18} />} onClick={onBack}>
          Изменить данные
        </Button>
      </Group>
    </AuthLayout>
  )
}
