/**
 * GroveBadge - Professional badge component with semantic variants
 * Part of the Grove Design System for HydroML
 * 
 * Features:
 * - Semantic color variants (success, warning, error, info, brand)
 * - Classification colors (purple, pink, indigo, teal, orange)
 * - Multiple sizes (xs, sm, md, lg)
 * - Optional dismiss functionality
 * - Icon and dot indicator support
 * - Accessibility compliant
 * - Grove Design System integration
 */

class GroveBadge {
    constructor(element, config = {}) {
        this.element = element;
        this.config = {
            variant: 'default', // default, success, warning, error, info, brand, purple, pink, indigo, teal, orange
            size: 'md', // xs, sm, md, lg
            outlined: false, // outlined style instead of filled
            dismissible: false,
            clickable: false,
            dot: false, // shows a small dot indicator
            icon: null, // tabler icon name
            href: null, // makes badge clickable
            target: '_self',
            ...config
        };
        
        this.dismissed = false;
        this.init();
    }

    init() {
        this.setupStructure();
        this.applyClasses();
        this.setupEventListeners();
        this.updateAccessibility();
    }

    setupStructure() {
        // Store original content
        const originalContent = this.element.innerHTML;
        
        // Create badge structure
        this.element.innerHTML = '';
        
        // Add dot if configured
        if (this.config.dot) {
            const dot = document.createElement('span');
            dot.className = 'grove-badge__dot';
            this.element.appendChild(dot);
        }
        
        // Add icon if configured
        if (this.config.icon) {
            const icon = document.createElement('svg');
            icon.className = 'grove-badge__icon';
            icon.innerHTML = `<use href="#tabler-${this.config.icon}"></use>`;
            this.element.appendChild(icon);
        }
        
        // Add text content
        const textElement = document.createElement('span');
        textElement.className = 'grove-badge__text';
        textElement.innerHTML = originalContent;
        this.element.appendChild(textElement);
        this.textElement = textElement;
        
        // Add dismiss button if configured
        if (this.config.dismissible) {
            const dismissButton = document.createElement('button');
            dismissButton.className = 'grove-badge__dismiss';
            dismissButton.type = 'button';
            dismissButton.setAttribute('aria-label', 'Remove badge');
            dismissButton.innerHTML = `
                <svg class="grove-badge__dismiss-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
            `;
            this.element.appendChild(dismissButton);
            this.dismissButton = dismissButton;
        }
    }

    applyClasses() {
        // Remove existing grove-badge classes
        this.element.className = this.element.className.replace(/grove-badge[^\s]*/g, '').trim();
        
        // Add base class
        this.element.classList.add('grove-badge');
        
        // Add variant class
        this.element.classList.add(`grove-badge--${this.config.variant}`);
        
        // Add size class
        this.element.classList.add(`grove-badge--${this.config.size}`);
        
        // Add modifiers
        if (this.config.outlined) {
            this.element.classList.add('grove-badge--outlined');
        }
        
        if (this.config.dismissible) {
            this.element.classList.add('grove-badge--dismissible');
        }
        
        if (this.config.clickable || this.config.href) {
            this.element.classList.add('grove-badge--clickable');
        }
        
        if (this.config.dot) {
            this.element.classList.add('grove-badge--dot');
        }
        
        if (this.dismissed) {
            this.element.style.display = 'none';
        }
    }

