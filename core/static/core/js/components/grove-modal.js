/**
 * Grove Modal & Panel JavaScript Component
 * Provides accessibility features and modal management
 */

class GroveModal {
    constructor(element, options = {}) {
        this.element = element;
        this.backdrop = element.closest('.grove-modal-backdrop, .grove-panel-backdrop');
        this.options = {
            closeOnBackdrop: true,
            closeOnEscape: true,
            focusOnOpen: true,
            returnFocus: true,
            ...options
        };
        
        this.isOpen = false;
        this.previousFocus = null;
        this.focusableElements = [];
        
        this.init();
    }
    
    init() {
        // Find close buttons
        this.closeButtons = this.element.querySelectorAll('.grove-modal-close, [data-grove-modal-close]');
        
        // Bind events
        this.closeButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                this.close();
            });
        });
        
        // Backdrop click to close
        if (this.backdrop && this.options.closeOnBackdrop) {
            this.backdrop.addEventListener('click', (e) => {
                if (e.target === this.backdrop) {
                    this.close();
                }
            });
        }
        
        // Escape key to close
        if (this.options.closeOnEscape) {
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && this.isOpen) {
                    this.close();
                }
            });
        }
        
        // Focus management
        this.element.addEventListener('keydown', this.handleKeyDown.bind(this));
    }
    
    open() {
        if (this.isOpen) return;
        
        // Store previous focus
        if (this.options.returnFocus) {
            this.previousFocus = document.activeElement;
        }
        
        // Show modal
        this.backdrop.classList.add('show');
        this.backdrop.classList.remove('closing');
        
        // Lock body scroll
        document.body.classList.add('grove-modal-scroll-lock');
        
        // Set focus
        if (this.options.focusOnOpen) {
            setTimeout(() => {
                const focusTarget = this.element.querySelector('[data-grove-modal-focus]') || 
                                 this.element.querySelector('.grove-modal-close') || 
                                 this.element;
                focusTarget.focus();
            }, 100);
        }
        
        // Update focusable elements
        this.updateFocusableElements();
        
        this.isOpen = true;
        
        // Emit event
        this.element.dispatchEvent(new CustomEvent('grove-modal:opened', {
            bubbles: true,
            detail: { modal: this }
        }));
    }
    
    close() {
        if (!this.isOpen) return;
        
        // Add closing class for animation
        this.backdrop.classList.add('closing');
        
        setTimeout(() => {
            // Hide modal
            this.backdrop.classList.remove('show', 'closing');
            
            // Unlock body scroll
            document.body.classList.remove('grove-modal-scroll-lock');
            
            // Return focus
            if (this.options.returnFocus && this.previousFocus) {
                this.previousFocus.focus();
            }
            
            this.isOpen = false;
            
            // Emit event
            this.element.dispatchEvent(new CustomEvent('grove-modal:closed', {
                bubbles: true,
                detail: { modal: this }
            }));
        }, 150); // Match CSS animation duration
    }
    
    handleKeyDown(e) {
        if (!this.isOpen) return;
        
        // Tab trap
        if (e.key === 'Tab') {
            this.trapFocus(e);
        }
    }
    
    trapFocus(e) {
        const focusableElements = this.getFocusableElements();
        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];
        
        if (e.shiftKey) {
            // Shift + Tab
            if (document.activeElement === firstElement) {
                e.preventDefault();
                lastElement.focus();
            }
        } else {
            // Tab
            if (document.activeElement === lastElement) {
                e.preventDefault();
                firstElement.focus();
            }
        }
    }
    
    getFocusableElements() {
        const focusableSelectors = [
            'button:not([disabled])',
            'input:not([disabled])',
            'select:not([disabled])',
            'textarea:not([disabled])',
            'a[href]',
            '[tabindex]:not([tabindex="-1"])',
            '[data-grove-modal-focus]'
        ];
        
        return Array.from(this.element.querySelectorAll(focusableSelectors.join(',')))
            .filter(el => !el.hasAttribute('hidden') && el.offsetParent !== null);
    }
    
    updateFocusableElements() {
        this.focusableElements = this.getFocusableElements();
    }
}

// Auto-initialize modals
document.addEventListener('DOMContentLoaded', () => {
    // Initialize all modals
    document.querySelectorAll('.grove-modal, .grove-panel').forEach(modal => {
        if (!modal.groveModal) {
            modal.groveModal = new GroveModal(modal);
        }
    });
    
    // Handle modal triggers
    document.querySelectorAll('[data-grove-modal-target]').forEach(trigger => {
        trigger.addEventListener('click', (e) => {
            e.preventDefault();
            const targetSelector = trigger.getAttribute('data-grove-modal-target');
            const target = document.querySelector(targetSelector);
            if (target && target.groveModal) {
                target.groveModal.open();
            }
        });
    });
});

// Global utility functions
window.GroveModal = GroveModal;

window.groveModal = {
    open: (selector) => {
        const modal = document.querySelector(selector);
        if (modal && modal.groveModal) {
            modal.groveModal.open();
        }
    },
    
    close: (selector) => {
        const modal = document.querySelector(selector);
        if (modal && modal.groveModal) {
            modal.groveModal.close();
        }
    },
    
    closeAll: () => {
        document.querySelectorAll('.grove-modal, .grove-panel').forEach(modal => {
            if (modal.groveModal && modal.groveModal.isOpen) {
                modal.groveModal.close();
            }
        });
    }
};