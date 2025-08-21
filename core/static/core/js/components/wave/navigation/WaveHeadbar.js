/**
 * WaveHeadbar - Professional navigation header with Grove design
 * Part of HydroML Grove Component Library
 * 
 * Simplified version focused on Grove demo functionality
 */

class WaveHeadbar {
    static createAlpineData(config = {}) {
        // Essential configuration only
        const defaultConfig = {
            logoText: 'Grove',
            logoSrc: '/static/core/img/logos/grove_logo.svg',
            showSearch: true,
            showThemeToggle: true,
            showNotifications: true,
            showUserMenu: true,
            notificationCount: 0,
            userInitials: 'G',
            userName: 'User',
            navigationItems: []
        };
        
        const mergedConfig = { ...defaultConfig, ...config };
        
        return {
            // Configuration
            ...mergedConfig,
            
            // State
            mobileMenuOpen: false,
            userMenuOpen: false,
            notificationsMenuOpen: false,
            searchFocused: false,
            
            // Computed Properties
            get headbarClasses() {
                return [
                    'wave-headbar', 'w-full', 'transition-all', 'duration-200',
                    'border-b', 'border-gray-200', 'dark:border-gray-700',
                    'bg-white', 'dark:bg-gray-900', 'sticky', 'top-0', 'z-50',
                    'px-4', 'py-3', 'flex', 'items-center', 'justify-between'
                ].join(' ');
            },
            
            // HTML Generation Methods
            getLogoHtml() {
                return `
                    <a href="/dashboard/" class="flex items-center space-x-2 flex-shrink-0">
                        <img src="${this.logoSrc}" alt="${this.logoText}" class="h-8 w-8">
                        <span class="font-semibold text-gray-900 dark:text-white">${this.logoText}</span>
                    </a>
                `;
            },
            
            getMobileToggleHtml() {
                return `
                    <button @click="toggleMobileMenu()" 
                            class="p-2 rounded-md text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800">
                        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
                        </svg>
                    </button>
                `;
            },
            
            getSearchHtml() {
                return `
                    <div class="relative">
                        <input type="text" 
                               placeholder="Search..." 
                               @focus="searchFocused = true" 
                               @blur="searchFocused = false"
                               class="w-64 px-3 py-2 text-sm border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-800 dark:border-gray-600 dark:text-white">
                        <svg class="absolute right-3 top-2.5 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                        </svg>
                    </div>
                `;
            },
            
            getThemeToggleHtml() {
                return `
                    <button @click="toggleTheme()" 
                            class="p-2 rounded-md text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"></path>
                        </svg>
                    </button>
                `;
            },
            
            getNotificationsHtml() {
                return `
                    <button @click="toggleNotifications()" 
                            class="relative p-2 rounded-md text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-5-5-5 5h5zm0 0v-5a6 6 0 00-12 0v5"></path>
                        </svg>
                        <span x-show="notificationCount > 0" 
                              class="absolute -top-1 -right-1 inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white bg-red-600 rounded-full"
                              x-text="notificationCount"></span>
                    </button>
                `;
            },
            
            getUserMenuHtml() {
                return `
                    <button @click="toggleUserMenu()" 
                            class="flex items-center space-x-2 p-2 rounded-md text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800">
                        <div class="w-8 h-8 bg-gray-300 dark:bg-gray-600 rounded-full flex items-center justify-center text-sm font-medium">
                            ${this.userInitials}
                        </div>
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                        </svg>
                    </button>
                `;
            },
            
            getMobileMenuHtml() {
                return `
                    <div class="absolute top-full left-0 right-0 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 shadow-lg">
                        <div class="px-4 py-2 space-y-2">
                            <template x-for="item in navigationItems" :key="item.text">
                                <a :href="item.href" 
                                   class="block px-3 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-md"
                                   x-text="item.text"></a>
                            </template>
                        </div>
                    </div>
                `;
            },
            
            // Event Methods
            toggleTheme() {
                const html = document.documentElement;
                const isDark = html.classList.contains('dark');
                
                if (isDark) {
                    html.classList.remove('dark');
                    html.classList.add('light');
                    console.log('Theme toggled to: light');
                } else {
                    html.classList.remove('light');
                    html.classList.add('dark');
                    console.log('Theme toggled to: dark');
                }
            },
            
            toggleMobileMenu() {
                this.mobileMenuOpen = !this.mobileMenuOpen;
            },
            
            toggleUserMenu() {
                this.userMenuOpen = !this.userMenuOpen;
            },
            
            toggleNotifications() {
                this.notificationsMenuOpen = !this.notificationsMenuOpen;
            },
            
            setNotificationCount(count) {
                this.notificationCount = count;
            },
            
            updateNavigationItems(items) {
                this.navigationItems = items;
            },
            
            // Initialization
            init() {
                console.log('WaveHeadbar initialized with Grove design');
            }
        };
    }
}

// Global registration
if (typeof window !== 'undefined') {
    window.WaveHeadbar = WaveHeadbar;
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = WaveHeadbar;
}