    setupEventListeners() {
        // Handle dismiss button
        if (this.dismissButton) {
            this.dismissButton.addEventListener('click', (event) => {
                event.stopPropagation();
                this.dismiss();
            });
        }
        
        // Handle clickable badge
        if (this.config.href) {
            this.element.addEventListener('click', (event) => {
                if (this.config.href) {
                    if (this.config.target === '_blank') {
                        window.open(this.config.href, '_blank', 'noopener,noreferrer');
                    } else {
                        window.location.href = this.config.href;
                    }
                }
                this.emit('click', { event, href: this.config.href });
            });
        } else if (this.config.clickable) {
            this.element.addEventListener('click', (event) => {
                this.emit('click', { event, variant: this.config.variant });
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
    }

    updateAccessibility() {
        // Make focusable if interactive
        if (this.config.href || this.config.clickable || this.config.dismissible) {
            this.element.setAttribute('tabindex', '0');
        }
        
        // Update ARIA attributes
        if (this.config.dismissible) {
            this.element.setAttribute('role', 'button');
            this.element.setAttribute('aria-label', `Badge: ${this.getTextContent()}. Press Delete to remove.`);
        } else if (this.config.clickable) {
            this.element.setAttribute('role', 'button');
            this.element.setAttribute('aria-label', `Badge: ${this.getTextContent()}`);
        }
        
        // Update link attributes
        if (this.config.href) {
            this.element.setAttribute('role', 'link');
            this.element.setAttribute('aria-label', `Badge link: ${this.getTextContent()}`);
        }
    }

    // Public API Methods
    dismiss() {
        if (this.dismissed) return;
        
        this.dismissed = true;
        
        // Add dismissing animation class
        this.element.classList.add('grove-badge--dismissing');
        
        // Emit dismiss event
        this.emit('dismiss', { 
            variant: this.config.variant,
            text: this.getTextContent()
        });
        
        // Hide after animation
        setTimeout(() => {
            this.element.style.display = 'none';
            this.element.classList.remove('grove-badge--dismissing');
            this.emit('dismissed', { 
                variant: this.config.variant,
                text: this.getTextContent()
            });
        }, 200);
    }

    restore() {
        if (!this.dismissed) return;
        
        this.dismissed = false;
        this.element.style.display = '';
        
        this.emit('restore', { 
            variant: this.config.variant,
            text: this.getTextContent()
        });
    }

    setVariant(variant) {
        // Remove old variant class
        this.element.classList.remove(`grove-badge--${this.config.variant}`);
        
        // Update config and add new class
        this.config.variant = variant;
        this.element.classList.add(`grove-badge--${variant}`);
        
        this.emit('variant-change', { variant });
    }

    setSize(size) {
        // Remove old size class
        this.element.classList.remove(`grove-badge--${this.config.size}`);
        
        // Update config and add new class
        this.config.size = size;
        this.element.classList.add(`grove-badge--${size}`);
        
        this.emit('size-change', { size });
    }

    setText(text) {
        if (this.textElement) {
            this.textElement.textContent = text;
            this.updateAccessibility();
            this.emit('text-change', { text });
        }
    }

    setIcon(iconName) {
        const existingIcon = this.element.querySelector('.grove-badge__icon');
        
        if (iconName && !existingIcon) {
            // Add icon
            const icon = document.createElement('svg');
            icon.className = 'grove-badge__icon';
            icon.innerHTML = `<use href="#tabler-${iconName}"></use>`;
            this.element.insertBefore(icon, this.textElement);
        } else if (iconName && existingIcon) {
            // Update existing icon
            existingIcon.innerHTML = `<use href="#tabler-${iconName}"></use>`;
        } else if (!iconName && existingIcon) {
            // Remove icon
            existingIcon.remove();
        }
        
        this.config.icon = iconName;
        this.emit('icon-change', { icon: iconName });
    }

    toggleOutlined() {
        this.config.outlined = !this.config.outlined;
        this.element.classList.toggle('grove-badge--outlined', this.config.outlined);
        
        this.emit('outline-change', { outlined: this.config.outlined });
    }

    // Utility Methods
    getTextContent() {
        return this.textElement?.textContent || this.element.textContent || '';
    }

    isDismissed() {
        return this.dismissed;
    }

    getConfig() {
        return { ...this.config };
    }

    // Event System
    emit(eventName, detail = {}) {
        const event = new CustomEvent(`grove-badge:${eventName}`, {
            detail: { element: this.element, ...detail },
            bubbles: true,
            cancelable: true
        });
        this.element.dispatchEvent(event);
    }

    on(eventName, handler) {
        this.element.addEventListener(`grove-badge:${eventName}`, handler);
        return this; // For chaining
    }

    off(eventName, handler) {
        this.element.removeEventListener(`grove-badge:${eventName}`, handler);
        return this; // For chaining
    }

    // Destroy Method
    destroy() {
        // Remove event listeners
        if (this.dismissButton) {
            this.dismissButton.removeEventListener('click', this.handleDismiss);
        }
        
        // Remove classes
        this.element.className = this.element.className.replace(/grove-badge[^\s]*/g, '').trim();
        
        // Reset structure
        if (this.textElement) {
            this.element.innerHTML = this.textElement.innerHTML;
        }
        
        // Remove properties
        delete this.element._groveBadge;
        
        this.emit('destroyed');
    }
}

// Auto-initialization for elements with data-grove-badge attribute
document.addEventListener('DOMContentLoaded', () => {
    const badges = document.querySelectorAll('[data-grove-badge]');
    badges.forEach(element => {
        if (!element._groveBadge) {
            const config = element.dataset.groveBadge ? 
                JSON.parse(element.dataset.groveBadge) : {};
            element._groveBadge = new GroveBadge(element, config);
        }
    });
});

// Static factory method
GroveBadge.create = (element, config = {}) => {
    if (typeof element === 'string') {
        element = document.querySelector(element);
    }
    
    if (!element) {
        console.warn('GroveBadge: Element not found');
        return null;
    }
    
    if (element._groveBadge) {
        return element._groveBadge;
    }
    
    return new GroveBadge(element, config);
};

// Alpine.js integration
if (typeof Alpine !== 'undefined') {
    Alpine.data('groveBadge', (config = {}) => ({
        badge: null,
        
        init() {
            this.badge = new GroveBadge(this.$el, config);
        },
        
        dismiss() {
            this.badge?.dismiss();
        },
        
        restore() {
            this.badge?.restore();
        },
        
        setVariant(variant) {
            this.badge?.setVariant(variant);
        },
        
        setText(text) {
            this.badge?.setText(text);
        }
    }));
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = GroveBadge;
}

// Global registration
if (typeof window !== 'undefined') {
    window.GroveBadge = GroveBadge;
}