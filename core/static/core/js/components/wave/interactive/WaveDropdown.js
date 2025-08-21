/**
 * WaveDropdown - Professional dropdown component with Grove design
 * Part of HydroML Grove Component Library
 * 
 * Features:
 * - Grove monochromatic design with smooth animations
 * - Multiple trigger options (click, hover, focus)
 * - Configurable positioning (auto, top, bottom, left, right)
 * - Keyboard navigation support (Arrow keys, Enter, Escape)
 * - Click outside to close
 * - Custom content support
 * - Accessibility compliant (ARIA attributes)
 * - Mobile responsive behavior
 */

class WaveDropdown extends BaseComponent {
    constructor() {
        super('WaveDropdown');
        
        this.defaultConfig = {
            trigger: 'click', // click, hover, focus, manual
            position: 'auto', // auto, top, bottom, left, right, top-start, top-end, bottom-start, bottom-end
            offset: 8, // pixels from trigger element
            closeOnClick: true, // close when clicking inside dropdown
            closeOnOutsideClick: true,
            closeOnEscape: true,
            showArrow: false, // show positioning arrow
            animation: 'fade', // fade, slide, scale, none
            animationDuration: 200, // milliseconds
            delay: { open: 0, close: 300 }, // hover delays
            disabled: false,
            zIndex: 1000,
            minWidth: null, // minimum width in pixels
            maxWidth: null, // maximum width in pixels
            boundary: 'viewport', // viewport, scrollParent, or element selector
            strategy: 'absolute' // absolute, fixed
        };
        
        this.state = {
            isOpen: false,
            position: null,
            triggerRect: null,
            dropdownRect: null
        };
        
        this.openTimeout = null;
        this.closeTimeout = null;
    }

    init(element, config = {}) {
        super.init(element, config);
        
        // Find key elements
        this.triggerElement = this.element.querySelector('.wave-dropdown-trigger') || this.element.children[0];
        this.dropdownElement = this.element.querySelector('.wave-dropdown-content') || this.element.children[1];
        
        if (!this.triggerElement || !this.dropdownElement) {
            console.warn('WaveDropdown: Missing trigger or content element');
            return;
        }
        
        this.setupEventListeners();
        this.updateState();
        this.initializeAriaAttributes();
        
        return this.getAlpineData();
    }

