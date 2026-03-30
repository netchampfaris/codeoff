import { computed, reactive, ref } from 'vue'
import { useCall } from 'frappe-ui'
import router from '@/router'

const CODEOFF_LOGIN_REDIRECT = '/codeoff'

export const sessionUser = ref<string | null>(getSessionUserFromCookie())

export const session = reactive({
  login: useCall({
    url: '/api/v2/method/login',
    immediate: false,
    onSuccess(data: any) {
      sessionUser.value = getSessionUserFromCookie()
      session.login.reset()
      window.location.href = data?.default_route || CODEOFF_LOGIN_REDIRECT
    },
  }),
  logout: useCall({
    url: '/api/v2/method/logout',
    method: 'POST',
    immediate: false,
    onSuccess() {
      sessionUser.value = getSessionUserFromCookie()
      window.location.href = '/login'
    },
  }),
  user: sessionUser,
  isLoggedIn: computed(() => sessionUser.value != null),
})

export { CODEOFF_LOGIN_REDIRECT }

function getSessionUserFromCookie(): string | null {
  const cookies = new URLSearchParams(document.cookie.split('; ').join('&'))
  let user = cookies.get('user_id')
  if (user === 'Guest') {
    user = null
  }
  return user
}
