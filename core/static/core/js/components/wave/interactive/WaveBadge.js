/**
 * WaveBadge - Professional badge component with pastel colors for tags/labels
 * Part of HydroML Wave-Inspired Component Library
 * 
 * Features:
 * - Pastel color palette for tags and classification
 * - Multiple variants and sizes
 * - Optional dismiss functionality
 * - Icon support
 * - Accessibility compliant
 * - Theme system integration
 */

class WaveBadge extends BaseComponent {
    constructor() {
        super('WaveBadge');
        
        this.defaultConfig = {
            variant: 'default', // default, success, warning, error, info, custom
            color: null, // override variant with custom pastel color
            size: 'md', // xs, sm, md, lg
            rounded: 'full', // none, sm, md, lg, full
            dismissible: false,
            icon: null,
            iconPosition: 'left', // left, right
            href: null, // makes badge clickable
            target: '_self',
            dot: false, // shows a small dot indicator
            outlined: false // outlined style instead of filled
        };
        
        this.dismissed = false;
    }

    init(element, config = {}) {
        super.init(element, config);
        
        this.textElement = this.element.querySelector('.wave-badge-text');
        this.iconElement = this.element.querySelector('.wave-badge-icon');
        this.dotElement = this.element.querySelector('.wave-badge-dot');
        this.dismissButton = this.element.querySelector('.wave-badge-dismiss');
        
        this.setupEventListeners();
        this.updateState();
        
        return this.getAlpineData();
    }

    getAlpineData() {
        return {
            // State
            dismissed: this.dismissed,
            
            // Computed
            get badgeClasses() {
                if (this.dismissed) return 'hidden';
                
                const base = 'wave-badge inline-flex items-center font-medium transition-all duration-200';
                const variant = this.getVariantClasses();
                const size = this.getSizeClasses();
                const rounded = this.getRoundedClasses();
                const interactive = this.config.href ? 'cursor-pointer hover:opacity-80' : '';
                const outlined = this.config.outlined ? 'border' : '';
                
                return `${base} ${variant} ${size} ${rounded} ${interactive} ${outlined}`.trim();
            },
            
            get containerClasses() {
                return 'wave-badge-container inline-flex items-center';
            },
            
            get showIcon() {
                return this.config.icon && !this.config.dot;
            },
            
            get showDot() {
                return this.config.dot;
            },
            
            get showDismiss() {
                return this.config.dismissible && !this.dismissed;
            },

            // Methods
            getVariantClasses: () => {
                if (this.config.color) {
                    // Custom color - always pastel
                    const outlined = this.config.outlined ? 
                        `text-${this.config.color}-700 bg-${this.config.color}-50 border-${this.config.color}-200` :
                        `text-${this.config.color}-800 bg-${this.config.color}-100`;
                    return outlined;
                }
                
                const variants = this.config.outlined ? {
                    // Outlined variants - subtle borders with light backgrounds
                    default: 'text-gray-700 bg-gray-50 border-gray-200',
                    success: 'text-green-700 bg-green-50 border-green-200',
                    warning: 'text-amber-700 bg-amber-50 border-amber-200',
                    error: 'text-red-700 bg-red-50 border-red-200',
                    info: 'text-blue-700 bg-blue-50 border-blue-200',
                    
                    // Classification colors (pastel)
                    purple: 'text-purple-700 bg-purple-50 border-purple-200',
                    pink: 'text-pink-700 bg-pink-50 border-pink-200',
                    indigo: 'text-indigo-700 bg-indigo-50 border-indigo-200',
                    teal: 'text-teal-700 bg-teal-50 border-teal-200',
                    orange: 'text-orange-700 bg-orange-50 border-orange-200'
                } : {
                    // Filled variants - soft pastel backgrounds
                    default: 'text-gray-800 bg-gray-100',
                    success: 'text-green-800 bg-green-100',
                    warning: 'text-amber-800 bg-amber-100',
                    error: 'text-red-800 bg-red-100',
                    info: 'text-blue-800 bg-blue-100',
                    
                    // Classification colors (pastel)
                    purple: 'text-purple-800 bg-purple-100',
                    pink: 'text-pink-800 bg-pink-100',
                    indigo: 'text-indigo-800 bg-indigo-100',
                    teal: 'text-teal-800 bg-teal-100',
                    orange: 'text-orange-800 bg-orange-100'
                };
                
                return variants[this.config.variant] || variants.default;
            },
            
            getSizeClasses: () => {
                const sizes = {
                    xs: 'px-1.5 py-0.5 text-xs gap-1',
                    sm: 'px-2 py-0.5 text-sm gap-1',
                    md: 'px-2.5 py-1 text-sm gap-1.5',
                    lg: 'px-3 py-1.5 text-base gap-2'
                };
                return sizes[this.config.size] || sizes.md;
            },
            
            getRoundedClasses: () => {
                const rounded = {
                    none: 'rounded-none',
                    sm: 'rounded-sm',
                    md: 'rounded-md',
                    lg: 'rounded-lg',
                    full: 'rounded-full'
                };
                return rounded[this.config.rounded] || rounded.full;
            },

            // Event Handlers
            handleClick: (event) => {
                if (this.config.href) {
                    // Let the link handle navigation
                    this.emit('click', { 
                        event, 
                        variant: this.config.variant,
                        href: this.config.href 
                    });
                } else {
                    // Regular badge click
                    this.emit('click', { 
                        event, 
                        variant: this.config.variant 
                    });
                }
            },
            
            handleDismiss: (event) => {
                event.stopPropagation();
                this.dismiss();
            },
            
            dismiss: () => {
                this.dismissed = true;
                this.emit('dismiss', { 
                    variant: this.config.variant,
                    text: this.getTextContent()
                });
                
                // Animate out
                this.element.style.transition = 'all 0.2s ease-out';
                this.element.style.opacity = '0';
                this.element.style.transform = 'scale(0.95)';
                
                setTimeout(() => {
                    this.element.style.display = 'none';
                }, 200);
            },
            
            restore: () => {
                this.dismissed = false;
                this.element.style.display = '';
                this.element.style.opacity = '1';
                this.element.style.transform = 'scale(1)';
                
                this.emit('restore', { 
                    variant: this.config.variant,
                    text: this.getTextContent()
                });
            },

            // Icon and content management
            getIconHtml: () => {
                if (!this.config.icon) return '';
                
                const sizeClass = this.config.size === 'xs' ? 'w-3 h-3' : 
                                 this.config.size === 'sm' ? 'w-3.5 h-3.5' :
                                 this.config.size === 'lg' ? 'w-5 h-5' : 'w-4 h-4';
                
                return `
                    <svg class="wave-badge-icon ${sizeClass}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        ${this.getIconPath(this.config.icon)}
                    </svg>
                `;
            },
            
            getDotHtml: () => {
                if (!this.config.dot) return '';
                
                const sizeClass = this.config.size === 'xs' ? 'w-1.5 h-1.5' : 
                                 this.config.size === 'sm' ? 'w-2 h-2' :
                                 this.config.size === 'lg' ? 'w-3 h-3' : 'w-2.5 h-2.5';
                
                return `<span class="wave-badge-dot ${sizeClass} rounded-full bg-current opacity-75"></span>`;
            },
            
            getDismissHtml: () => {
                if (!this.config.dismissible) return '';
                
                const sizeClass = this.config.size === 'xs' ? 'w-3 h-3' : 
                                 this.config.size === 'sm' ? 'w-3.5 h-3.5' :
                                 this.config.size === 'lg' ? 'w-5 h-5' : 'w-4 h-4';
                
                return `
                    <button class="wave-badge-dismiss ml-1 hover:opacity-70 focus:outline-none focus:opacity-70 transition-opacity" 
                            aria-label="Remove badge">
                        <svg class="${sizeClass}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                    </button>
                `;
            }
        };
    }

