import { Button, createTheme, Input, InputWrapper, Paper, PasswordInput, PinInput, type CSSVariablesResolver } from '@mantine/core'

// Токены из docs/design.md. Hex-значения живут только здесь.
const tokens = {
  bgCanvas: '#F2F0EB',
  bgApp: '#F8F7F4',
  bgSurface: '#FFFFFF',
  bgSunken: '#ECE9E3',
  borderDefault: 'rgba(42, 39, 35, 0.1)',
  borderSubtle: 'rgba(42, 39, 35, 0.06)',
  canvasDot: '#D3CEC5',
  textPrimary: '#2A2723',
  textSecondary: '#67615A',
  textMuted: '#8C857B',
  accent: '#2F6A5F',
  danger: '#A9503F',
}

export const theme = createTheme({
  colors: {
    // 0 - accent/soft, 6 - accent/default, 7 - accent/hover
    accent: ['#E3ECE8', '#C9DAD4', '#A9C4BB', '#87ADA2', '#63958A', '#467F73', '#2F6A5F', '#26574E', '#1E463F', '#163530'],
    // 0 - danger/soft, 6 - danger/default
    red: ['#F5E6E2', '#EBCBC3', '#DFAEA3', '#D39183', '#C67765', '#B9614F', '#A9503F', '#8E4335', '#73362B', '#582920'],
  },
  primaryColor: 'accent',
  primaryShade: 6,
  white: tokens.bgSurface,
  black: tokens.textPrimary,

  fontFamily: '"Golos Text", system-ui, sans-serif',
  headings: {
    fontFamily: '"Golos Text", system-ui, sans-serif',
    fontWeight: '500',
    sizes: {
      h1: { fontSize: '32px', lineHeight: '1.25' },
      h2: { fontSize: '20px', lineHeight: '1.4' },
      h3: { fontSize: '16px', lineHeight: '1.5' },
    },
  },
  fontSizes: { xs: '12px', sm: '13px', md: '14px', lg: '16px', xl: '20px' },
  lineHeights: { xs: '1.3333', sm: '1.5385', md: '1.4286', lg: '1.5', xl: '1.4' },
  spacing: { xs: '8px', sm: '12px', md: '16px', lg: '24px', xl: '32px' },
  radius: { xs: '4px', sm: '6px', md: '8px', lg: '12px', xl: '16px' },
  defaultRadius: 'md',
  shadows: { md: '0 8px 24px rgba(41, 38, 36, 0.06)' },

  components: {
    Button: Button.extend({
      defaultProps: { size: 'sm' },
      styles: { root: { fontWeight: 500 } },
      // Размер L из макетов: 40px, шрифт кнопки 13px
      vars: (_theme, props) =>
        props.size === 'lg'
          ? { root: { '--button-height': '40px', '--button-fz': 'var(--mantine-font-size-sm)' } }
          : { root: {} },
    }),
    Input: Input.extend({
      styles: { input: { fontSize: 'var(--mantine-font-size-md)' } },
    }),
    InputWrapper: InputWrapper.extend({
      styles: {
        label: { fontSize: 'var(--mantine-font-size-md)', marginBottom: 'var(--mantine-spacing-xs)' },
      },
    }),
    PasswordInput: PasswordInput.extend({
      defaultProps: { visibilityToggleButtonProps: { 'aria-label': 'Показать пароль' } },
    }),
    // Фон приложения - bg/app, а карточки и панели - bg/surface
    Paper: Paper.extend({ defaultProps: { bg: 'white' } }),
    PinInput: PinInput.extend({
      defaultProps: { placeholder: '' },
      styles: {
        root: { width: '100%' },
        pinInput: { flex: 1 },
        input: { width: '100%', fontSize: 'var(--mantine-font-size-xl)' },
      },
    }),
  },
})

export const cssVariablesResolver: CSSVariablesResolver = () => ({
  variables: {
    '--sb-bg-canvas': tokens.bgCanvas,
    '--sb-bg-app': tokens.bgApp,
    '--sb-bg-sunken': tokens.bgSunken,
    '--sb-border-subtle': tokens.borderSubtle,
    '--sb-canvas-dot': tokens.canvasDot,
    '--sb-header-height': '56px',
    '--sb-auth-card-width': '400px',
  },
  light: {
    '--mantine-color-body': tokens.bgApp,
    '--mantine-color-text': tokens.textPrimary,
    '--mantine-color-dimmed': tokens.textSecondary,
    '--mantine-color-placeholder': tokens.textMuted,
    '--mantine-color-default-border': tokens.borderDefault,
    '--mantine-color-default-hover': tokens.bgSunken,
    '--mantine-color-error': tokens.danger,
    '--mantine-color-anchor': tokens.accent,
  },
  dark: {},
})
