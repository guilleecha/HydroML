/**
 * WaveModal - Professional modal component with focus management and accessibility
 * Part of HydroML Wave-Inspired Component Library
 * 
 * Features:
 * - Monochromatic design with subtle backdrop
 * - Focus trap and keyboard navigation
 * - Multiple sizes and positions
 * - Accessibility compliant (ARIA, focus management)
 * - Animation and transition support
 * - Scrollable content handling
 * - Theme system integration
 */

class WaveModal extends BaseComponent {
    constructor() {
        super('WaveModal');
        
        this.defaultConfig = {
            // Modal configuration
            size: 'md', // xs, sm, md, lg, xl, full
            position: 'center', // center, top, bottom
            backdrop: 'blur', // blur, dark, light, none
            
            // Behavior
            closeable: true,
            closeOnBackdrop: true,
            closeOnEscape: true,
            scrollable: true,
            centered: true,
            
            // Animation
            animated: true,
            animationDuration: 200,
            
            // Focus management
            focusTrap: true,
            autoFocus: true,
            returnFocus: true,
            
            // ARIA
            role: 'dialog',
            ariaLabelledBy: null,
            ariaDescribedBy: null
        };
        
        this.isOpen = false;
        this.previousActiveElement = null;
        this.focusableElements = [];
        this.currentFocusIndex = 0;
    }

    init(element, config = {}) {
        super.init(element, config);
        
        this.modalElement = this.element.querySelector('.wave-modal');
        this.backdropElement = this.element.querySelector('.wave-modal-backdrop');
        this.contentElement = this.element.querySelector('.wave-modal-content');
        this.headerElement = this.element.querySelector('.wave-modal-header');
        this.bodyElement = this.element.querySelector('.wave-modal-body');
        this.footerElement = this.element.querySelector('.wave-modal-footer');
        this.closeButton = this.element.querySelector('.wave-modal-close');
        
        this.setupEventListeners();
        this.setupAccessibility();
        
        return this.getAlpineData();
    }