    setupEventListeners() {
        // Handle dismiss button if present
        if (this.dismissButton) {
            this.dismissButton.addEventListener('click', (event) => {
                event.stopPropagation();
                this.dismiss();
            });
        }
        
        // Handle keyboard accessibility for dismissible badges
        if (this.config.dismissible) {
            this.element.addEventListener('keydown', (event) => {
                if (event.key === 'Delete' || event.key === 'Backspace') {
                    event.preventDefault();
                    this.dismiss();
                }
            });
        }
        
        // Make focusable if interactive
        if (this.config.href || this.config.dismissible) {
            this.element.setAttribute('tabindex', '0');
        }
    }

    updateState() {
        // Update link attributes if badge is clickable
        if (this.config.href) {
            if (this.element.tagName !== 'A') {
                // Wrap in link or convert to link
                const link = document.createElement('a');
                link.href = this.config.href;
                link.target = this.config.target;
                link.className = this.element.className;
                link.innerHTML = this.element.innerHTML;
                this.element.parentNode.replaceChild(link, this.element);
                this.element = link;
            } else {
                this.element.href = this.config.href;
                this.element.target = this.config.target;
            }
        }
        
        // Update ARIA attributes
        if (this.config.dismissible) {
            this.element.setAttribute('role', 'button');
            this.element.setAttribute('aria-label', `Badge: ${this.getTextContent()}. Press Delete to remove.`);
        }
    }

    getIconPath(iconName) {
        const icons = {
            check: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>',
            x: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>',
            info: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>',
            warning: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.464 0L4.268 16.5c-.77.833.192 2.5 1.732 2.5z"></path>',
            star: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"></path>',
            tag: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"></path>',
            user: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>',
            database: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4"></path>',
            code: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"></path>'
        };
        
        return icons[iconName] || icons.tag;
    }

    getTextContent() {
        return this.textElement?.textContent || this.element.textContent || '';
    }

    // Public API
    setVariant(variant) {
        this.config.variant = variant;
        this.updateState();
        this.emit('variant-change', { variant });
    }

    setColor(color) {
        this.config.color = color;
        this.updateState();
        this.emit('color-change', { color });
    }

    setText(text) {
        if (this.textElement) {
            this.textElement.textContent = text;
        } else {
            this.element.textContent = text;
        }
        this.emit('text-change', { text });
    }

    setIcon(icon) {
        this.config.icon = icon;
        this.updateState();
        this.emit('icon-change', { icon });
    }

    dismiss() {
        const alpineData = this.getAlpineData();
        alpineData.dismiss();
    }

    restore() {
        const alpineData = this.getAlpineData();
        alpineData.restore();
    }

    isDismissed() {
        return this.dismissed;
    }
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = WaveBadge;
}

// Register with ComponentRegistry if available
if (typeof window !== 'undefined' && window.ComponentRegistry) {
    window.ComponentRegistry.register('WaveBadge', WaveBadge);
}