import { Button, Center, Loader, Stack, Text } from '@mantine/core'
import { Navigate, Outlet } from 'react-router'

import { useMe } from '../api/auth'
import { getAccessToken } from './tokens'

export function RequireAuth() {
  const me = useMe()

  if (getAccessToken() === null) return <Navigate to="/login" replace />
  if (me.isPending) {
    return (
      <Center h="100vh">
        <Loader />
      </Center>
    )
  }
  // 401 сюда не доходит: api() сам обновляет токены или уводит на /login
  if (me.isError) {
    return (
      <Center h="100vh">
        <Stack align="center" gap="sm">
          <Text c="dimmed">Не удалось загрузить данные пользователя</Text>
          <Button variant="default" onClick={() => me.refetch()}>
            Повторить
          </Button>
        </Stack>
      </Center>
    )
  }
  return <Outlet />
}

export function GuestOnly() {
  return getAccessToken() === null ? <Outlet /> : <Navigate to="/projects" replace />
}
