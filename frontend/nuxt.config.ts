export default defineNuxtConfig({
  modules: ['@nuxt/eslint'],
  ssr: false,
  app: {
    head: {
      title: 'Clients SPA',
      htmlAttrs: { lang: 'en' },
    },
  },
  css: ['~/assets/css/main.css'],
  runtimeConfig: {
    public: {
      apiBase: '',
    },
  },
  compatibilityDate: '2025-10-01',
  nitro: {
    devProxy: {
      '/api': 'http://localhost:8000',
    },
    prerender: {
      routes: ['/'],
    },
  },
  eslint: {
    config: {
      stylistic: true,
    },
  },
})
