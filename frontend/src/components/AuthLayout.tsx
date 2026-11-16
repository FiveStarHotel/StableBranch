import { Center, Group, Image, Paper, Stack, Text, Title } from '@mantine/core'
import type { ReactNode } from 'react'

import logo from '../assets/logo.svg'

type Props = {
  title: string
  subtitle?: ReactNode
  children: ReactNode
}

// Шапка с логотипом и карточка по центру полотна - общий вид экранов входа
export function AuthLayout({ title, subtitle, children }: Props) {
  return (
    <Stack gap={0} mih="100vh">
      <Group
        h="var(--sb-header-height)"
        px="lg"
        style={{ flexShrink: 0, borderBottom: '1px solid var(--sb-border-subtle)' }}
      >
        <Image src={logo} alt="StableBranch" h={32} w="auto" />
      </Group>
      <Center className="dotted-canvas" flex={1} p="md" pb="var(--sb-header-height)">
        <Paper w="100%" maw="var(--sb-auth-card-width)" p="xl" radius="xl" shadow="md" withBorder>
          <Stack gap="lg">
            <Stack gap={4}>
              <Title order={2}>{title}</Title>
              {subtitle && (
                <Text size="sm" c="dimmed">
                  {subtitle}
                </Text>
              )}
            </Stack>
            {children}
          </Stack>
        </Paper>
      </Center>
    </Stack>
  )
}
