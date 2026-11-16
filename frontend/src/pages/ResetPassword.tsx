import { Anchor, Button, Group, PasswordInput, PinInput, Stack, Stepper, Text, TextInput } from '@mantine/core'
import { isEmail, matchesField, useForm } from '@mantine/form'
import { ArrowLeft } from '@phosphor-icons/react'
import { useMutation } from '@tanstack/react-query'
import { useState } from 'react'
import { Link, useNavigate } from 'react-router'

import { requestPasswordReset, resetPassword, verifyPasswordResetCode } from '../api/auth'
import { ApiError, commonErrorMessage } from '../api/client'
import { AuthLayout } from '../components/AuthLayout'
import { FormAlert } from '../components/FormAlert'

type Step = 'email' | 'code' | 'password' | 'complete'

function resetErrorMessage(error: unknown) {
  if (error instanceof ApiError && error.status === 400) return 'Код неверный или срок его действия истёк'
  if (error instanceof ApiError && error.status === 429) return 'Исчерпано число попыток. Запросите новый код'
  return commonErrorMessage(error)
}

export function ResetPasswordPage() {
  const [step, setStep] = useState<Step>('email')
  const [resetToken, setResetToken] = useState('')
  const navigate = useNavigate()
  const form = useForm({
    initialValues: { email: '', code: '', password: '', confirmPassword: '' },
    validate: {
      email: isEmail('Неверный формат почты'),
      code: (value) => (/^\d{6}$/.test(value) ? null : 'Введите шестизначный код'),
      password: (value) => (value.length < 8 || value.length > 128 ? 'От 8 до 128 символов' : null),
      confirmPassword: matchesField('password', 'Пароли не совпадают'),
    },
  })

  const requestMutation = useMutation({
    mutationFn: requestPasswordReset,
    onSuccess: () => setStep('code'),
  })
  const verifyMutation = useMutation({
    mutationFn: () => verifyPasswordResetCode(form.values.email.trim(), form.values.code),
    onSuccess: ({ reset_token }) => {
      setResetToken(reset_token)
      setStep('password')
    },
  })
  const resetMutation = useMutation({
    mutationFn: () => resetPassword(resetToken, form.values.password),
    onSuccess: () => setStep('complete'),
  })
  const resendMutation = useMutation({
    mutationFn: () => requestPasswordReset(form.values.email.trim()),
    onSuccess: () => {
      form.setFieldValue('code', '')
      setResetToken('')
    },
  })

  if (step === 'complete') {
    return (
      <AuthLayout title="Пароль изменён" subtitle="Теперь можно войти с новым паролем">
        <Button size="lg" fullWidth onClick={() => navigate('/login', { replace: true })}>
          Перейти ко входу
        </Button>
      </AuthLayout>
    )
  }

  const activeError =
    step === 'email'
      ? requestMutation.error
      : step === 'code'
        ? verifyMutation.error ?? resendMutation.error
        : resetMutation.error

  return (
    <AuthLayout
      title={step === 'email' ? 'Восстановление пароля' : step === 'code' ? 'Код подтверждения' : 'Новый пароль'}
      subtitle={
        step === 'email'
          ? 'Укажите почту, к которой привязан аккаунт. Мы отправим на неё код.'
          : step === 'code'
            ? `Введите шестизначный код, отправленный на ${form.values.email}`
            : `Код подтверждён для ${form.values.email}. Создайте новый пароль.`
      }
    >
      <Stepper active={step === 'email' ? 0 : step === 'code' ? 1 : 2} size="xs" allowNextStepsSelect={false}>
        <Stepper.Step label="Почта" />
        <Stepper.Step label="Код" />
        <Stepper.Step label="Пароль" />
      </Stepper>

      {activeError && <FormAlert>{resetErrorMessage(activeError)}</FormAlert>}

      {step === 'email' && (
        <form
          noValidate
          onSubmit={(event) => {
            event.preventDefault()
            if (!form.validateField('email').hasError) {
              requestMutation.mutate(form.values.email.trim())
            }
          }}
        >
          <Stack gap="lg">
            <TextInput
              label="Почта"
              placeholder="you@example.com"
              type="email"
              autoComplete="email"
              {...form.getInputProps('email')}
            />
            <Button type="submit" size="lg" fullWidth loading={requestMutation.isPending}>
              Отправить код
            </Button>
          </Stack>
        </form>
      )}

      {step === 'code' && (
        <Stack gap="lg">
          {resendMutation.isSuccess && (
            <Text size="sm" c="dimmed">Если аккаунт зарегистрирован на эту почту, новый код отправлен.</Text>
          )}
          <Stack gap="xs">
            <Text fw={500}>Код из письма</Text>
            <PinInput
              length={6}
              size="lg"
              type="number"
              oneTimeCode
              autoFocus
              aria-label="Код из письма"
              value={form.values.code}
              onChange={(value) => form.setFieldValue('code', value)}
              onComplete={() => verifyMutation.mutate()}
              error={verifyMutation.isError}
            />
          </Stack>
          <Button
            size="lg"
            fullWidth
            loading={verifyMutation.isPending}
            disabled={form.values.code.length !== 6}
            onClick={() => verifyMutation.mutate()}
          >
            Подтвердить код
          </Button>
          <Text size="sm" c="dimmed" ta="center">
            Код не пришёл?{' '}
            <Anchor component="button" type="button" onClick={() => resendMutation.mutate()}>
              Отправить повторно
            </Anchor>
          </Text>
        </Stack>
      )}

      {step === 'password' && (
        <form
          noValidate
          onSubmit={form.onSubmit(() => resetMutation.mutate())}
        >
          <Stack gap="lg">
            <Stack gap="md">
              <PasswordInput
                label="Новый пароль"
                placeholder="Не меньше 8 символов"
                autoComplete="new-password"
                {...form.getInputProps('password')}
              />
              <PasswordInput
                label="Повторите пароль"
                autoComplete="new-password"
                {...form.getInputProps('confirmPassword')}
              />
            </Stack>
            <Button type="submit" size="lg" fullWidth loading={resetMutation.isPending}>
              Сохранить пароль
            </Button>
          </Stack>
        </form>
      )}

      <Group justify="center">
        <Button variant="subtle" color="gray" component={Link} to="/login" leftSection={<ArrowLeft size={18} />}>
          Вернуться ко входу
        </Button>
      </Group>
    </AuthLayout>
  )
}