    getAlpineData() {
        return {
            // State
            isOpen: this.state.isOpen,
            position: this.state.position,
            
            // Computed
            get dropdownClasses() {
                const base = 'wave-dropdown-content absolute bg-white dark:bg-gray-800 rounded-md shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none transition-all duration-200 z-50';
                const animation = this.getAnimationClasses();
                const visibility = this.isOpen ? 'opacity-100 visible' : 'opacity-0 invisible pointer-events-none';
                const sizing = this.getSizingClasses();
                
                return `${base} ${animation} ${visibility} ${sizing}`.trim();
            },
            
            get wrapperClasses() {
                return `wave-dropdown relative inline-block ${this.config.disabled ? 'pointer-events-none opacity-50' : ''}`.trim();
            },
            
            get triggerClasses() {
                const base = 'wave-dropdown-trigger focus:outline-none';
                const state = this.isOpen ? 'ring-2 ring-grove-accent' : '';
                return `${base} ${state}`.trim();
            },

            // Animation Methods
            getAnimationClasses: () => {
                const animations = {
                    fade: 'transition-opacity',
                    slide: this.position?.includes('top') ? 'transition-all transform' + (this.isOpen ? ' translate-y-0' : ' -translate-y-2') :
                           'transition-all transform' + (this.isOpen ? ' translate-y-0' : ' translate-y-2'),
                    scale: 'transition-all transform origin-top' + (this.isOpen ? ' scale-100' : ' scale-95'),
                    none: ''
                };
                return animations[this.config.animation] || animations.fade;
            },
            
            getSizingClasses: () => {
                let classes = '';
                if (this.config.minWidth) classes += ` min-w-[${this.config.minWidth}px]`;
                if (this.config.maxWidth) classes += ` max-w-[${this.config.maxWidth}px]`;
                return classes;
            },

            // Event Handlers
            handleTriggerClick: (event) => {
                if (this.config.disabled) return;
                
                if (this.config.trigger === 'click' || this.config.trigger === 'manual') {
                    event.preventDefault();
                    event.stopPropagation();
                    this.toggle();
                }
            },
            
            handleTriggerMouseEnter: () => {
                if (this.config.disabled || this.config.trigger !== 'hover') return;
                
                this.clearCloseTimeout();
                this.openTimeout = setTimeout(() => {
                    this.open();
                }, this.config.delay.open);
            },
            
            handleTriggerMouseLeave: () => {
                if (this.config.disabled || this.config.trigger !== 'hover') return;
                
                this.clearOpenTimeout();
                this.closeTimeout = setTimeout(() => {
                    this.close();
                }, this.config.delay.close);
            },
            
            handleTriggerFocus: () => {
                if (this.config.disabled || this.config.trigger !== 'focus') return;
                this.open();
            },
            
            handleTriggerBlur: () => {
                if (this.config.disabled || this.config.trigger !== 'focus') return;
                // Small delay to allow clicking on dropdown content
                setTimeout(() => {
                    if (!this.dropdownElement.contains(document.activeElement)) {
                        this.close();
                    }
                }, 100);
            },
            
            handleDropdownMouseEnter: () => {
                if (this.config.trigger === 'hover') {
                    this.clearCloseTimeout();
                }
            },
            
            handleDropdownMouseLeave: () => {
                if (this.config.trigger === 'hover') {
                    this.closeTimeout = setTimeout(() => {
                        this.close();
                    }, this.config.delay.close);
                }
            },
            
            handleDropdownClick: (event) => {
                if (this.config.closeOnClick) {
                    this.close();
                } else {
                    event.stopPropagation();
                }
            },
            
            handleKeyDown: (event) => {
                if (this.config.disabled) return;
                
                switch (event.key) {
                    case 'Escape':
                        if (this.config.closeOnEscape && this.isOpen) {
                            event.preventDefault();
                            this.close();
                            this.triggerElement.focus();
                        }
                        break;
                    case 'Enter':
                    case ' ':
                        if (event.target === this.triggerElement && this.config.trigger === 'click') {
                            event.preventDefault();
                            this.toggle();
                        }
                        break;
                    case 'ArrowDown':
                        if (event.target === this.triggerElement) {
                            event.preventDefault();
                            this.open();
                            this.focusFirstItem();
                        } else if (this.isOpen) {
                            event.preventDefault();
                            this.focusNextItem();
                        }
                        break;
                    case 'ArrowUp':
                        if (this.isOpen) {
                            event.preventDefault();
                            this.focusPreviousItem();
                        }
                        break;
                    case 'Tab':
                        if (this.isOpen) {
                            this.close();
                        }
                        break;
                }
            },

            // Public Methods
            toggle: () => {
                if (this.isOpen) {
                    this.close();
                } else {
                    this.open();
                }
            },
            
            open: () => {
                if (this.config.disabled || this.isOpen) return;
                
                this.clearTimeouts();
                this.state.isOpen = true;
                this.isOpen = true;
                
                this.updatePosition();
                this.updateAriaAttributes();
                
                this.emit('open', { 
                    position: this.state.position,
                    triggerElement: this.triggerElement,
                    dropdownElement: this.dropdownElement
                });
                
                // Focus management
                if (this.config.trigger === 'click') {
                    this.$nextTick(() => {
                        this.focusFirstItem();
                    });
                }
            },
            
            close: () => {
                if (!this.isOpen) return;
                
                this.clearTimeouts();
                this.state.isOpen = false;
                this.isOpen = false;
                
                this.updateAriaAttributes();
                
                this.emit('close', { 
                    triggerElement: this.triggerElement,
                    dropdownElement: this.dropdownElement
                });
            },

            // Focus Management
            focusFirstItem: () => {
                const focusableItems = this.getFocusableItems();
                if (focusableItems.length > 0) {
                    focusableItems[0].focus();
                }
            },
            
            focusLastItem: () => {
                const focusableItems = this.getFocusableItems();
                if (focusableItems.length > 0) {
                    focusableItems[focusableItems.length - 1].focus();
                }
            },
            
            focusNextItem: () => {
                const focusableItems = this.getFocusableItems();
                const currentIndex = focusableItems.indexOf(document.activeElement);
                const nextIndex = currentIndex < focusableItems.length - 1 ? currentIndex + 1 : 0;
                focusableItems[nextIndex].focus();
            },
            
            focusPreviousItem: () => {
                const focusableItems = this.getFocusableItems();
                const currentIndex = focusableItems.indexOf(document.activeElement);
                const previousIndex = currentIndex > 0 ? currentIndex - 1 : focusableItems.length - 1;
                focusableItems[previousIndex].focus();
            },

            // Position Management
            updatePosition: () => {
                if (!this.dropdownElement || !this.triggerElement) return;
                
                this.state.triggerRect = this.triggerElement.getBoundingClientRect();
                
                // Reset positioning
                this.dropdownElement.style.position = this.config.strategy;
                this.dropdownElement.style.zIndex = this.config.zIndex;
                
                const position = this.calculatePosition();
                this.state.position = position.placement;
                
                // Apply positioning
                Object.assign(this.dropdownElement.style, {
                    top: `${position.y}px`,
                    left: `${position.x}px`,
                    transformOrigin: this.getTransformOrigin(position.placement)
                });
                
                // Update arrow if enabled
                if (this.config.showArrow) {
                    this.updateArrow(position);
                }
            },
            
            calculatePosition: () => {
                const trigger = this.state.triggerRect;
                const dropdown = this.dropdownElement.getBoundingClientRect();
                const viewport = {
                    width: window.innerWidth,
                    height: window.innerHeight
                };
                
                let placement = this.config.position;
                let x = 0;
                let y = 0;
                
                // Auto positioning logic
                if (placement === 'auto') {
                    const spaceAbove = trigger.top;
                    const spaceBelow = viewport.height - trigger.bottom;
                    const spaceLeft = trigger.left;
                    const spaceRight = viewport.width - trigger.right;
                    
                    if (spaceBelow >= dropdown.height || spaceBelow >= spaceAbove) {
                        placement = 'bottom-start';
                    } else {
                        placement = 'top-start';
                    }
                }
                
                // Calculate position based on placement
                switch (placement) {
                    case 'top':
                        x = trigger.left + (trigger.width / 2) - (dropdown.width / 2);
                        y = trigger.top - dropdown.height - this.config.offset;
                        break;
                    case 'top-start':
                        x = trigger.left;
                        y = trigger.top - dropdown.height - this.config.offset;
                        break;
                    case 'top-end':
                        x = trigger.right - dropdown.width;
                        y = trigger.top - dropdown.height - this.config.offset;
                        break;
                    case 'bottom':
                        x = trigger.left + (trigger.width / 2) - (dropdown.width / 2);
                        y = trigger.bottom + this.config.offset;
                        break;
                    case 'bottom-start':
                        x = trigger.left;
                        y = trigger.bottom + this.config.offset;
                        break;
                    case 'bottom-end':
                        x = trigger.right - dropdown.width;
                        y = trigger.bottom + this.config.offset;
                        break;
                    case 'left':
                        x = trigger.left - dropdown.width - this.config.offset;
                        y = trigger.top + (trigger.height / 2) - (dropdown.height / 2);
                        break;
                    case 'right':
                        x = trigger.right + this.config.offset;
                        y = trigger.top + (trigger.height / 2) - (dropdown.height / 2);
                        break;
                }
                
                // Boundary checking and adjustment
                const adjusted = this.adjustForBoundaries(x, y, dropdown, viewport);
                
                return {
                    x: adjusted.x,
                    y: adjusted.y,
                    placement
                };
            },
            
            adjustForBoundaries: (x, y, dropdown, viewport) => {
                let adjustedX = x;
                let adjustedY = y;
                
                // Horizontal boundary checking
                if (adjustedX < 0) {
                    adjustedX = this.config.offset;
                } else if (adjustedX + dropdown.width > viewport.width) {
                    adjustedX = viewport.width - dropdown.width - this.config.offset;
                }
                
                // Vertical boundary checking
                if (adjustedY < 0) {
                    adjustedY = this.config.offset;
                } else if (adjustedY + dropdown.height > viewport.height) {
                    adjustedY = viewport.height - dropdown.height - this.config.offset;
                }
                
                return { x: adjustedX, y: adjustedY };
            },
            
            getTransformOrigin: (placement) => {
                const origins = {
                    'top': 'bottom center',
                    'top-start': 'bottom left',
                    'top-end': 'bottom right',
                    'bottom': 'top center',
                    'bottom-start': 'top left',
                    'bottom-end': 'top right',
                    'left': 'center right',
                    'right': 'center left'
                };
                return origins[placement] || 'top left';
            }
        };
    }

