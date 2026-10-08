export default defineNuxtRouteMiddleware((to) => {
  const { token, init } = useAuth()
  init()
  if (!token.value && to.path !== '/login') {
    return navigateTo('/login')
  }
  if (token.value && to.path === '/login') {
    return navigateTo('/')
  }
})
