/**
 * WaveTabs - Professional tab navigation component with responsive behavior
 * Part of HydroML Wave-Inspired Component Library
 * 
 * Features:
 * - Monochromatic design with subtle highlights
 * - Keyboard navigation (arrow keys, home/end)
 * - Responsive behavior with overflow handling
 * - Icon support and badge integration
 * - Accessibility compliant (ARIA attributes)
 * - Theme system integration
 * - URL synchronization (optional)
 */

class WaveTabs extends BaseComponent {
    constructor() {
        super('WaveTabs');
        
        this.defaultConfig = {
            // Tab configuration
            tabs: [],
            activeTab: null,
            defaultTab: 0,
            
            // Styling variants
            variant: 'default', // default, pills, underline, card
            size: 'md', // sm, md, lg
            alignment: 'left', // left, center, right, justified
            
            // Features
            closeable: false,
            scrollable: true,
            animated: true,
            lazy: false, // lazy load tab content
            
            // URL integration
            urlSync: false,
            urlParam: 'tab',
            
            // Accessibility
            orientation: 'horizontal', // horizontal, vertical
            
            // Responsive
            stackOnMobile: false,
            collapseToDropdown: false
        };
        
        this.tabElements = new Map();
        this.panelElements = new Map();
        this.focusedTabIndex = 0;
    }

    init(element, config = {}) {
        super.init(element, config);
        
        this.tabList = this.element.querySelector('[role="tablist"]');
        this.tabContainer = this.element.querySelector('.wave-tabs-container');
        this.panelContainer = this.element.querySelector('.wave-tab-panels');
        
        this.setupTabs();
        this.setupEventListeners();
        this.setupAccessibility();
        this.setActiveTab(this.config.activeTab || this.config.defaultTab);
        
        return this.getAlpineData();
    }

