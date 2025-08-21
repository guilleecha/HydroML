/**
 * WaveInput - Professional input component with validation states and icons
 * Part of HydroML Wave-Inspired Component Library
 * 
 * Features:
 * - Monochromatic design system (white, black, grays)
 * - Validation states with visual feedback
 * - Icon support (prefix/suffix)
 * - Accessibility compliant
 * - Theme system integration
 */

class WaveInput extends BaseComponent {
    constructor() {
        super('WaveInput');
        
        this.defaultConfig = {
            variant: 'default', // default, success, warning, error
            size: 'md', // sm, md, lg
            disabled: false,
            readonly: false,
            required: false,
            icon: null, // prefix icon
            suffixIcon: null,
            placeholder: '',
            helpText: '',
            validationMessage: '',
            showValidation: false,
            debounceMs: 300,
            validateOnBlur: true,
            validateOnInput: false
        };
        
        this.validationRules = new Map();
        this.validators = {
            required: (value) => value.trim().length > 0 || 'This field is required',
            email: (value) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value) || 'Please enter a valid email',
            minLength: (min) => (value) => value.length >= min || `Minimum ${min} characters required`,
            maxLength: (max) => (value) => value.length <= max || `Maximum ${max} characters allowed`,
            pattern: (regex, message) => (value) => regex.test(value) || message
        };
    }

    init(element, config = {}) {
        super.init(element, config);
        
        this.input = this.element.querySelector('input');
        this.label = this.element.querySelector('label');
        this.helpTextElement = this.element.querySelector('.wave-input-help');
        this.validationElement = this.element.querySelector('.wave-input-validation');
        this.iconContainer = this.element.querySelector('.wave-input-icon');
        this.suffixContainer = this.element.querySelector('.wave-input-suffix');
        
        this.setupEventListeners();
        this.updateState();
        
        return this.getAlpineData();
    }

    getAlpineData() {
        return {
            // State
            value: this.input?.value || '',
            focused: false,
            valid: true,
            validationMessage: this.config.validationMessage,
            showValidation: this.config.showValidation,
            
            // Computed
            get inputClasses() {
                const base = 'wave-input-field w-full px-3 py-2 border rounded-lg transition-all duration-200';
                const variant = this.getVariantClasses();
                const size = this.getSizeClasses();
                const state = this.getStateClasses();
                
                return `${base} ${variant} ${size} ${state}`;
            },
            
            get containerClasses() {
                return 'wave-input-container relative flex flex-col gap-1';
            },
            
            get labelClasses() {
                const base = 'wave-input-label text-sm font-medium transition-colors duration-200';
                const state = this.focused ? 'text-gray-700' : 'text-gray-600';
                const required = this.config.required ? 'after:content-["*"] after:text-red-400 after:ml-1' : '';
                
                return `${base} ${state} ${required}`;
            },

            // Methods
            getVariantClasses: () => {
                const variants = {
                    default: 'border-gray-300 bg-white text-gray-900 placeholder-gray-500',
                    success: 'border-green-400 bg-green-50 text-green-900',
                    warning: 'border-yellow-400 bg-yellow-50 text-yellow-900', 
                    error: 'border-red-400 bg-red-50 text-red-900'
                };
                return variants[this.config.variant] || variants.default;
            },
            
            getSizeClasses: () => {
                const sizes = {
                    sm: 'px-2 py-1 text-sm',
                    md: 'px-3 py-2 text-base',
                    lg: 'px-4 py-3 text-lg'
                };
                return sizes[this.config.size] || sizes.md;
            },
            
            getStateClasses: () => {
                const disabled = this.config.disabled ? 'opacity-50 cursor-not-allowed' : '';
                const readonly = this.config.readonly ? 'bg-gray-100' : '';
                const focus = this.focused && !this.config.disabled ? 'ring-2 ring-gray-200 border-gray-400' : '';
                
                return `${disabled} ${readonly} ${focus}`.trim();
            },

            // Event Handlers
            handleFocus: () => {
                if (this.config.disabled) return;
                this.focused = true;
                this.emit('focus', { value: this.value });
            },
            
            handleBlur: () => {
                this.focused = false;
                if (this.config.validateOnBlur) {
                    this.validate();
                }
                this.emit('blur', { value: this.value, valid: this.valid });
            },
            
            handleInput: (event) => {
                this.value = event.target.value;
                
                if (this.config.validateOnInput) {
                    this.debouncedValidate();
                }
                
                this.emit('input', { value: this.value, valid: this.valid });
            },
            
            validate: () => {
                this.valid = true;
                this.validationMessage = '';
                
                for (const [rule, validator] of this.validationRules) {
                    const result = validator(this.value);
                    if (result !== true) {
                        this.valid = false;
                        this.validationMessage = result;
                        break;
                    }
                }
                
                this.showValidation = !this.valid;
                this.updateVariant();
                
                return this.valid;
            },
            
            updateVariant: () => {
                if (!this.valid && this.showValidation) {
                    this.config.variant = 'error';
                } else if (this.valid && this.value.length > 0) {
                    this.config.variant = 'success';
                } else {
                    this.config.variant = 'default';
                }
            },
            
            // Validation Rules
            addValidation: (rule, ...params) => {
                if (this.validators[rule]) {
                    this.validationRules.set(rule, this.validators[rule](...params));
                }
            },
            
            addCustomValidation: (name, validator) => {
                this.validationRules.set(name, validator);
            },
            
            clearValidation: () => {
                this.validationRules.clear();
                this.valid = true;
                this.validationMessage = '';
                this.showValidation = false;
                this.config.variant = 'default';
            }
        };
    }

    setupEventListeners() {
        if (!this.input) return;
        
        // Debounced validation for input events
        this.debouncedValidate = this.debounce(() => {
            this.validate();
        }, this.config.debounceMs);
        
        // Setup validation rules from data attributes
        if (this.config.required) {
            this.validationRules.set('required', this.validators.required);
        }
        
        if (this.input.type === 'email') {
            this.validationRules.set('email', this.validators.email);
        }
        
        const minLength = this.input.getAttribute('minlength');
        if (minLength) {
            this.validationRules.set('minLength', this.validators.minLength(parseInt(minLength)));
        }
        
        const maxLength = this.input.getAttribute('maxlength');
        if (maxLength) {
            this.validationRules.set('maxLength', this.validators.maxLength(parseInt(maxLength)));
        }
        
        const pattern = this.input.getAttribute('pattern');
        if (pattern) {
            const patternMessage = this.input.getAttribute('data-pattern-message') || 'Invalid format';
            this.validationRules.set('pattern', this.validators.pattern(new RegExp(pattern), patternMessage));
        }
    }

    updateState() {
        if (!this.input) return;
        
        // Apply configuration to input
        this.input.disabled = this.config.disabled;
        this.input.readOnly = this.config.readonly;
        this.input.required = this.config.required;
        this.input.placeholder = this.config.placeholder;
        
        // Update help text
        if (this.helpTextElement && this.config.helpText) {
            this.helpTextElement.textContent = this.config.helpText;
        }
        
        // Setup icons
        this.setupIcons();
    }

    setupIcons() {
        if (this.config.icon && this.iconContainer) {
            this.iconContainer.innerHTML = `
                <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    ${this.getIconPath(this.config.icon)}
                </svg>
            `;
        }
        
        if (this.config.suffixIcon && this.suffixContainer) {
            this.suffixContainer.innerHTML = `
                <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    ${this.getIconPath(this.config.suffixIcon)}
                </svg>
            `;
        }
    }

    getIconPath(iconName) {
        const icons = {
            user: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>',
            email: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 7.89a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>',
            lock: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a1 1 0 001-1v-6a1 1 0 00-1-1H6a1 1 0 00-1 1v6a1 1 0 001 1zM12 7a4 4 0 114 4v4H8v-4a4 4 0 014-4z"></path>',
            search: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>',
            check: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>',
            x: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>'
        };
        
        return icons[iconName] || icons.user;
    }

    // Public API
    getValue() {
        return this.input?.value || '';
    }

    setValue(value) {
        if (this.input) {
            this.input.value = value;
            this.input.dispatchEvent(new Event('input', { bubbles: true }));
        }
    }

    focus() {
        this.input?.focus();
    }

    blur() {
        this.input?.blur();
    }

    setVariant(variant) {
        this.config.variant = variant;
        this.updateState();
    }

    setValidationMessage(message) {
        this.config.validationMessage = message;
        this.showValidation = !!message;
        this.updateState();
    }

    reset() {
        this.setValue('');
        this.clearValidation();
    }
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = WaveInput;
}

// Register with ComponentRegistry if available
if (typeof window !== 'undefined' && window.ComponentRegistry) {
    window.ComponentRegistry.register('WaveInput', WaveInput);
}