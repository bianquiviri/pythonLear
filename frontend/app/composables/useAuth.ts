export interface Client {
  id: number
  name: string
  email: string
  phone?: string | null
  address?: string | null
  notes?: string | null
  is_active: boolean
  created_at: string
  updated_at?: string | null
}

export interface PageMeta {
  page: number
  per_page: number
  total: number
  pages: number
}

export interface ClientList {
  items: Client[]
  meta: PageMeta
}

export interface User {
  id: number
  email: string
  full_name: string
  role: string
}

const TOKEN_KEY = 'spa_token'

export function useAuth() {
  const token = useState<string | null>('token', () => null)
  const user = useState<User | null>('user', () => null)

  function init() {
    if (import.meta.client && !token.value) {
      token.value = localStorage.getItem(TOKEN_KEY)
    }
  }

  async function login(email: string, password: string) {
    const res = await useApi().post<{ access_token: string }>('/api/v1/auth/login', {
      email,
      password,
    })
    token.value = res.access_token
    if (import.meta.client) {
      localStorage.setItem(TOKEN_KEY, res.access_token)
    }
    user.value = await useApi().get<User>('/api/v1/auth/me')
  }

  async function fetchUser() {
    if (!token.value)
      return
    try {
      user.value = await useApi().get<User>('/api/v1/auth/me')
    }
    catch {
      logout()
    }
  }

  function logout() {
    token.value = null
    user.value = null
    if (import.meta.client) {
      localStorage.removeItem(TOKEN_KEY)
    }
    navigateTo('/login')
  }

  const isAuthenticated = computed(() => Boolean(token.value))

  return { token, user, login, logout, init, fetchUser, isAuthenticated }
}