    getAlpineData() {
        return {
            // State
            activeTab: this.config.activeTab,
            focusedTab: this.focusedTabIndex,
            tabs: this.config.tabs,
            
            // Computed
            get tabListClasses() {
                const base = 'wave-tabs-list flex';
                const variant = this.getVariantClasses();
                const size = this.getSizeClasses();
                const alignment = this.getAlignmentClasses();
                const orientation = this.config.orientation === 'vertical' ? 'flex-col' : 'flex-row';
                const scrollable = this.config.scrollable ? 'overflow-x-auto' : '';
                
                return `${base} ${variant} ${size} ${alignment} ${orientation} ${scrollable}`.trim();
            },
            
            get containerClasses() {
                const base = 'wave-tabs-container';
                const orientation = this.config.orientation === 'vertical' ? 'flex' : 'block';
                const responsive = this.config.stackOnMobile ? 'wave-tabs-responsive' : '';
                
                return `${base} ${orientation} ${responsive}`.trim();
            },

            // Methods
            getVariantClasses: () => {
                const variants = {
                    default: 'border-b border-gray-200',
                    pills: 'bg-gray-100 rounded-lg p-1 gap-1',
                    underline: 'border-b-2 border-transparent',
                    card: 'border border-gray-200 rounded-lg bg-white'
                };
                return variants[this.config.variant] || variants.default;
            },
            
            getSizeClasses: () => {
                const sizes = {
                    sm: 'text-sm',
                    md: 'text-base',
                    lg: 'text-lg'
                };
                return sizes[this.config.size] || sizes.md;
            },
            
            getAlignmentClasses: () => {
                const alignments = {
                    left: 'justify-start',
                    center: 'justify-center',
                    right: 'justify-end',
                    justified: 'justify-between'
                };
                return alignments[this.config.alignment] || alignments.left;
            },
            
            getTabClasses: (tab, index) => {
                const base = 'wave-tab inline-flex items-center justify-center gap-2 font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500';
                const active = this.activeTab === index || this.activeTab === tab.id;
                const disabled = tab.disabled;
                
                let variant = '';
                switch (this.config.variant) {
                    case 'pills':
                        variant = active ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50';
                        break;
                    case 'underline':
                        variant = active ? 'border-b-2 border-gray-900 text-gray-900' : 'text-gray-600 hover:text-gray-900 hover:border-gray-300';
                        break;
                    case 'card':
                        variant = active ? 'bg-white border-b-2 border-gray-900 text-gray-900' : 'text-gray-600 hover:text-gray-900 bg-gray-50';
                        break;
                    default:
                        variant = active ? 'border-b-2 border-gray-900 text-gray-900' : 'text-gray-600 hover:text-gray-900 border-b-2 border-transparent';
                }
                
                const size = this.getTabSizeClasses();
                const disabledClass = disabled ? 'opacity-50 cursor-not-allowed pointer-events-none' : 'cursor-pointer';
                
                return `${base} ${variant} ${size} ${disabledClass}`.trim();
            },
            
            getTabSizeClasses: () => {
                const sizes = {
                    sm: 'px-3 py-2 text-sm',
                    md: 'px-4 py-3 text-base',
                    lg: 'px-6 py-4 text-lg'
                };
                return sizes[this.config.size] || sizes.md;
            },
            
            getPanelClasses: (tab, index) => {
                const base = 'wave-tab-panel';
                const active = this.activeTab === index || this.activeTab === tab.id;
                const animated = this.config.animated ? 'transition-opacity duration-200' : '';
                const visible = active ? 'opacity-100' : 'opacity-0 hidden';
                
                return `${base} ${animated} ${visible}`.trim();
            },

            // Event Handlers
            handleTabClick: (tab, index, event) => {
                event.preventDefault();
                
                if (tab.disabled) return;
                
                this.setActiveTab(index);
                this.focusedTabIndex = index;
                
                this.emit('tab-click', { 
                    tab, 
                    index, 
                    previousTab: this.activeTab 
                });
            },
            
            handleTabKeydown: (event) => {
                const tabs = this.config.tabs.filter(tab => !tab.disabled);
                const currentIndex = tabs.findIndex((tab, i) => 
                    i === this.focusedTabIndex || tab.id === this.activeTab
                );
                
                let newIndex = currentIndex;
                
                switch (event.key) {
                    case 'ArrowLeft':
                    case 'ArrowUp':
                        event.preventDefault();
                        newIndex = currentIndex > 0 ? currentIndex - 1 : tabs.length - 1;
                        break;
                    case 'ArrowRight':
                    case 'ArrowDown':
                        event.preventDefault();
                        newIndex = currentIndex < tabs.length - 1 ? currentIndex + 1 : 0;
                        break;
                    case 'Home':
                        event.preventDefault();
                        newIndex = 0;
                        break;
                    case 'End':
                        event.preventDefault();
                        newIndex = tabs.length - 1;
                        break;
                    case 'Enter':
                    case ' ':
                        event.preventDefault();
                        this.setActiveTab(this.focusedTabIndex);
                        return;
                }
                
                if (newIndex !== currentIndex) {
                    this.focusedTabIndex = newIndex;
                    this.focusTab(newIndex);
                }
            },
            
            handleTabClose: (tab, index, event) => {
                event.stopPropagation();
                
                if (!this.config.closeable || tab.required) return;
                
                this.closeTab(index);
                
                this.emit('tab-close', { 
                    tab, 
                    index 
                });
            },

            // Tab management
            setActiveTab: (tabIndex) => {
                const tab = typeof tabIndex === 'string' ? 
                    this.config.tabs.find(t => t.id === tabIndex) : 
                    this.config.tabs[tabIndex];
                
                if (!tab || tab.disabled) return;
                
                const index = this.config.tabs.indexOf(tab);
                const previousTab = this.activeTab;
                
                this.activeTab = index;
                this.focusedTabIndex = index;
                
                // Update URL if sync enabled
                if (this.config.urlSync) {
                    this.updateURL(tab.id || index);
                }
                
                // Lazy load content if needed
                if (this.config.lazy && tab.lazyLoad && !tab.loaded) {
                    this.loadTabContent(tab, index);
                }
                
                this.emit('tab-change', { 
                    tab, 
                    index, 
                    previousTab 
                });
            },
            
            addTab: (tab, index = null) => {
                const insertIndex = index !== null ? index : this.config.tabs.length;
                this.config.tabs.splice(insertIndex, 0, tab);
                
                this.setupTabs();
                
                this.emit('tab-add', { 
                    tab, 
                    index: insertIndex 
                });
            },
            
            removeTab: (index) => {
                if (this.config.tabs.length <= 1) return;
                
                const tab = this.config.tabs[index];
                if (!tab || tab.required) return;
                
                this.config.tabs.splice(index, 1);
                
                // Adjust active tab if necessary
                if (this.activeTab === index) {
                    const newActiveIndex = Math.min(index, this.config.tabs.length - 1);
                    this.setActiveTab(newActiveIndex);
                } else if (this.activeTab > index) {
                    this.activeTab--;
                }
                
                this.setupTabs();
                
                this.emit('tab-remove', { 
                    tab, 
                    index 
                });
            },
            
            closeTab: (index) => {
                this.removeTab(index);
            },

            // Content management
            getTabContent: (tab, index) => {
                if (tab.content) return tab.content;
                if (tab.template) return this.renderTemplate(tab.template, tab.data);
                if (tab.component) return this.renderComponent(tab.component, tab.props);
                
                return `<div class="p-4 text-gray-500">No content available for tab: ${tab.title}</div>`;
            },
            
            getTabIcon: (tab) => {
                if (!tab.icon) return '';
                
                const sizeClass = this.config.size === 'sm' ? 'w-4 h-4' : 
                                 this.config.size === 'lg' ? 'w-6 h-6' : 'w-5 h-5';
                
                return `
                    <svg class="wave-tab-icon ${sizeClass}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        ${this.getIconPath(tab.icon)}
                    </svg>
                `;
            },
            
            getTabBadge: (tab) => {
                if (!tab.badge) return '';
                
                const badgeClasses = 'wave-tab-badge ml-2 px-1.5 py-0.5 text-xs rounded-full bg-gray-200 text-gray-700';
                
                return `<span class="${badgeClasses}">${tab.badge}</span>`;
            },
            
            getCloseButton: (tab) => {
                if (!this.config.closeable || tab.required) return '';
                
                const sizeClass = this.config.size === 'sm' ? 'w-3 h-3' : 'w-4 h-4';
                
                return `
                    <button class="wave-tab-close ml-2 hover:text-red-600 focus:outline-none focus:text-red-600 transition-colors"
                            aria-label="Close tab">
                        <svg class="${sizeClass}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                    </button>
                `;
            }
        };
    }

