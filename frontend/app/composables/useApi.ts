export class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

export function useApi() {
  const config = useRuntimeConfig()
  const base = config.public.apiBase || ''
  const { token } = useAuth()

  function headers(): Record<string, string> {
    const h: Record<string, string> = { 'Content-Type': 'application/json' }
    if (token.value)
      h.Authorization = `Bearer ${token.value}`
    return h
  }

  async function request<T>(method: string, path: string, body?: unknown): Promise<T> {
    try {
      return await $fetch<T>(`${base}${path}`, {
        method: method as 'GET',
        headers: headers(),
        body: body as never,
      })
    }
    catch (error: unknown) {
      const err = error as { status?: number, data?: { detail?: string } }
      const status = err.status ?? 500
      const detail = err.data?.detail ?? 'Unexpected error'
      throw new ApiError(status, typeof detail === 'string' ? detail : JSON.stringify(detail))
    }
  }

  return {
    get: <T>(path: string) => request<T>('GET', path),
    post: <T>(path: string, body?: unknown) => request<T>('POST', path, body),
    put: <T>(path: string, body?: unknown) => request<T>('PUT', path, body),
    remove: <T>(path: string) => request<T>('DELETE', path),
  }
}
