/**
 * WaveButton - Professional button component with monochromatic design
 * Part of HydroML Wave-Inspired Component Library
 * 
 * Features:
 * - Monochromatic design (white, black, grays, subtle accents)
 * - Multiple variants and sizes
 * - Loading states with spinner
 * - Icon support
 * - Accessibility compliant
 * - Theme system integration
 */

class WaveButton extends BaseComponent {
    constructor() {
        super('WaveButton');
        
        this.defaultConfig = {
            variant: 'primary', // primary, secondary, ghost, outline, danger
            size: 'md', // xs, sm, md, lg, xl
            disabled: false,
            loading: false,
            icon: null,
            iconPosition: 'left', // left, right, only
            fullWidth: false,
            rounded: 'md', // none, sm, md, lg, full
            href: null, // if provided, renders as link
            target: '_self',
            type: 'button' // button, submit, reset
        };
        
        this.loadingSpinner = `
            <svg class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
        `;
    }

    init(element, config = {}) {
        super.init(element, config);
        
        this.buttonElement = this.element.tagName === 'BUTTON' ? this.element : this.element.querySelector('button');
        this.linkElement = this.element.tagName === 'A' ? this.element : this.element.querySelector('a');
        this.textElement = this.element.querySelector('.wave-button-text');
        this.iconElement = this.element.querySelector('.wave-button-icon');
        this.loadingElement = this.element.querySelector('.wave-button-loading');
        
        this.setupEventListeners();
        this.updateState();
        
        return this.getAlpineData();
    }

