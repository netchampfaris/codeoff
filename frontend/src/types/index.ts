declare global {
  interface Window {
    csrf_token: string
    site_name: string
    frappe_version: string
  }
}

export {}
