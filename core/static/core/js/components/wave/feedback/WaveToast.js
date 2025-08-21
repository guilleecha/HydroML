/**
 * WaveToast - Professional toast notification system with queuing and auto-dismiss
 * Part of HydroML Wave-Inspired Component Library
 * 
 * Features:
 * - Monochromatic design with subtle status colors
 * - Global notification queue management
 * - Auto-dismiss with progress indicator
 * - Multiple positions and animations
 * - Icon support and action buttons
 * - Accessibility compliant
 * - Theme system integration
 */

class WaveToast extends BaseComponent {
    constructor() {
        super('WaveToast');
        
        this.defaultConfig = {
            // Toast configuration
            type: 'info', // success, warning, error, info, default
            position: 'top-right', // top-left, top-center, top-right, bottom-left, bottom-center, bottom-right
            duration: 5000, // milliseconds, 0 for persistent
            
            // Content
            title: '',
            message: '',
            icon: null, // auto-determined by type if null
            actionButton: null,
            
            // Behavior
            dismissible: true,
            autoClose: true,
            pauseOnHover: true,
            
            // Animation
            animation: 'slide', // slide, fade, scale
            animationDuration: 300,
            
            // Progress
            showProgress: true,
            progressColor: null,
            
            // Sound
            sound: false,
            soundUrl: null
        };
        
        this.isVisible = false;
        this.isPaused = false;
        this.startTime = null;
        this.remainingTime = null;
        this.timeoutId = null;
        this.progressInterval = null;
    }

    init(element, config = {}) {
        super.init(element, config);
        
        this.toastElement = this.element.querySelector('.wave-toast');
        this.iconElement = this.element.querySelector('.wave-toast-icon');
        this.titleElement = this.element.querySelector('.wave-toast-title');
        this.messageElement = this.element.querySelector('.wave-toast-message');
        this.closeButton = this.element.querySelector('.wave-toast-close');
        this.actionButton = this.element.querySelector('.wave-toast-action');
        this.progressBar = this.element.querySelector('.wave-toast-progress');
        
        this.setupEventListeners();
        this.setupAccessibility();
        
        return this.getAlpineData();
    }