    setupEventListeners() {
        // Trigger events
        this.triggerElement.addEventListener('click', this.getAlpineData().handleTriggerClick);
        this.triggerElement.addEventListener('mouseenter', this.getAlpineData().handleTriggerMouseEnter);
        this.triggerElement.addEventListener('mouseleave', this.getAlpineData().handleTriggerMouseLeave);
        this.triggerElement.addEventListener('focus', this.getAlpineData().handleTriggerFocus);
        this.triggerElement.addEventListener('blur', this.getAlpineData().handleTriggerBlur);
        
        // Dropdown events
        this.dropdownElement.addEventListener('mouseenter', this.getAlpineData().handleDropdownMouseEnter);
        this.dropdownElement.addEventListener('mouseleave', this.getAlpineData().handleDropdownMouseLeave);
        this.dropdownElement.addEventListener('click', this.getAlpineData().handleDropdownClick);
        
        // Keyboard events
        this.element.addEventListener('keydown', this.getAlpineData().handleKeyDown);
        
        // Outside click
        if (this.config.closeOnOutsideClick) {
            document.addEventListener('click', (event) => {
                if (!this.element.contains(event.target) && this.state.isOpen) {
                    this.close();
                }
            });
        }
        
        // Window resize
        window.addEventListener('resize', () => {
            if (this.state.isOpen) {
                this.updatePosition();
            }
        });
        
        // Scroll events
        window.addEventListener('scroll', () => {
            if (this.state.isOpen) {
                this.updatePosition();
            }
        }, true);
    }

