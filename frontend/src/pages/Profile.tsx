import {
  Avatar,
  Button,
  Container,
  Group,
  Image,
  Paper,
  PasswordInput,
  PinInput,
  SimpleGrid,
  Stack,
  Text,
  TextInput,
  Title,
} from '@mantine/core'
import { isEmail, matchesField, useForm } from '@mantine/form'
import { ArrowLeft, SignOut } from '@phosphor-icons/react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { Link, useNavigate } from 'react-router'

import { changePassword, confirmEmailChange, logout, requestEmailChange, useMe } from '../api/auth'
import { ApiError, commonErrorMessage } from '../api/client'
import { FormAlert } from '../components/FormAlert'
import logo from '../assets/logo.svg'

function accountErrorMessage(error: unknown) {
  if (error instanceof ApiError && error.status === 400) return 'Код неверный или срок его действия истёк'
  if (error instanceof ApiError && error.status === 401) return 'Текущий пароль указан неверно'
  if (error instanceof ApiError && error.status === 409) return 'Эта почта уже используется другим аккаунтом'
  if (error instanceof ApiError && error.status === 429) return 'Исчерпано число попыток. Запросите новый код'
  return commonErrorMessage(error)
}

export function ProfilePage() {
  const { data: user } = useMe()
  const [emailCodeStep, setEmailCodeStep] = useState(false)
  const [emailSuccess, setEmailSuccess] = useState(false)
  const [passwordSuccess, setPasswordSuccess] = useState(false)
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const emailForm = useForm({
    initialValues: { newEmail: '', code: '' },
    validate: { newEmail: isEmail('Неверный формат почты') },
  })
  const passwordForm = useForm({
    initialValues: { oldPassword: '', newPassword: '', confirmPassword: '' },
    validate: {
      oldPassword: (value) => (value ? null : 'Введите текущий пароль'),
      newPassword: (value) => (value.length < 8 || value.length > 128 ? 'От 8 до 128 символов' : null),
      confirmPassword: matchesField('newPassword', 'Пароли не совпадают'),
    },
  })

  const requestEmailMutation = useMutation({
    mutationFn: (newEmail: string) => requestEmailChange(user!.email, newEmail),
    onSuccess: () => {
      setEmailCodeStep(true)
      setEmailSuccess(false)
      emailForm.setFieldValue('code', '')
    },
  })
  const confirmEmailMutation = useMutation({
    mutationFn: () => confirmEmailChange(emailForm.values.newEmail.trim(), emailForm.values.code),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['users', 'me'] })
      emailForm.reset()
      setEmailCodeStep(false)
      setEmailSuccess(true)
    },
  })
  const passwordMutation = useMutation({
    mutationFn: () => changePassword(passwordForm.values.oldPassword, passwordForm.values.newPassword),
    onSuccess: () => {
      passwordForm.reset()
      setPasswordSuccess(true)
    },
  })
  const logoutMutation = useMutation({
    mutationFn: logout,
    onSettled: () => {
      queryClient.clear()
      navigate('/login', { replace: true })
    },
  })

  return (
    <Stack gap={0} mih="100vh">
      <Group
        h="var(--sb-header-height)"
        px="lg"
        justify="space-between"
        style={{ flexShrink: 0, borderBottom: '1px solid var(--sb-border-subtle)' }}
      >
        <Image src={logo} alt="StableBranch" h={32} w="auto" />
        <Group gap="sm">
          <Avatar size="sm" color="accent">{user?.username.slice(0, 1).toUpperCase()}</Avatar>
          <Text size="sm">{user?.username}</Text>
        </Group>
      </Group>

      <Container size="xl" py="xl" w="100%">
        <Stack gap="xl">
          <Button
            variant="subtle"
            color="gray"
            component={Link}
            to="/projects"
            leftSection={<ArrowLeft size={18} />}
            w="fit-content"
          >
            Мои проекты
          </Button>
          <Stack gap={4}>
            <Title order={1}>Профиль</Title>
            <Text size="sm" c="dimmed">{user?.username} · {user?.email}</Text>
          </Stack>

          <SimpleGrid cols={{ base: 1, sm: 2 }} spacing="lg" verticalSpacing="lg">
        <Paper withBorder p="lg" radius="md">
          <Stack gap="md">
            <Stack gap={4}>
              <Title order={3}>Почта</Title>
              <Text size="sm" c="dimmed">
                Текущая почта: {user?.email}. Код подтверждения придёт на новый адрес.
              </Text>
            </Stack>

            {requestEmailMutation.isError && <FormAlert>{accountErrorMessage(requestEmailMutation.error)}</FormAlert>}
            {confirmEmailMutation.isError && <FormAlert>{accountErrorMessage(confirmEmailMutation.error)}</FormAlert>}
            {emailSuccess && <Text size="sm" c="accent">Почта обновлена</Text>}

            {!emailCodeStep ? (
              <form noValidate onSubmit={emailForm.onSubmit((values) => requestEmailMutation.mutate(values.newEmail.trim()))}>
                <Stack gap="md">
                  <TextInput
                    label="Новая почта"
                    placeholder="new@example.com"
                    type="email"
                    autoComplete="email"
                    {...emailForm.getInputProps('newEmail')}
                  />
                  <Button type="submit" loading={requestEmailMutation.isPending}>
                    Получить код
                  </Button>
                </Stack>
              </form>
            ) : (
              <Stack gap="md">
                <Text size="sm">Код отправлен на {emailForm.values.newEmail}</Text>
                <Stack gap="xs">
                  <Text fw={500}>Код из письма</Text>
                  <PinInput
                    length={6}
                    type="number"
                    oneTimeCode
                    aria-label="Код подтверждения почты"
                    value={emailForm.values.code}
                    onChange={(value) => emailForm.setFieldValue('code', value)}
                    error={confirmEmailMutation.isError}
                  />
                </Stack>
                <Group grow>
                  <Button
                    variant="default"
                    loading={requestEmailMutation.isPending}
                    onClick={() => requestEmailMutation.mutate(emailForm.values.newEmail.trim())}
                  >
                    Отправить снова
                  </Button>
                  <Button
                    loading={confirmEmailMutation.isPending}
                    disabled={emailForm.values.code.length !== 6}
                    onClick={() => confirmEmailMutation.mutate()}
                  >
                    Подтвердить
                  </Button>
                </Group>
                <Button
                  variant="subtle"
                  color="gray"
                  size="xs"
                  onClick={() => {
                    setEmailCodeStep(false)
                    emailForm.setFieldValue('code', '')
                  }}
                >
                  Изменить адрес
                </Button>
              </Stack>
            )}
          </Stack>
        </Paper>

        <Paper withBorder p="lg" radius="md">
          <form
            noValidate
            onSubmit={passwordForm.onSubmit(() => passwordMutation.mutate())}
          >
            <Stack gap="md">
              <Title order={3}>Пароль</Title>
              {passwordMutation.isError && <FormAlert>{accountErrorMessage(passwordMutation.error)}</FormAlert>}
              {passwordSuccess && <Text size="sm" c="accent">Пароль изменён</Text>}
              <PasswordInput
                label="Текущий пароль"
                autoComplete="current-password"
                {...passwordForm.getInputProps('oldPassword')}
              />
              <PasswordInput
                label="Новый пароль"
                placeholder="Не меньше 8 символов"
                autoComplete="new-password"
                {...passwordForm.getInputProps('newPassword')}
              />
              <PasswordInput
                label="Повторите пароль"
                autoComplete="new-password"
                {...passwordForm.getInputProps('confirmPassword')}
              />
              <Button type="submit" loading={passwordMutation.isPending}>
                Сменить пароль
              </Button>
            </Stack>
          </form>
        </Paper>
          </SimpleGrid>

          <Group justify="flex-end">
            <Button
              variant="default"
              leftSection={<SignOut size={18} />}
              loading={logoutMutation.isPending && !logoutMutation.variables}
              onClick={() => logoutMutation.mutate(false)}
            >
              Выйти
            </Button>
            <Button
              variant="subtle"
              color="gray"
              loading={logoutMutation.isPending && logoutMutation.variables}
              onClick={() => logoutMutation.mutate(true)}
            >
              Выйти на всех устройствах
            </Button>
          </Group>
        </Stack>
      </Container>
    </Stack>
  )
}