    getAlpineData() {
        return {
            // State
            isVisible: this.isVisible,
            isPaused: this.isPaused,
            progress: 0,
            
            // Computed
            get toastClasses() {
                const base = 'wave-toast relative overflow-hidden rounded-lg shadow-lg max-w-sm w-full pointer-events-auto';
                const type = this.getTypeClasses();
                const animation = this.getAnimationClasses();
                const visible = this.isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-2';
                
                return `${base} ${type} ${animation} ${visible}`.trim();
            },
            
            get containerClasses() {
                return 'wave-toast-container flex flex-col gap-2 pointer-events-none';
            },
            
            get iconClasses() {
                const base = 'wave-toast-icon flex-shrink-0';
                const size = 'w-5 h-5';
                const color = this.getIconColor();
                
                return `${base} ${size} ${color}`.trim();
            },
            
            get progressClasses() {
                const base = 'wave-toast-progress absolute bottom-0 left-0 h-1 transition-all duration-100';
                const color = this.config.progressColor || this.getProgressColor();
                
                return `${base} ${color}`.trim();
            },

            // Methods
            getTypeClasses: () => {
                const types = {
                    success: 'bg-white border border-green-200 text-gray-900',
                    warning: 'bg-white border border-yellow-200 text-gray-900',
                    error: 'bg-white border border-red-200 text-gray-900',
                    info: 'bg-white border border-blue-200 text-gray-900',
                    default: 'bg-white border border-gray-200 text-gray-900'
                };
                return types[this.config.type] || types.default;
            },
            
            getAnimationClasses: () => {
                const base = 'transition-all duration-300 ease-out';
                return base;
            },
            
            getIconColor: () => {
                const colors = {
                    success: 'text-green-500',
                    warning: 'text-yellow-500',
                    error: 'text-red-500',
                    info: 'text-blue-500',
                    default: 'text-gray-500'
                };
                return colors[this.config.type] || colors.default;
            },
            
            getProgressColor: () => {
                const colors = {
                    success: 'bg-green-500',
                    warning: 'bg-yellow-500',
                    error: 'bg-red-500',
                    info: 'bg-blue-500',
                    default: 'bg-gray-500'
                };
                return colors[this.config.type] || colors.default;
            },

            // Toast lifecycle
            show: () => {
                if (this.isVisible) return;
                
                this.isVisible = true;
                this.startTime = Date.now();
                this.remainingTime = this.config.duration;
                
                // Add to container
                WaveToast.addToContainer(this);
                
                // Play sound if enabled
                if (this.config.sound) {
                    this.playSound();
                }
                
                // Start auto-close timer
                if (this.config.autoClose && this.config.duration > 0) {
                    this.startTimer();
                }
                
                // Start progress animation
                if (this.config.showProgress && this.config.duration > 0) {
                    this.startProgress();
                }
                
                this.emit('show', { toast: this });
            },
            
            hide: () => {
                if (!this.isVisible) return;
                
                this.isVisible = false;
                this.clearTimers();
                
                // Remove after animation
                setTimeout(() => {
                    WaveToast.removeFromContainer(this);
                    this.emit('hidden', { toast: this });
                }, this.config.animationDuration);
                
                this.emit('hide', { toast: this });
            },
            
            pause: () => {
                if (this.isPaused || !this.config.autoClose) return;
                
                this.isPaused = true;
                this.remainingTime = this.remainingTime - (Date.now() - this.startTime);
                this.clearTimers();
                
                this.emit('pause', { toast: this });
            },
            
            resume: () => {
                if (!this.isPaused || !this.config.autoClose) return;
                
                this.isPaused = false;
                this.startTime = Date.now();
                this.startTimer();
                this.startProgress();
                
                this.emit('resume', { toast: this });
            },

            // Timer management
            startTimer: () => {
                this.clearTimers();
                
                this.timeoutId = setTimeout(() => {
                    this.hide();
                }, this.remainingTime);
            },
            
            startProgress: () => {
                if (!this.progressBar) return;
                
                const totalDuration = this.config.duration;
                const updateInterval = 50; // Update every 50ms for smooth animation
                
                this.progressInterval = setInterval(() => {
                    if (this.isPaused) return;
                    
                    const elapsed = Date.now() - this.startTime;
                    const progress = Math.min((elapsed / totalDuration) * 100, 100);
                    
                    this.progress = progress;
                    this.progressBar.style.width = `${progress}%`;
                    
                    if (progress >= 100) {
                        clearInterval(this.progressInterval);
                    }
                }, updateInterval);
            },
            
            clearTimers: () => {
                if (this.timeoutId) {
                    clearTimeout(this.timeoutId);
                    this.timeoutId = null;
                }
                
                if (this.progressInterval) {
                    clearInterval(this.progressInterval);
                    this.progressInterval = null;
                }
            },

            // Event handlers
            handleMouseEnter: () => {
                if (this.config.pauseOnHover) {
                    this.pause();
                }
            },
            
            handleMouseLeave: () => {
                if (this.config.pauseOnHover && this.isPaused) {
                    this.resume();
                }
            },
            
            handleClose: () => {
                this.hide();
            },
            
            handleAction: () => {
                if (this.config.actionButton && this.config.actionButton.onClick) {
                    this.config.actionButton.onClick(this);
                }
                
                if (this.config.actionButton && this.config.actionButton.dismiss !== false) {
                    this.hide();
                }
            },

            // Content management
            getIcon: () => {
                const iconName = this.config.icon || this.getDefaultIcon();
                return this.getIconHTML(iconName);
            },
            
            getDefaultIcon: () => {
                const icons = {
                    success: 'check-circle',
                    warning: 'exclamation-triangle',
                    error: 'x-circle',
                    info: 'info-circle',
                    default: 'bell'
                };
                return icons[this.config.type] || icons.default;
            },
            
            getIconHTML: (iconName) => {
                return `
                    <svg class="${this.iconClasses}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        ${this.getIconPath(iconName)}
                    </svg>
                `;
            },
            
            playSound: () => {
                if (!this.config.sound) return;
                
                try {
                    const audio = new Audio(this.config.soundUrl || this.getDefaultSoundUrl());
                    audio.volume = 0.3;
                    audio.play().catch(() => {
                        // Ignore audio play errors (user interaction required)
                    });
                } catch (error) {
                    // Ignore audio errors
                }
            },
            
            getDefaultSoundUrl: () => {
                // You can provide default notification sounds here
                return 'data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1O2+dSgELIHR8N2QQAoUXrTp66hVFApGn+DyvmwhB';
            }
        };
    }

    setupEventListeners() {
        // Mouse events for pause on hover
        if (this.config.pauseOnHover) {
            this.element.addEventListener('mouseenter', () => this.pause());
            this.element.addEventListener('mouseleave', () => this.resume());
        }
        
        // Close button
        if (this.closeButton) {
            this.closeButton.addEventListener('click', () => this.hide());
        }
        
        // Action button
        if (this.actionButton) {
            this.actionButton.addEventListener('click', () => this.handleAction());
        }
    }

    setupAccessibility() {
        this.element.setAttribute('role', 'alert');
        this.element.setAttribute('aria-live', 'polite');
        this.element.setAttribute('aria-atomic', 'true');
        
        if (this.config.dismissible && this.closeButton) {
            this.closeButton.setAttribute('aria-label', 'Close notification');
        }
    }

