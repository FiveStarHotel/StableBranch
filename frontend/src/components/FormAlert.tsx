import { Alert } from '@mantine/core'
import { WarningCircle } from '@phosphor-icons/react'

// Плашка ошибки из макета: фон danger/soft, текст и иконка danger/default
export function FormAlert({ children }: { children: string }) {
  return (
    <Alert
      color="red"
      bg="red.0"
      p="xs"
      icon={<WarningCircle size={18} />}
      styles={{ message: { color: 'var(--mantine-color-red-6)', fontSize: 'var(--mantine-font-size-sm)' } }}
    >
      {children}
    </Alert>
  )
}
