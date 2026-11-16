import '@mantine/core/styles.css'
import './index.css'

import { MantineProvider } from '@mantine/core'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { createBrowserRouter, Navigate } from 'react-router'
import { RouterProvider } from 'react-router/dom'

import { GuestOnly, RequireAuth } from './auth/guards'
import { LoginPage } from './pages/Login'
import { ProjectsPage } from './pages/Projects'
import { RegisterPage } from './pages/Register'
import { cssVariablesResolver, theme } from './theme'

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
})

const router = createBrowserRouter([
  {
    Component: GuestOnly,
    children: [
      { path: '/login', Component: LoginPage },
      { path: '/register', Component: RegisterPage },
    ],
  },
  {
    Component: RequireAuth,
    children: [{ path: '/projects', Component: ProjectsPage }],
  },
  // shortcut: лендинга пока нет, всё остальное ведёт в приложение (или на вход)
  { path: '*', element: <Navigate to="/projects" replace /> },
])

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <MantineProvider theme={theme} cssVariablesResolver={cssVariablesResolver} defaultColorScheme="light">
      <QueryClientProvider client={queryClient}>
        <RouterProvider router={router} />
      </QueryClientProvider>
    </MantineProvider>
  </StrictMode>,
)
