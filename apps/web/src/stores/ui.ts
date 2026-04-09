import { defineStore } from 'pinia'

export type ToastTone = 'success' | 'error' | 'info'

export interface UiToast {
  id: number
  message: string
  tone: ToastTone
  createdAt: number
}

export const useUiStore = defineStore('ui', {
  state: () => ({
    sidebarOpen: true,
    mobileNavOpen: false,
    toasts: [] as UiToast[],
  }),
  actions: {
    toggleSidebar() {
      this.sidebarOpen = !this.sidebarOpen
    },
    openMobileNav() {
      this.mobileNavOpen = true
    },
    closeMobileNav() {
      this.mobileNavOpen = false
    },
    toggleMobileNav() {
      this.mobileNavOpen = !this.mobileNavOpen
    },
    showToast(message: string, tone: ToastTone = 'info') {
      const id = Date.now() + Math.floor(Math.random() * 1000)
      this.toasts.push({ id, message, tone, createdAt: Date.now() })
      window.setTimeout(() => {
        this.removeToast(id)
      }, 3200)
      return id
    },
    removeToast(id: number) {
      this.toasts = this.toasts.filter((item) => item.id !== id)
    },
    clearToasts() {
      this.toasts = []
    },
  },
})