    getIconPath(iconName) {
        const icons = {
            'check-circle': '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>',
            'x-circle': '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"></path>',
            'exclamation-triangle': '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.464 0L4.268 16.5c-.77.833.192 2.5 1.732 2.5z"></path>',
            'info-circle': '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>',
            'bell': '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"></path>'
        };
        
        return icons[iconName] || icons.bell;
    }

    // Public API
    show() {
        const alpineData = this.getAlpineData();
        alpineData.show();
    }

    hide() {
        const alpineData = this.getAlpineData();
        alpineData.hide();
    }

    pause() {
        const alpineData = this.getAlpineData();
        alpineData.pause();
    }

    resume() {
        const alpineData = this.getAlpineData();
        alpineData.resume();
    }

    updateContent(options) {
        if (options.title !== undefined) {
            this.config.title = options.title;
            if (this.titleElement) {
                this.titleElement.textContent = options.title;
            }
        }
        
        if (options.message !== undefined) {
            this.config.message = options.message;
            if (this.messageElement) {
                this.messageElement.textContent = options.message;
            }
        }
        
        this.emit('update', { toast: this, options });
    }

    // Static methods for global toast management
    static containers = new Map();

    static getContainer(position) {
        if (!WaveToast.containers.has(position)) {
            const container = WaveToast.createContainer(position);
            WaveToast.containers.set(position, container);
        }
        return WaveToast.containers.get(position);
    }

    static createContainer(position) {
        const container = document.createElement('div');
        container.className = `wave-toast-container-${position} fixed z-50 flex flex-col gap-2 pointer-events-none`;
        
        // Position classes
        const positions = {
            'top-left': 'top-4 left-4',
            'top-center': 'top-4 left-1/2 transform -translate-x-1/2',
            'top-right': 'top-4 right-4',
            'bottom-left': 'bottom-4 left-4',
            'bottom-center': 'bottom-4 left-1/2 transform -translate-x-1/2',
            'bottom-right': 'bottom-4 right-4'
        };
        
        container.className += ` ${positions[position] || positions['top-right']}`;
        
        document.body.appendChild(container);
        return container;
    }

    static addToContainer(toast) {
        const container = WaveToast.getContainer(toast.config.position);
        container.appendChild(toast.element);
    }

    static removeFromContainer(toast) {
        if (toast.element.parentNode) {
            toast.element.parentNode.removeChild(toast.element);
        }
    }

    // Factory methods
    static create(options = {}) {
        const toastHTML = `
            <div class="wave-toast relative overflow-hidden rounded-lg shadow-lg max-w-sm w-full pointer-events-auto">
                <div class="p-4">
                    <div class="flex items-start">
                        <div class="flex-shrink-0">
                            <div class="wave-toast-icon"></div>
                        </div>
                        <div class="ml-3 w-0 flex-1">
                            ${options.title ? `
                                <p class="wave-toast-title text-sm font-medium text-gray-900">
                                    ${options.title}
                                </p>
                            ` : ''}
                            <p class="wave-toast-message text-sm text-gray-500 ${options.title ? 'mt-1' : ''}">
                                ${options.message || 'Notification message'}
                            </p>
                            ${options.actionButton ? `
                                <div class="mt-3">
                                    <button class="wave-toast-action text-sm font-medium text-blue-600 hover:text-blue-500">
                                        ${options.actionButton.text || 'Action'}
                                    </button>
                                </div>
                            ` : ''}
                        </div>
                        ${options.dismissible !== false ? `
                            <div class="ml-4 flex-shrink-0 flex">
                                <button class="wave-toast-close bg-white rounded-md inline-flex text-gray-400 hover:text-gray-500">
                                    <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                                    </svg>
                                </button>
                            </div>
                        ` : ''}
                    </div>
                </div>
                ${options.showProgress !== false && options.duration > 0 ? `
                    <div class="wave-toast-progress absolute bottom-0 left-0 h-1 w-0"></div>
                ` : ''}
            </div>
        `;
        
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = toastHTML;
        const toastElement = tempDiv.firstElementChild;
        
        const toast = new WaveToast();
        toast.init(toastElement, options);
        
        return toast;
    }

    static success(message, options = {}) {
        return WaveToast.create({
            type: 'success',
            message,
            ...options
        });
    }

    static error(message, options = {}) {
        return WaveToast.create({
            type: 'error',
            message,
            duration: 0, // Errors should be persistent by default
            ...options
        });
    }

    static warning(message, options = {}) {
        return WaveToast.create({
            type: 'warning',
            message,
            ...options
        });
    }

    static info(message, options = {}) {
        return WaveToast.create({
            type: 'info',
            message,
            ...options
        });
    }

    static show(message, options = {}) {
        const toast = WaveToast.create({
            message,
            ...options
        });
        toast.show();
        return toast;
    }
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = WaveToast;
}

// Register with ComponentRegistry if available
if (typeof window !== 'undefined' && window.ComponentRegistry) {
    window.ComponentRegistry.register('WaveToast', WaveToast);
}