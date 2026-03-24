import { initSocket } from 'frappe-ui'

let socket: ReturnType<typeof initSocket> | null = null

export function getSocket() {
  if (!socket) {
    socket = initSocket()
  }
  return socket
}
