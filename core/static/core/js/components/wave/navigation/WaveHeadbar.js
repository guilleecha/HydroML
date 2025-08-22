/**
 * WaveHeadbar - Professional navigation header with Grove design
 * Part of HydroML Grove Component Library
 * 
 * Enhanced version with two-row layout support for Enhanced Grove Headbar Epic
 */

class WaveHeadbar {
    static createAlpineData(config = {}) {
        // Enhanced configuration for two-row layout
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
            navigationItems: [],
            // Two-row layout options
            layoutMode: 'two-row', // 'single-row', 'two-row'
            showBreadcrumbs: true,
            breadcrumbStyle: 'character-based', // '@username', etc.
            showTabCounts: true,
            tabCountsData: {
                workspaces: 8,
                datasources: 15,
                experiments: 2
            },
            currentBreadcrumb: '@demo-user'
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
            quickActionsOpen: false,
            darkMode: false,
            
            // Computed Properties
            get headbarClasses() {
                const baseClasses = ['wave-headbar', 'w-full', 'transition-all', 'duration-200'];
                
                if (this.layoutMode === 'two-row') {
                    return [
                        ...baseClasses,
                        'two-row', 'flex', 'flex-col', 'sticky', 'top-0', 'z-50'
                    ].join(' ');
                }
                
                return [
                    ...baseClasses,
                    'border-b', 'border-gray-200', 'dark:border-gray-700',
                    'bg-white', 'dark:bg-gray-900', 'sticky', 'top-0', 'z-50',
                    'px-4', 'py-3', 'flex', 'items-center', 'justify-between'
                ].join(' ');
            },
            
            // HTML Generation Methods for Two-Row Layout
            getTwoRowHtml() {
                if (this.layoutMode !== 'two-row') {
                    return this.getSingleRowHtml();
                }
                
                return `
                    <!-- Primary Row (Breadcrumbs) -->
                    <div class="wave-headbar-primary-row">
                        ${this.getPrimaryRowHtml()}
                    </div>
                    
                    <!-- Secondary Row (Navigation) -->
                    <div class="wave-headbar-secondary-row">
                        ${this.getSecondaryRowHtml()}
                    </div>
                `;
            },
            
            getPrimaryRowHtml() {
                return `
                    <div class="wave-headbar-primary-left">
                        <!-- Mobile menu button -->
                        <button @click="mobileMenuOpen = !mobileMenuOpen" 
                                class="md:hidden p-2 rounded-md text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-200 dark:hover:bg-gray-800">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
                            </svg>
                        </button>
                        
                        <!-- Grove Logo -->
                        <a href="/dashboard/" class="wave-headbar-primary-logo">
                            <svg class="w-12 h-12 text-gray-600 dark:text-gray-300" fill="currentColor" viewBox="0 0 24 24">
                                <path d="M12 2L13.09 8.26L20 9L13.09 9.74L12 16L10.91 9.74L4 9L10.91 8.26L12 2Z"/>
                            </svg>
                        </a>
                        
                        <!-- Enhanced Breadcrumbs -->
                        <div class="wave-headbar-breadcrumbs">
                            <span class="wave-headbar-breadcrumb-char">@</span>
                            <span class="wave-headbar-breadcrumb-user">${this.userName}</span>
                        </div>
                    </div>

                    <div class="wave-headbar-primary-right">
                        <!-- Search Bar -->
                        <div class="hidden md:block">
                            <div class="relative">
                                <input type="text" 
                                       placeholder="Search workspaces..."
                                       class="w-64 px-3 py-1.5 pl-8 text-sm bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                                <svg class="absolute left-2.5 top-2 w-4 h-4 text-gray-500 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                                </svg>
                            </div>
                        </div>

                        <!-- Quick Actions Dropdown -->
                        <div class="relative">
                            <button @click="quickActionsOpen = !quickActionsOpen" 
                                    class="flex items-center p-2 text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-200 dark:hover:bg-gray-800 rounded-md transition-colors">
                                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
                                </svg>
                            </button>
                        </div>

                        <!-- Theme Toggle -->
                        <button @click="toggleTheme()" 
                                class="p-2 text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-200 dark:hover:bg-gray-800 rounded-md transition-colors">
                            <svg x-show="!darkMode" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"></path>
                            </svg>
                            <svg x-show="darkMode" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"></path>
                            </svg>
                        </button>

                        <!-- User Avatar/Menu -->
                        <div class="relative">
                            <button @click="userMenuOpen = !userMenuOpen" 
                                    class="flex items-center p-1 text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white rounded-md transition-colors">
                                <div class="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                                    <span class="text-white font-medium text-sm">${this.userInitials}</span>
                                </div>
                                <svg class="w-3 h-3 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                                </svg>
                            </button>
                        </div>
                    </div>
                `;
            },
            
            getSecondaryRowHtml() {
                return `
                    <nav class="wave-headbar-nav">
                        <a href="#" class="wave-headbar-nav-item active">
                            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2V7"></path>
                            </svg>
                            Dashboard
                        </a>
                        
                        <a href="#" class="wave-headbar-nav-item">
                            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-2m-2 0H7m14 0V9a2 2 0 00-2-2H9a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2z"></path>
                            </svg>
                            Workspaces
                            <span class="wave-headbar-count-badge" x-text="tabCountsData.workspaces"></span>
                        </a>
                        
                        <a href="#" class="wave-headbar-nav-item">
                            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4"></path>
                            </svg>
                            Data Sources
                            <span class="wave-headbar-count-badge" x-text="tabCountsData.datasources"></span>
                        </a>
                        
                        <a href="#" class="wave-headbar-nav-item">
                            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
                            </svg>
                            Experiments
                            <span class="wave-headbar-count-badge" x-text="tabCountsData.experiments"></span>
                        </a>
                    </nav>
                `;
            },

            // Legacy single-row method for backward compatibility
            getLogoHtml() {
                return `
                    <a href="/dashboard/" class="flex items-center space-x-2 flex-shrink-0">
                        <img src="${this.logoSrc}" alt="${this.logoText}" class="h-8 w-8">
                        <span class="font-semibold text-gray-900 dark:text-white">${this.logoText}</span>
                    </a>
                `;
            },
            
            getSingleRowHtml() {
                return `
                    <div class="flex items-center justify-between w-full">
                        ${this.getLogoHtml()}
                        <div class="flex items-center space-x-4">
                            ${this.getSearchHtml()}
                            ${this.getThemeToggleHtml()}
                            ${this.getNotificationsHtml()}
                            ${this.getUserMenuHtml()}
                        </div>
                    </div>
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