    getAlpineData() {
        return {
            // State
            isOpen: this.isOpen,
            animating: false,
            
            // Computed
            get modalClasses() {
                const base = 'wave-modal fixed inset-0 z-50 flex items-center justify-center p-4';
                const position = this.getPositionClasses();
                const visible = this.isOpen ? 'block' : 'hidden';
                
                return `${base} ${position} ${visible}`.trim();
            },
            
            get backdropClasses() {
                const base = 'wave-modal-backdrop fixed inset-0 transition-opacity';
                const variant = this.getBackdropClasses();
                const visible = this.isOpen ? 'opacity-100' : 'opacity-0';
                
                return `${base} ${variant} ${visible}`.trim();
            },
            
            get contentClasses() {
                const base = 'wave-modal-content relative bg-white rounded-lg shadow-xl max-h-full flex flex-col';
                const size = this.getSizeClasses();
                const animated = this.config.animated ? 'transition-all duration-200' : '';
                const transform = this.isOpen ? 'scale-100 opacity-100' : 'scale-95 opacity-0';
                
                return `${base} ${size} ${animated} ${transform}`.trim();
            },

            // Methods
            getPositionClasses: () => {
                const positions = {
                    center: 'items-center justify-center',
                    top: 'items-start justify-center pt-16',
                    bottom: 'items-end justify-center pb-16'
                };
                return positions[this.config.position] || positions.center;
            },
            
            getBackdropClasses: () => {
                const backdrops = {
                    blur: 'bg-gray-900 bg-opacity-75 backdrop-blur-sm',
                    dark: 'bg-gray-900 bg-opacity-75',
                    light: 'bg-gray-500 bg-opacity-50',
                    none: 'bg-transparent'
                };
                return backdrops[this.config.backdrop] || backdrops.blur;
            },
            
            getSizeClasses: () => {
                const sizes = {
                    xs: 'max-w-xs w-full',
                    sm: 'max-w-sm w-full',
                    md: 'max-w-md w-full',
                    lg: 'max-w-lg w-full',
                    xl: 'max-w-xl w-full',
                    '2xl': 'max-w-2xl w-full',
                    '4xl': 'max-w-4xl w-full',
                    full: 'max-w-full w-full h-full m-0 rounded-none'
                };
                return sizes[this.config.size] || sizes.md;
            },

            // Modal controls
            open: () => {
                if (this.isOpen) return;
                
                this.previousActiveElement = document.activeElement;
                this.isOpen = true;
                this.animating = true;
                
                // Add to DOM and setup
                document.body.appendChild(this.element);
                document.body.style.overflow = 'hidden';
                
                // Setup focus trap
                if (this.config.focusTrap) {
                    this.setupFocusTrap();
                }
                
                // Auto focus
                if (this.config.autoFocus) {
                    this.focusFirstElement();
                }
                
                // Animation
                if (this.config.animated) {
                    setTimeout(() => {
                        this.animating = false;
                    }, this.config.animationDuration);
                }
                
                this.emit('open', { modal: this });
            },
            
            close: () => {
                if (!this.isOpen || !this.config.closeable) return;
                
                this.animating = true;
                
                // Return focus
                if (this.config.returnFocus && this.previousActiveElement) {
                    this.previousActiveElement.focus();
                }
                
                // Animation then cleanup
                if (this.config.animated) {
                    setTimeout(() => {
                        this.cleanup();
                    }, this.config.animationDuration);
                } else {
                    this.cleanup();
                }
                
                this.emit('close', { modal: this });
            },
            
            cleanup: () => {
                this.isOpen = false;
                this.animating = false;
                
                // Remove from DOM
                if (this.element.parentNode) {
                    this.element.parentNode.removeChild(this.element);
                }
                
                // Restore body scroll
                document.body.style.overflow = '';
                
                // Clear focus trap
                this.focusableElements = [];
                this.currentFocusIndex = 0;
            },
            
            toggle: () => {
                if (this.isOpen) {
                    this.close();
                } else {
                    this.open();
                }
            },

            // Event handlers
            handleBackdropClick: (event) => {
                if (event.target === this.modalElement && this.config.closeOnBackdrop) {
                    this.close();
                }
            },
            
            handleKeydown: (event) => {
                if (!this.isOpen) return;
                
                switch (event.key) {
                    case 'Escape':
                        if (this.config.closeOnEscape) {
                            event.preventDefault();
                            this.close();
                        }
                        break;
                    case 'Tab':
                        if (this.config.focusTrap) {
                            this.handleTabNavigation(event);
                        }
                        break;
                }
            },
            
            handleTabNavigation: (event) => {
                if (this.focusableElements.length === 0) return;
                
                const isShiftTab = event.shiftKey;
                
                if (isShiftTab) {
                    // Shift + Tab (backwards)
                    if (this.currentFocusIndex <= 0) {
                        event.preventDefault();
                        this.currentFocusIndex = this.focusableElements.length - 1;
                        this.focusableElements[this.currentFocusIndex].focus();
                    } else {
                        this.currentFocusIndex--;
                    }
                } else {
                    // Tab (forwards)
                    if (this.currentFocusIndex >= this.focusableElements.length - 1) {
                        event.preventDefault();
                        this.currentFocusIndex = 0;
                        this.focusableElements[this.currentFocusIndex].focus();
                    } else {
                        this.currentFocusIndex++;
                    }
                }
            },

            // Focus management
            setupFocusTrap: () => {
                this.focusableElements = this.element.querySelectorAll(
                    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
                );
                this.focusableElements = Array.from(this.focusableElements).filter(
                    el => !el.disabled && el.offsetParent !== null
                );
            },
            
            focusFirstElement: () => {
                if (this.focusableElements.length > 0) {
                    this.focusableElements[0].focus();
                    this.currentFocusIndex = 0;
                } else if (this.contentElement) {
                    this.contentElement.focus();
                }
            },
            
            focusLastElement: () => {
                if (this.focusableElements.length > 0) {
                    const lastIndex = this.focusableElements.length - 1;
                    this.focusableElements[lastIndex].focus();
                    this.currentFocusIndex = lastIndex;
                }
            },

            // Content management
            setTitle: (title) => {
                const titleElement = this.headerElement?.querySelector('.wave-modal-title');
                if (titleElement) {
                    titleElement.textContent = title;
                }
            },
            
            setContent: (content) => {
                if (this.bodyElement) {
                    if (typeof content === 'string') {
                        this.bodyElement.innerHTML = content;
                    } else {
                        this.bodyElement.innerHTML = '';
                        this.bodyElement.appendChild(content);
                    }
                }
            },
            
            setFooter: (footer) => {
                if (this.footerElement) {
                    if (typeof footer === 'string') {
                        this.footerElement.innerHTML = footer;
                    } else {
                        this.footerElement.innerHTML = '';
                        this.footerElement.appendChild(footer);
                    }
                }
            }
        };
    }

    setupEventListeners() {
        // Close button
        if (this.closeButton) {
            this.closeButton.addEventListener('click', (event) => {
                event.preventDefault();
                this.close();
            });
        }
        
        // Backdrop click
        this.element.addEventListener('click', (event) => {
            if (event.target === this.modalElement && this.config.closeOnBackdrop) {
                this.close();
            }
        });
        
        // Global keyboard events
        document.addEventListener('keydown', (event) => {
            this.handleKeydown(event);
        });
    }