    updateState() {
        this.initializeAriaAttributes();
        
        if (this.state.isOpen) {
            this.updatePosition();
        }
    }

    initializeAriaAttributes() {
        // Set up ARIA relationship
        const dropdownId = this.dropdownElement.id || `wave-dropdown-${Math.random().toString(36).substr(2, 9)}`;
        
        if (!this.dropdownElement.id) {
            this.dropdownElement.id = dropdownId;
        }
        
        this.triggerElement.setAttribute('aria-haspopup', 'true');
        this.triggerElement.setAttribute('aria-controls', dropdownId);
        this.updateAriaAttributes();
        
        this.dropdownElement.setAttribute('role', 'menu');
        this.dropdownElement.setAttribute('aria-labelledby', this.triggerElement.id || 'dropdown-trigger');
    }

    updateAriaAttributes() {
        this.triggerElement.setAttribute('aria-expanded', this.state.isOpen.toString());
        
        if (this.state.isOpen) {
            this.dropdownElement.removeAttribute('aria-hidden');
        } else {
            this.dropdownElement.setAttribute('aria-hidden', 'true');
        }
    }

    getFocusableItems() {
        const focusableSelectors = [
            'a[href]',
            'button:not([disabled])',
            'input:not([disabled])',
            'select:not([disabled])',
            'textarea:not([disabled])',
            '[tabindex]:not([tabindex="-1"])'
        ].join(', ');
        
        return Array.from(this.dropdownElement.querySelectorAll(focusableSelectors));
    }

    clearTimeouts() {
        this.clearOpenTimeout();
        this.clearCloseTimeout();
    }

    clearOpenTimeout() {
        if (this.openTimeout) {
            clearTimeout(this.openTimeout);
            this.openTimeout = null;
        }
    }

    clearCloseTimeout() {
        if (this.closeTimeout) {
            clearTimeout(this.closeTimeout);
            this.closeTimeout = null;
        }
    }

    updateArrow(position) {
        // Arrow implementation for visual enhancement
        // This would create and position an arrow element
    }

    // Public API
    open() {
        this.getAlpineData().open();
    }

    close() {
        this.getAlpineData().close();
    }

    toggle() {
        this.getAlpineData().toggle();
    }

    setDisabled(disabled) {
        this.config.disabled = disabled;
        this.updateState();
        this.emit('disabled-change', { disabled });
    }

    setPosition(position) {
        this.config.position = position;
        if (this.state.isOpen) {
            this.updatePosition();
        }
        this.emit('position-change', { position });
    }

    destroy() {
        this.clearTimeouts();
        super.destroy();
    }
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = WaveDropdown;
}

// Register with ComponentRegistry if available
if (typeof window !== 'undefined' && window.ComponentRegistry) {
    window.ComponentRegistry.register('WaveDropdown', WaveDropdown);
}