import { Button, PasswordInput, Stack, TextInput } from '@mantine/core'
import { useForm } from '@mantine/form'
import { useMutation } from '@tanstack/react-query'
import { useNavigate } from 'react-router'

import { login } from '../api/auth'
import { ApiError, commonErrorMessage } from '../api/client'
import { AuthLayout } from '../components/AuthLayout'
import { AuthSwitch } from '../components/AuthSwitch'
import { FormAlert } from '../components/FormAlert'

function loginErrorMessage(error: unknown) {
  if (error instanceof ApiError && error.status === 401) return 'Неверный логин или пароль'
  if (error instanceof ApiError && error.status === 403) return 'Почта не подтверждена. Пройдите регистрацию заново'
  return commonErrorMessage(error)
}

export function LoginPage() {
  const navigate = useNavigate()
  const form = useForm({
    mode: 'uncontrolled',
    initialValues: { login: '', password: '' },
    validate: {
      login: (value) => (value.trim() ? null : 'Введите почту или имя пользователя'),
      password: (value) => (value ? null : 'Введите пароль'),
    },
  })
  const mutation = useMutation({
    // Бэкенд приводит имя к NFC и обрезает пробелы при регистрации, делаем так же
    mutationFn: (values: typeof form.values) => login(values.login.trim().normalize('NFC'), values.password),
    onSuccess: () => navigate('/projects', { replace: true }),
  })

  return (
    <AuthLayout title="Вход" subtitle="Войдите, чтобы продолжить работу над историями">
      {mutation.isError && <FormAlert>{loginErrorMessage(mutation.error)}</FormAlert>}
      <form onSubmit={form.onSubmit((values) => mutation.mutate(values))} noValidate>
        <Stack gap="lg">
          <Stack gap="md">
            <TextInput
              label="Почта или имя пользователя"
              placeholder="you@example.com"
              autoComplete="username"
              key={form.key('login')}
              {...form.getInputProps('login')}
            />
            <PasswordInput
              label="Пароль"
              autoComplete="current-password"
              key={form.key('password')}
              {...form.getInputProps('password')}
            />
          </Stack>
          <Button type="submit" size="lg" fullWidth loading={mutation.isPending}>
            Войти
          </Button>
        </Stack>
      </form>
      <AuthSwitch question="Нет аккаунта?" link="Зарегистрироваться" to="/register" />
    </AuthLayout>
  )
}
