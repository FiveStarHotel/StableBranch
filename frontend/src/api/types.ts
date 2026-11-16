// Повторяют Pydantic-схемы из backend/app/schemas

export type Token = {
  access_token: string
  refresh_token: string
  token_type: 'bearer'
}

export type User = {
  id: number
  username: string
  email: string
}

export type UserCreate = {
  username: string
  email: string
  password: string
}

// Тело ошибки 422 от FastAPI
export type ValidationErrorBody = {
  detail: { loc: (string | number)[]; msg: string; type: string }[]
}
