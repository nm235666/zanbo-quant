import { defineStore } from 'pinia'
import type { NavSurface } from '../app/navigation'

export type ToastTone = 'success' | 'error' | 'info'

export interface UiToast {
  id: number
  message: string
  tone: ToastTone
  createdAt: number
}

export const useUiStore = defineStore('ui', {
  state: () => ({
    appSidebarOpen: true,
    adminSidebarOpen: true,
    mobileNavOpen: false,
    toasts: [] as UiToast[],
  }),
  actions: {
    isSidebarOpen(surface: NavSurface) {
      return surface === 'admin' ? this.adminSidebarOpen : this.appSidebarOpen
    },
    setSidebarOpen(surface: NavSurface, open: boolean) {
      if (surface === 'admin') {
        this.adminSidebarOpen = open
        return
      }
      this.appSidebarOpen = open
    },
    toggleSidebar(surface: NavSurface) {
      this.setSidebarOpen(surface, !this.isSidebarOpen(surface))
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
