/**
 * FormComponent - Specialized component for form-related functionality
 * 
 * Extends BaseComponent with form-specific features like validation,
 * field management, submission handling, and form state tracking.
 */

class FormComponent extends BaseComponent {
  constructor(element, options = {}) {
    super(element, options);
    
    this.fields = new Map();
    this.validators = new Map();
    this.errors = new Map();
    this.isDirty = false;
    this.isSubmitting = false;
  }
  
  /**
   * Initialize form component
   */
  init() {
    super.init();
    
    this.setupFormFields();
    this.setupFormValidation();
    this.setupFormSubmission();
    
    return this;
  }
  
  /**
   * Initialize form-specific state
   */
  initializeState() {
    return {
      ...super.initializeState(),
      isValid: true,
      isDirty: false,
      isSubmitting: false,
      submitCount: 0,
      lastSubmitTime: null,
      formData: {},
      fieldErrors: {},
      globalErrors: []
    };
  }
  
  /**
   * Validate form-specific options
   */
  validateOptions(options) {
    const defaults = {
      ...super.validateOptions(options),
      validateOnInput: true,
      validateOnBlur: true,
      preventSubmitOnError: true,
      showErrorMessages: true,
      submitMethod: 'POST',
      submitUrl: null,
      csrfToken: null,
      autoReset: false,
      requireConfirmation: false
    };
    
    return { ...defaults, ...options };
  }
  
  /**
   * Setup form fields discovery and management
   */
  setupFormFields() {
    const formElements = this.element.querySelectorAll(
      'input, select, textarea, [x-data]'
    );
    
    formElements.forEach(field => {
      const fieldName = field.name || field.getAttribute('data-field');
      if (fieldName) {
        this.registerField(fieldName, field);
      }
    });
    
    this.emit('form:fields-registered', { fieldCount: this.fields.size });
  }
  
  /**
   * Register a form field
   * @param {string} name - Field name
   * @param {HTMLElement} element - Field element
   * @param {Object} options - Field options
   */
  registerField(name, element, options = {}) {
    const fieldConfig = {
      element,
      name,
      type: element.type || 'text',
      required: element.required || element.hasAttribute('required'),
      value: this.getFieldValue(element),
      initialValue: this.getFieldValue(element),
      isDirty: false,
      isValid: true,
      errors: [],
      ...options
    };
    
    this.fields.set(name, fieldConfig);
    
    // Setup field event listeners
    this.setupFieldListeners(fieldConfig);
    
    this.emit('form:field-registered', { field: fieldConfig });
  }
  
  /**
   * Setup event listeners for a specific field
   * @param {Object} fieldConfig - Field configuration
   */
  setupFieldListeners(fieldConfig) {
    const { element, name } = fieldConfig;
    
    // Input event for real-time validation
    if (this.options.validateOnInput) {
      element.addEventListener('input', (e) => {
        this.handleFieldInput(name, e);
      });
    }
    
    // Blur event for validation
    if (this.options.validateOnBlur) {
      element.addEventListener('blur', (e) => {
        this.handleFieldBlur(name, e);
      });
    }
    
    // Focus event
    element.addEventListener('focus', (e) => {
      this.handleFieldFocus(name, e);
    });
  }
  
  /**
   * Handle field input events
   * @param {string} fieldName - Name of the field
   * @param {Event} event - Input event
   */
  handleFieldInput(fieldName, event) {
    const field = this.fields.get(fieldName);
    if (!field) return;
    
    const newValue = this.getFieldValue(field.element);
    const previousValue = field.value;
    
    // Update field value
    field.value = newValue;
    field.isDirty = newValue !== field.initialValue;
    
    // Update form dirty state
    this.updateDirtyState();
    
    // Validate field if enabled
    if (this.options.validateOnInput) {
      this.validateField(fieldName);
    }
    
    this.emit('form:field-input', {
      fieldName,
      value: newValue,
      previousValue,
      field
    });
  }
  
  /**
   * Handle field blur events
   * @param {string} fieldName - Name of the field
   * @param {Event} event - Blur event
   */
  handleFieldBlur(fieldName, event) {
    if (this.options.validateOnBlur) {
      this.validateField(fieldName);
    }
    
    this.emit('form:field-blur', { fieldName, field: this.fields.get(fieldName) });
  }
  
