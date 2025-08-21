/**
 * WaveSelect - Professional select dropdown component with search and multi-select
 * Part of HydroML Wave-Inspired Component Library
 * 
 * Features:
 * - Monochromatic design with subtle highlights
 * - Search functionality
 * - Multi-select support
 * - Custom styling
 * - Accessibility compliant
 * - Theme system integration
 */

class WaveSelect extends BaseComponent {
    constructor() {
        super('WaveSelect');
        
        this.defaultConfig = {
            // Select configuration
            options: [],
            value: null,
            multiple: false,
            searchable: false,
            clearable: false,
            placeholder: 'Select an option...',
            
            // Styling
            size: 'md', // sm, md, lg
            variant: 'default', // default, success, warning, error
            
            // Behavior
            disabled: false,
            readonly: false,
            required: false,
            
            // Search
            searchPlaceholder: 'Search options...',
            noResultsText: 'No options found',
            
            // Validation
            validationMessage: '',
            showValidation: false
        };
        
        this.selectedValues = new Set();
        this.filteredOptions = [];
        this.isOpen = false;
        this.searchQuery = '';
        this.focusedOptionIndex = -1;
    }

    init(element, config = {}) {
        super.init(element, config);
        
        this.selectElement = this.element.querySelector('select');
        this.dropdownElement = this.element.querySelector('.wave-select-dropdown');
        this.triggerElement = this.element.querySelector('.wave-select-trigger');
        this.searchInput = this.element.querySelector('.wave-select-search');
        this.optionsContainer = this.element.querySelector('.wave-select-options');
        this.selectedContainer = this.element.querySelector('.wave-select-selected');
        
        this.initializeOptions();
        this.setupEventListeners();
        this.updateState();
        
        return this.getAlpineData();
    }