    setupAccessibility() {
        // ARIA attributes
        this.element.setAttribute('role', this.config.role);
        this.element.setAttribute('aria-modal', 'true');
        this.element.setAttribute('aria-hidden', 'true');
        
        if (this.config.ariaLabelledBy) {
            this.element.setAttribute('aria-labelledby', this.config.ariaLabelledBy);
        }
        
        if (this.config.ariaDescribedBy) {
            this.element.setAttribute('aria-describedby', this.config.ariaDescribedBy);
        }
        
        // Focus management
        if (this.contentElement) {
            this.contentElement.setAttribute('tabindex', '-1');
        }
    }

    // Public API
    open() {
        const alpineData = this.getAlpineData();
        alpineData.open();
    }

    close() {
        const alpineData = this.getAlpineData();
        alpineData.close();
    }

    toggle() {
        const alpineData = this.getAlpineData();
        alpineData.toggle();
    }

    isOpen() {
        return this.isOpen;
    }

    setSize(size) {
        this.config.size = size;
        this.emit('size-change', { size });
    }

    setPosition(position) {
        this.config.position = position;
        this.emit('position-change', { position });
    }

    setTitle(title) {
        const alpineData = this.getAlpineData();
        alpineData.setTitle(title);
    }

    setContent(content) {
        const alpineData = this.getAlpineData();
        alpineData.setContent(content);
    }

    // Static factory methods
    static create(options = {}) {
        const modalHTML = `
            <div class="wave-modal fixed inset-0 z-50 hidden">
                <div class="wave-modal-backdrop fixed inset-0"></div>
                <div class="wave-modal-content relative bg-white rounded-lg shadow-xl max-h-full flex flex-col">
                    ${options.header !== false ? `
                        <div class="wave-modal-header px-6 py-4 border-b border-gray-200">
                            <div class="flex items-center justify-between">
                                <h3 class="wave-modal-title text-lg font-semibold text-gray-900">
                                    ${options.title || 'Modal Title'}
                                </h3>
                                ${options.closeable !== false ? `
                                    <button class="wave-modal-close text-gray-400 hover:text-gray-600">
                                        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                                        </svg>
                                    </button>
                                ` : ''}
                            </div>
                        </div>
                    ` : ''}
                    <div class="wave-modal-body px-6 py-4 flex-1 overflow-y-auto">
                        ${options.content || 'Modal content goes here.'}
                    </div>
                    ${options.footer ? `
                        <div class="wave-modal-footer px-6 py-4 border-t border-gray-200">
                            ${options.footer}
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
        
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = modalHTML;
        const modalElement = tempDiv.firstElementChild;
        
        const modal = new WaveModal();
        modal.init(modalElement, options);
        
        return modal;
    }

    static confirm(options = {}) {
        const confirmModal = WaveModal.create({
            title: options.title || 'Confirm Action',
            content: options.message || 'Are you sure you want to continue?',
            footer: `
                <div class="flex justify-end gap-3">
                    <button class="wave-modal-cancel btn btn-secondary">
                        ${options.cancelText || 'Cancel'}
                    </button>
                    <button class="wave-modal-confirm btn btn-primary">
                        ${options.confirmText || 'Confirm'}
                    </button>
                </div>
            `,
            size: options.size || 'sm',
            ...options
        });
        
        return new Promise((resolve) => {
            const cancelBtn = confirmModal.element.querySelector('.wave-modal-cancel');
            const confirmBtn = confirmModal.element.querySelector('.wave-modal-confirm');
            
            cancelBtn?.addEventListener('click', () => {
                confirmModal.close();
                resolve(false);
            });
            
            confirmBtn?.addEventListener('click', () => {
                confirmModal.close();
                resolve(true);
            });
            
            confirmModal.open();
        });
    }

    static alert(options = {}) {
        const alertModal = WaveModal.create({
            title: options.title || 'Alert',
            content: options.message || 'Alert message',
            footer: `
                <div class="flex justify-end">
                    <button class="wave-modal-ok btn btn-primary">
                        ${options.okText || 'OK'}
                    </button>
                </div>
            `,
            size: options.size || 'sm',
            ...options
        });
        
        return new Promise((resolve) => {
            const okBtn = alertModal.element.querySelector('.wave-modal-ok');
            
            okBtn?.addEventListener('click', () => {
                alertModal.close();
                resolve(true);
            });
            
            alertModal.open();
        });
    }
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = WaveModal;
}

// Register with ComponentRegistry if available
if (typeof window !== 'undefined' && window.ComponentRegistry) {
    window.ComponentRegistry.register('WaveModal', WaveModal);
}