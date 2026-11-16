import { Button, Stack, Text } from '@mantine/core'
import { SignOut } from '@phosphor-icons/react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router'

import { logout, useMe } from '../api/auth'
import { AuthLayout } from '../components/AuthLayout'

// shortcut: заглушка вместо меню проектов, чтобы проверить вход и выход; заменить на этапе "Проекты"
export function ProjectsPage() {
  const { data: user } = useMe()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const mutation = useMutation({
    mutationFn: logout,
    // Токены очищаются и при ошибке запроса, поэтому уходим на вход в любом случае
    onSettled: () => {
      queryClient.clear()
      navigate('/login', { replace: true })
    },
  })

  return (
    <AuthLayout title={user?.username ?? ''} subtitle={user?.email}>
      <Text>Меню проектов появится здесь позже</Text>
      <Stack gap="xs">
        <Button
          variant="default"
          size="lg"
          fullWidth
          leftSection={<SignOut size={18} />}
          loading={mutation.isPending && !mutation.variables}
          onClick={() => mutation.mutate(false)}
        >
          Выйти
        </Button>
        <Button
          variant="subtle"
          color="gray"
          fullWidth
          loading={mutation.isPending && mutation.variables}
          onClick={() => mutation.mutate(true)}
        >
          Выйти на всех устройствах
        </Button>
      </Stack>
    </AuthLayout>
  )
}