    getAlpineData() {
        return {
            // State
            loading: this.config.loading,
            disabled: this.config.disabled,
            
            // Computed
            get buttonClasses() {
                const base = 'wave-button inline-flex items-center justify-center font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed';
                const variant = this.getVariantClasses();
                const size = this.getSizeClasses();
                const rounded = this.getRoundedClasses();
                const width = this.config.fullWidth ? 'w-full' : '';
                const state = this.loading ? 'cursor-wait' : '';
                
                return `${base} ${variant} ${size} ${rounded} ${width} ${state}`.trim();
            },
            
            get isDisabled() {
                return this.disabled || this.loading;
            },
            
            get showIcon() {
                return this.config.icon && this.config.iconPosition !== 'only' && !this.loading;
            },
            
            get showText() {
                return this.config.iconPosition !== 'only';
            },
            
            get showLoading() {
                return this.loading;
            },

            // Methods
            getVariantClasses: () => {
                const variants = {
                    // Primary - Dark gray with white text (professional)
                    primary: 'bg-gray-800 text-white border border-gray-800 hover:bg-gray-900 focus:ring-gray-500 active:bg-gray-900',
                    
                    // Secondary - Light gray with dark text
                    secondary: 'bg-gray-200 text-gray-800 border border-gray-300 hover:bg-gray-300 focus:ring-gray-400 active:bg-gray-300',
                    
                    // Ghost - No background, subtle hover
                    ghost: 'bg-transparent text-gray-700 border border-transparent hover:bg-gray-100 focus:ring-gray-400 active:bg-gray-200',
                    
                    // Outline - White background with gray border
                    outline: 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50 focus:ring-gray-400 active:bg-gray-100',
                    
                    // Danger - Muted red (not bright)
                    danger: 'bg-red-600 text-white border border-red-600 hover:bg-red-700 focus:ring-red-500 active:bg-red-700'
                };
                return variants[this.config.variant] || variants.primary;
            },
            
            getSizeClasses: () => {
                const sizes = {
                    xs: 'px-2 py-1 text-xs gap-1',
                    sm: 'px-3 py-1.5 text-sm gap-1.5',
                    md: 'px-4 py-2 text-base gap-2',
                    lg: 'px-6 py-3 text-lg gap-2.5',
                    xl: 'px-8 py-4 text-xl gap-3'
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
                return rounded[this.config.rounded] || rounded.md;
            },

            // Event Handlers
            handleClick: (event) => {
                if (this.isDisabled) {
                    event.preventDefault();
                    event.stopPropagation();
                    return false;
                }
                
                this.emit('click', { 
                    event, 
                    variant: this.config.variant,
                    disabled: this.disabled,
                    loading: this.loading 
                });
                
                // Handle special button types
                if (this.config.type === 'submit') {
                    this.emit('submit', { event });
                }
            },
            
            setLoading: (loading) => {
                this.loading = loading;
                this.emit('loading-change', { loading });
            },
            
            setDisabled: (disabled) => {
                this.disabled = disabled;
                this.emit('disabled-change', { disabled });
            },
            
            // Icon and content management
            getIconHtml: () => {
                if (!this.config.icon) return '';
                
                return `
                    <svg class="wave-button-icon w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        ${this.getIconPath(this.config.icon)}
                    </svg>
                `;
            },
            
            getLoadingHtml: () => {
                return `<span class="wave-button-loading">${this.loadingSpinner}</span>`;
            }
        };
    }

    setupEventListeners() {
        // Handle click delegation
        this.element.addEventListener('click', (event) => {
            if (this.config.disabled || this.config.loading) {
                event.preventDefault();
                event.stopPropagation();
                return false;
            }
        });
        
        // Handle keyboard accessibility
        this.element.addEventListener('keydown', (event) => {
            if (event.key === 'Enter' || event.key === ' ') {
                if (!this.config.disabled && !this.config.loading) {
                    event.preventDefault();
                    this.element.click();
                }
            }
        });
    }

    updateState() {
        // Update button/link attributes
        const targetElement = this.buttonElement || this.linkElement;
        if (targetElement) {
            if (this.buttonElement) {
                this.buttonElement.type = this.config.type;
                this.buttonElement.disabled = this.config.disabled || this.config.loading;
            }
            
            if (this.linkElement && this.config.href) {
                this.linkElement.href = this.config.href;
                this.linkElement.target = this.config.target;
                
                // Prevent click if disabled/loading
                if (this.config.disabled || this.config.loading) {
                    this.linkElement.setAttribute('aria-disabled', 'true');
                    this.linkElement.style.pointerEvents = 'none';
                } else {
                    this.linkElement.removeAttribute('aria-disabled');
                    this.linkElement.style.pointerEvents = '';
                }
            }
        }
        
        // Update ARIA attributes
        this.element.setAttribute('role', 'button');
        this.element.setAttribute('tabindex', (this.config.disabled || this.config.loading) ? '-1' : '0');
        this.element.setAttribute('aria-disabled', (this.config.disabled || this.config.loading).toString());
        
        if (this.config.loading) {
            this.element.setAttribute('aria-busy', 'true');
        } else {
            this.element.removeAttribute('aria-busy');
        }
    }

    getIconPath(iconName) {
        const icons = {
            plus: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>',
            edit: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>',
            trash: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>',
            save: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3-3-3m3-6v10"></path>',
            check: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>',
            x: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>',
            arrow: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6"></path>',
            download: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>',
            upload: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>',
            settings: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>'
        };
        
        return icons[iconName] || icons.arrow;
    }

    // Public API
    setVariant(variant) {
        this.config.variant = variant;
        this.updateState();
        this.emit('variant-change', { variant });
    }

    setSize(size) {
        this.config.size = size;
        this.updateState();
        this.emit('size-change', { size });
    }

    setLoading(loading) {
        this.config.loading = loading;
        this.updateState();
        this.emit('loading-change', { loading });
    }

    setDisabled(disabled) {
        this.config.disabled = disabled;
        this.updateState();
        this.emit('disabled-change', { disabled });
    }

    setIcon(icon, position = 'left') {
        this.config.icon = icon;
        this.config.iconPosition = position;
        this.updateState();
        this.emit('icon-change', { icon, position });
    }

    click() {
        if (!this.config.disabled && !this.config.loading) {
            this.element.click();
        }
    }
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = WaveButton;
}

// Register with ComponentRegistry if available
if (typeof window !== 'undefined' && window.ComponentRegistry) {
    window.ComponentRegistry.register('WaveButton', WaveButton);
}