    getAlpineData() {
        return {
            // State
            isOpen: this.isOpen,
            searchQuery: this.searchQuery,
            selectedValues: Array.from(this.selectedValues),
            focusedOptionIndex: this.focusedOptionIndex,
            
            // Computed
            get selectClasses() {
                const base = 'wave-select relative w-full';
                const disabled = this.config.disabled ? 'opacity-50 pointer-events-none' : '';
                
                return `${base} ${disabled}`.trim();
            },
            
            get triggerClasses() {
                const base = 'wave-select-trigger w-full px-3 py-2 border rounded-lg transition-all duration-200 flex items-center justify-between cursor-pointer';
                const variant = this.getVariantClasses();
                const size = this.getSizeClasses();
                const focus = this.isOpen ? 'ring-2 ring-gray-200 border-gray-400' : '';
                
                return `${base} ${variant} ${size} ${focus}`.trim();
            },
            
            get dropdownClasses() {
                const base = 'wave-select-dropdown absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg';
                const visible = this.isOpen ? 'block' : 'hidden';
                
                return `${base} ${visible}`.trim();
            },
            
            get filteredOptions() {
                if (!this.searchQuery) return this.config.options;
                
                return this.config.options.filter(option => 
                    option.label.toLowerCase().includes(this.searchQuery.toLowerCase())
                );
            },

            // Methods
            getVariantClasses: () => {
                const variants = {
                    default: 'border-gray-300 bg-white text-gray-900',
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

            // Event handlers
            toggleDropdown: () => {
                if (this.config.disabled || this.config.readonly) return;
                
                this.isOpen = !this.isOpen;
                
                if (this.isOpen) {
                    this.focusSearchInput();
                    this.emit('open');
                } else {
                    this.emit('close');
                }
            },
            
            selectOption: (option) => {
                if (this.config.multiple) {
                    if (this.selectedValues.has(option.value)) {
                        this.selectedValues.delete(option.value);
                    } else {
                        this.selectedValues.add(option.value);
                    }
                } else {
                    this.selectedValues.clear();
                    this.selectedValues.add(option.value);
                    this.isOpen = false;
                }
                
                this.updateNativeSelect();
                this.emit('change', { 
                    value: this.getValue(),
                    option,
                    selectedOptions: this.getSelectedOptions()
                });
            },
            
            removeOption: (optionValue) => {
                this.selectedValues.delete(optionValue);
                this.updateNativeSelect();
                this.emit('change', { 
                    value: this.getValue(),
                    selectedOptions: this.getSelectedOptions()
                });
            },
            
            clearSelection: () => {
                this.selectedValues.clear();
                this.updateNativeSelect();
                this.emit('clear');
            },
            
            handleSearch: (query) => {
                this.searchQuery = query;
                this.focusedOptionIndex = -1;
                this.emit('search', { query });
            },
            
            handleKeydown: (event) => {
                switch (event.key) {
                    case 'Enter':
                        event.preventDefault();
                        if (this.isOpen) {
                            if (this.focusedOptionIndex >= 0) {
                                this.selectOption(this.filteredOptions[this.focusedOptionIndex]);
                            }
                        } else {
                            this.toggleDropdown();
                        }
                        break;
                    case 'Escape':
                        if (this.isOpen) {
                            event.preventDefault();
                            this.isOpen = false;
                        }
                        break;
                    case 'ArrowDown':
                        event.preventDefault();
                        if (!this.isOpen) {
                            this.isOpen = true;
                        } else {
                            this.focusedOptionIndex = Math.min(
                                this.focusedOptionIndex + 1,
                                this.filteredOptions.length - 1
                            );
                        }
                        break;
                    case 'ArrowUp':
                        event.preventDefault();
                        if (this.isOpen) {
                            this.focusedOptionIndex = Math.max(this.focusedOptionIndex - 1, 0);
                        }
                        break;
                }
            },

            // Utility methods
            getDisplayText: () => {
                if (this.selectedValues.size === 0) {
                    return this.config.placeholder;
                }
                
                if (this.config.multiple) {
                    return `${this.selectedValues.size} selected`;
                } else {
                    const selectedOption = this.config.options.find(
                        opt => opt.value === Array.from(this.selectedValues)[0]
                    );
                    return selectedOption ? selectedOption.label : this.config.placeholder;
                }
            },
            
            isOptionSelected: (option) => {
                return this.selectedValues.has(option.value);
            },
            
            isOptionFocused: (option, index) => {
                return this.focusedOptionIndex === index;
            },
            
            getSelectedOptions: () => {
                return this.config.options.filter(option => 
                    this.selectedValues.has(option.value)
                );
            }
        };
    }

    initializeOptions() {
        // Initialize from native select if present
        if (this.selectElement) {
            const options = Array.from(this.selectElement.options).map(option => ({
                value: option.value,
                label: option.textContent,
                disabled: option.disabled
            }));
            
            this.config.options = options;
            
            // Set initial selection
            if (this.selectElement.multiple) {
                Array.from(this.selectElement.selectedOptions).forEach(option => {
                    this.selectedValues.add(option.value);
                });
            } else if (this.selectElement.value) {
                this.selectedValues.add(this.selectElement.value);
            }
        }
    }

    setupEventListeners() {
        // Click outside to close
        document.addEventListener('click', (event) => {
            if (!this.element.contains(event.target)) {
                this.isOpen = false;
            }
        });
        
        // Search input
        if (this.searchInput) {
            this.searchInput.addEventListener('input', (event) => {
                this.handleSearch(event.target.value);
            });
        }
    }

    updateState() {
        if (this.selectElement) {
            this.selectElement.disabled = this.config.disabled;
            this.selectElement.required = this.config.required;
        }
    }

    updateNativeSelect() {
        if (!this.selectElement) return;
        
        if (this.config.multiple) {
            Array.from(this.selectElement.options).forEach(option => {
                option.selected = this.selectedValues.has(option.value);
            });
        } else {
            this.selectElement.value = Array.from(this.selectedValues)[0] || '';
        }
        
        // Trigger change event
        this.selectElement.dispatchEvent(new Event('change', { bubbles: true }));
    }

    focusSearchInput() {
        if (this.searchInput && this.config.searchable) {
            setTimeout(() => this.searchInput.focus(), 0);
        }
    }

    // Public API
    getValue() {
        if (this.config.multiple) {
            return Array.from(this.selectedValues);
        } else {
            return Array.from(this.selectedValues)[0] || null;
        }
    }

    setValue(value) {
        this.selectedValues.clear();
        
        if (Array.isArray(value)) {
            value.forEach(v => this.selectedValues.add(v));
        } else if (value !== null && value !== undefined) {
            this.selectedValues.add(value);
        }
        
        this.updateNativeSelect();
        this.emit('change', { value: this.getValue() });
    }

    addOption(option) {
        this.config.options.push(option);
        this.emit('option-add', { option });
    }

    removeOption(value) {
        this.config.options = this.config.options.filter(opt => opt.value !== value);
        this.selectedValues.delete(value);
        this.updateNativeSelect();
        this.emit('option-remove', { value });
    }

    open() {
        this.isOpen = true;
        this.focusSearchInput();
        this.emit('open');
    }

    close() {
        this.isOpen = false;
        this.emit('close');
    }

    clear() {
        this.selectedValues.clear();
        this.updateNativeSelect();
        this.emit('clear');
    }

    focus() {
        this.triggerElement?.focus();
    }

    blur() {
        this.triggerElement?.blur();
        this.isOpen = false;
    }
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = WaveSelect;
}

// Register with ComponentRegistry if available
if (typeof window !== 'undefined' && window.ComponentRegistry) {
    window.ComponentRegistry.register('WaveSelect', WaveSelect);
}