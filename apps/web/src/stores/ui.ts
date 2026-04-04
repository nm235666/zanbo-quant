import { defineStore } from 'pinia'

export const useUiStore = defineStore('ui', {
  state: () => ({
    sidebarOpen: true,
    mobileNavOpen: false,
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
  },
})