  /**
   * Handle field focus events
   * @param {string} fieldName - Name of the field
   * @param {Event} event - Focus event
   */
  handleFieldFocus(fieldName, event) {
    // Clear field errors on focus
    this.clearFieldErrors(fieldName);
    
    this.emit('form:field-focus', { fieldName, field: this.fields.get(fieldName) });
  }
  
  /**
   * Get field value from element
   * @param {HTMLElement} element - Field element
   */
  getFieldValue(element) {
    switch (element.type) {
      case 'checkbox':
        return element.checked;
      case 'radio':
        return element.checked ? element.value : null;
      case 'file':
        return element.files;
      default:
        return element.value;
    }
  }
  
  /**
   * Setup form validation
   */
  setupFormValidation() {
    // Register common validators
    this.registerValidator('required', (value, field) => {
      if (field.required && (!value || value.toString().trim() === '')) {
        return 'This field is required';
      }
      return null;
    });
    
    this.registerValidator('email', (value, field) => {
      if (value && field.type === 'email') {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
          return 'Please enter a valid email address';
        }
      }
      return null;
    });
    
    this.registerValidator('minLength', (value, field) => {
      const minLength = field.element.getAttribute('minlength');
      if (minLength && value && value.length < parseInt(minLength)) {
        return `Minimum length is ${minLength} characters`;
      }
      return null;
    });
    
