import { Anchor, Text } from '@mantine/core'
import { Link } from 'react-router'

type Props = { question: string; link: string; to: string }

export function AuthSwitch({ question, link, to }: Props) {
  return (
    <Text size="sm" c="dimmed" ta="center">
      {question}{' '}
      <Anchor component={Link} to={to} size="sm" fw={500}>
        {link}
      </Anchor>
    </Text>
  )
}