    setupTabs() {
        if (!this.tabList || !this.config.tabs.length) return;
        
        // Clear existing tabs
        this.tabElements.clear();
        this.panelElements.clear();
        
        // Render tab list
        let tabListHTML = '';
        let panelHTML = '';
        
        this.config.tabs.forEach((tab, index) => {
            const tabId = tab.id || `tab-${index}`;
            const panelId = tab.panelId || `panel-${index}`;
            
            // Tab button
            tabListHTML += `
                <button role="tab" 
                        id="${tabId}"
                        class="${this.getTabClasses(tab, index)}"
                        aria-controls="${panelId}"
                        aria-selected="${this.activeTab === index}"
                        tabindex="${this.activeTab === index ? '0' : '-1'}"
                        ${tab.disabled ? 'disabled' : ''}>
                    ${this.getTabIcon(tab)}
                    <span class="wave-tab-title">${tab.title}</span>
                    ${this.getTabBadge(tab)}
                    ${this.getCloseButton(tab)}
                </button>
            `;
            
            // Tab panel
            panelHTML += `
                <div role="tabpanel"
                     id="${panelId}"
                     class="${this.getPanelClasses(tab, index)}"
                     aria-labelledby="${tabId}"
                     tabindex="0">
                    ${this.getTabContent(tab, index)}
                </div>
            `;
        });
        
        this.tabList.innerHTML = tabListHTML;
        if (this.panelContainer) {
            this.panelContainer.innerHTML = panelHTML;
        }
    }

    setupEventListeners() {
        if (!this.tabList) return;
        
        // Tab click events
        this.tabList.addEventListener('click', (event) => {
            const tabButton = event.target.closest('[role="tab"]');
            if (!tabButton) return;
            
            const index = Array.from(this.tabList.children).indexOf(tabButton);
            const tab = this.config.tabs[index];
            
            if (event.target.closest('.wave-tab-close')) {
                this.handleTabClose(tab, index, event);
            } else {
                this.handleTabClick(tab, index, event);
            }
        });
        
        // Keyboard navigation
        this.tabList.addEventListener('keydown', (event) => {
            this.handleTabKeydown(event);
        });
        
        // URL synchronization
        if (this.config.urlSync) {
            window.addEventListener('popstate', () => {
                this.syncFromURL();
            });
        }
    }

    setupAccessibility() {
        if (this.tabList) {
            this.tabList.setAttribute('role', 'tablist');
            this.tabList.setAttribute('aria-orientation', this.config.orientation);
        }
    }

    focusTab(index) {
        const tabButton = this.tabList?.children[index];
        if (tabButton) {
            tabButton.focus();
        }
    }

    updateURL(tabId) {
        if (!this.config.urlSync) return;
        
        const url = new URL(window.location);
        url.searchParams.set(this.config.urlParam, tabId);
        window.history.pushState({}, '', url);
    }

    syncFromURL() {
        if (!this.config.urlSync) return;
        
        const params = new URLSearchParams(window.location.search);
        const tabId = params.get(this.config.urlParam);
        
        if (tabId) {
            this.setActiveTab(tabId);
        }
    }

    getIconPath(iconName) {
        const icons = {
            home: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path>',
            chart: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>',
            settings: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>',
            user: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>',
            database: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4"></path>'
        };
        
        return icons[iconName] || icons.home;
    }

    // Public API
    getActiveTab() {
        return {
            tab: this.config.tabs[this.activeTab],
            index: this.activeTab
        };
    }

    goToTab(identifier) {
        this.setActiveTab(identifier);
    }

    nextTab() {
        const nextIndex = (this.activeTab + 1) % this.config.tabs.length;
        this.setActiveTab(nextIndex);
    }

    previousTab() {
        const prevIndex = this.activeTab === 0 ? this.config.tabs.length - 1 : this.activeTab - 1;
        this.setActiveTab(prevIndex);
    }

    addTab(tab, index = null) {
        const alpineData = this.getAlpineData();
        alpineData.addTab(tab, index);
    }

    removeTab(index) {
        const alpineData = this.getAlpineData();
        alpineData.removeTab(index);
    }

    updateTab(index, updates) {
        if (this.config.tabs[index]) {
            Object.assign(this.config.tabs[index], updates);
            this.setupTabs();
            this.emit('tab-update', { index, updates });
        }
    }

    getTabCount() {
        return this.config.tabs.length;
    }
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = WaveTabs;
}

// Register with ComponentRegistry if available
if (typeof window !== 'undefined' && window.ComponentRegistry) {
    window.ComponentRegistry.register('WaveTabs', WaveTabs);
}