    this.registerValidator('maxLength', (value, field) => {
      const maxLength = field.element.getAttribute('maxlength');
      if (maxLength && value && value.length > parseInt(maxLength)) {
        return `Maximum length is ${maxLength} characters`;
      }
      return null;
    });
  }
  
  /**
   * Register a validator function
   * @param {string} name - Validator name
   * @param {Function} validator - Validator function
   */
  registerValidator(name, validator) {
    this.validators.set(name, validator);
  }
  
  /**
   * Validate a specific field
   * @param {string} fieldName - Name of field to validate
   */
  validateField(fieldName) {
    const field = this.fields.get(fieldName);
    if (!field) return false;
    
    const errors = [];
    
    // Run all validators
    this.validators.forEach((validator, validatorName) => {
      const error = validator(field.value, field);
      if (error) {
        errors.push({ validator: validatorName, message: error });
      }
    });
    
    // Update field validation state
    field.isValid = errors.length === 0;
    field.errors = errors;
    
    // Update global errors map
    if (errors.length > 0) {
      this.errors.set(fieldName, errors);
    } else {
      this.errors.delete(fieldName);
    }
    
    // Update form validity
    this.updateFormValidity();
    
    // Show/hide error messages
    if (this.options.showErrorMessages) {
      this.showFieldErrors(fieldName, errors);
    }
    
    this.emit('form:field-validated', {
      fieldName,
      isValid: field.isValid,
      errors
    });
    
    return field.isValid;
  }
  
  /**
   * Validate entire form
   */
  validateForm() {
    let isValid = true;
    
    this.fields.forEach((field, fieldName) => {
      if (!this.validateField(fieldName)) {
        isValid = false;
      }
    });
    
    this.setState({ isValid });
    
    this.emit('form:validated', {
      isValid,
      errors: Object.fromEntries(this.errors)
    });
    
    return isValid;
  }
  
  /**
   * Update form dirty state
   */
  updateDirtyState() {
    const isDirty = Array.from(this.fields.values()).some(field => field.isDirty);
    
    if (this.isDirty !== isDirty) {
      this.isDirty = isDirty;
      this.setState({ isDirty });
      this.emit('form:dirty-changed', { isDirty });
    }
  }
  
  /**
   * Update form validity state
   */
  updateFormValidity() {
    const isValid = this.errors.size === 0;
    this.setState({ isValid });
  }
  
  /**
   * Setup form submission handling
   */
  setupFormSubmission() {
    this.element.addEventListener('submit', (e) => {
      e.preventDefault();
      this.handleSubmit(e);
    });
  }
  
  /**
   * Handle form submission
   * @param {Event} event - Submit event
   */
  async handleSubmit(event) {
    if (this.isSubmitting) {
      console.warn('[FormComponent] Form is already submitting');
      return;
    }
    
    // Validate form before submission
    if (!this.validateForm() && this.options.preventSubmitOnError) {
      this.emit('form:submit-prevented', { reason: 'validation-failed' });
      return;
    }
    
    // Check for confirmation if required
    if (this.options.requireConfirmation) {
      const confirmed = await this.requestConfirmation();
      if (!confirmed) {
        this.emit('form:submit-prevented', { reason: 'user-cancelled' });
        return;
      }
    }
    
    this.isSubmitting = true;
    this.setState({ isSubmitting: true });
    
    try {
      const formData = this.getFormData();
      
      this.emit('form:submit-start', { formData });
      
      const result = await this.submitForm(formData);
      
      this.setState({
        isSubmitting: false,
        submitCount: this.state.submitCount + 1,
        lastSubmitTime: new Date().toISOString()
      });
      
      this.emit('form:submit-success', { result, formData });
      
      if (this.options.autoReset) {
        this.resetForm();
      }
      
    } catch (error) {
      this.setState({ isSubmitting: false });
      this.handleSubmitError(error);
    }
    
    this.isSubmitting = false;
  }
  
  /**
   * Get form data as object
   */
  getFormData() {
    const formData = {};
    
    this.fields.forEach((field, fieldName) => {
      formData[fieldName] = field.value;
    });
    
    return formData;
  }
  
  /**
   * Submit form data
   * @param {Object} formData - Form data to submit
   */
  async submitForm(formData) {
    const url = this.options.submitUrl || this.element.action;
    const method = this.options.submitMethod || this.element.method || 'POST';
    
    const requestOptions = {
      method,
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(formData)
    };
    
    // Add CSRF token if available
    if (this.options.csrfToken) {
      requestOptions.headers['X-CSRFToken'] = this.options.csrfToken;
    }
    
    const response = await fetch(url, requestOptions);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  }
  
  /**
   * Handle submission errors
   * @param {Error} error - Submission error
   */
  handleSubmitError(error) {
    console.error('[FormComponent] Submission error:', error);
    
    this.setState({
      hasError: true,
      errorMessage: error.message
    });
    
    this.emit('form:submit-error', { error });
  }
  
  /**
   * Request user confirmation for form submission
   */
  async requestConfirmation() {
    return confirm('Are you sure you want to submit this form?');
  }
  
  /**
   * Show field errors in UI
   * @param {string} fieldName - Field name
   * @param {Array} errors - Array of error objects
   */
  showFieldErrors(fieldName, errors) {
    const field = this.fields.get(fieldName);
    if (!field) return;
    
    // Remove existing error messages
    this.clearFieldErrors(fieldName);
    
    if (errors.length > 0) {
      field.element.classList.add('error', 'border-error');
      field.element.setAttribute('aria-invalid', 'true');
      
      // Create error message element
      const errorElement = document.createElement('div');
      errorElement.className = 'field-error text-error text-sm mt-1';
      errorElement.setAttribute('data-field-error', fieldName);
      errorElement.textContent = errors[0].message;
      
      // Insert error message after field
      field.element.parentNode.insertBefore(errorElement, field.element.nextSibling);
    }
  }
  
  /**
   * Clear field errors from UI
   * @param {string} fieldName - Field name
   */
  clearFieldErrors(fieldName) {
    const field = this.fields.get(fieldName);
    if (!field) return;
    
    field.element.classList.remove('error', 'border-error');
    field.element.removeAttribute('aria-invalid');
    
    // Remove error message element
    const errorElement = document.querySelector(`[data-field-error="${fieldName}"]`);
    if (errorElement) {
      errorElement.remove();
    }
  }
  
  /**
   * Reset form to initial state
   */
  resetForm() {
    this.fields.forEach((field, fieldName) => {
      field.element.value = field.initialValue;
      field.value = field.initialValue;
      field.isDirty = false;
      field.isValid = true;
      field.errors = [];
      
      this.clearFieldErrors(fieldName);
    });
    
    this.errors.clear();
    this.isDirty = false;
    
    this.setState({
      isValid: true,
      isDirty: false,
      hasError: false,
      errorMessage: null,
      fieldErrors: {},
      globalErrors: []
    });
    
    this.emit('form:reset');
  }
  
  /**
   * Cleanup form-specific resources
   */
  destroy() {
    this.fields.clear();
    this.validators.clear();
    this.errors.clear();
    
    super.destroy();
  }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = FormComponent;
}

// Global registration for browser usage
if (typeof window !== 'undefined') {
  window.HydroML = window.HydroML || {};
  window.HydroML.FormComponent = FormComponent;
}