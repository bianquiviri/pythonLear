# Frontend agent rules

Owns: `frontend/` (Nuxt 4 SPA).

## Conventions

- Nuxt 4 structure: everything under `frontend/app/` (pages, components, composables, middleware).
- SPA mode (`ssr: false`). Auth token in `localStorage`; middleware `auth` guards private pages.
- TypeScript always; no `any` when a type exists. Export shared types from composables.
- Components: PascalCase (`ClientTable.vue`), one responsibility, `defineProps`/`defineEmits` typed.
- Styling: plain CSS in `assets/css/main.css`, CSS variables, no CSS framework.

## Data layer

- All HTTP goes through `useApi()` — never call `$fetch` directly in components.
  It attaches the Bearer token and maps errors to `ApiError { status, message }`.
- API base is same-origin (`''`); nginx proxies `/api` to the backend. Do not hardcode hosts.
- Composables own state (`useState`), pages own fetching (`onMounted` + loading flags).

## TDD / quality

- Pure logic lives in composables/utils so it is testable with vitest (`tests/unit/*.spec.ts`).
- Gates: `npm run lint` and `npm test` green; `npm run build` must succeed.
- UI states required for every view: loading, empty, error, success.
- Destructive actions (delete) require confirmation.

## UX rules

- Keep it simple: table + search + pagination for clients; form modal for create/edit.
- Accessible: labels tied to inputs, buttons have text (not icon-only), focus styles visible.
- Do not store passwords or JWT secrets anywhere except the token in localStorage.
