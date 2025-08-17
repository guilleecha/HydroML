# Neural Network Loading Animation - Usage Guide

## Overview

This document describes the sophisticated animated SVG loading indicator created for the HydroML application. The animation is inspired by a neural network structure and provides an elegant "thinking" effect during long-running operations.

## Components Created

### 1. `_loading_animation.html`
- **Location**: `core/templates/core/_loading_animation.html`
- **Description**: Self-contained animated SVG with neural network design
- **Features**:
  - Central pulsing core with breathing animation
  - 8 primary neural branches with branching paths
  - 8 secondary inner connections
  - Neural nodes at connection points with pulsing
  - Subtle rotating glow effect
  - Uses `currentColor` for easy theming

### 2. `_loading_overlay.html`
- **Location**: `core/templates/core/_loading_overlay.html`
- **Description**: Complete loading overlay component with backdrop
- **Features**:
  - Full-screen backdrop blur
  - Centered content container
  - Dynamic loading message support
  - Dark mode compatibility
  - Accessible with proper ARIA labels

### 3. Alpine.js Store Integration
- **Location**: `static/js/app.js`
- **Description**: Global state management for loading states
- **Methods**:
  - `startLoading(message)` - Show loading with custom message
  - `stopLoading()` - Hide loading overlay

## Usage Examples

### Basic Loading (Default Message)
```javascript
// Start loading
Alpine.store('app').startLoading();

// Stop loading
Alpine.store('app').stopLoading();
```

### Loading with Custom Message
```javascript
// Start loading with custom message
Alpine.store('app').startLoading('Training ML Model');

// Stop loading
Alpine.store('app').stopLoading();
```

### Complete AJAX Example
```javascript
// Before starting an experiment
Alpine.store('app').startLoading('Executing Experiment');

fetch('/api/experiments/run/', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => {
    // Handle success
    console.log('Experiment completed:', data);
})
.catch(error => {
    // Handle error
    console.error('Error:', error);
})
.finally(() => {
    // Always stop loading
    Alpine.store('app').stopLoading();
});
```

### Form Submission Example
```javascript
// In a form submission handler
submitExperiment() {
    Alpine.store('app').startLoading('Submitting Experiment');
    
    // Simulate form data preparation
    const formData = new FormData(this.$refs.experimentForm);
    
    fetch(this.$refs.experimentForm.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': this.getCsrfToken()
        }
    })
    .then(response => {
        if (!response.ok) throw new Error('Network response was not ok');
        return response.json();
    })
    .then(data => {
        // Handle success
        this.closePanel();
        window.location.reload();
    })
    .catch(error => {
        // Handle error
        this.showError(error.message);
    })
    .finally(() => {
        Alpine.store('app').stopLoading();
    });
}
```

### Data Upload Example
```javascript
// For file uploads
uploadDataset() {
    Alpine.store('app').startLoading('Uploading Dataset');
    
    const fileInput = this.$refs.fileInput;
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    
    fetch('/api/datasets/upload/', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        // Handle upload success
        this.refreshDatasetList();
    })
    .catch(error => {
        console.error('Upload failed:', error);
    })
    .finally(() => {
        Alpine.store('app').stopLoading();
    });
}
```

### Long-Running Process Example
```javascript
// For ML model training or data processing
trainModel() {
    Alpine.store('app').startLoading('Training Model - This may take several minutes');
    
    // Start training request
    fetch('/api/models/train/', {
        method: 'POST',
        body: JSON.stringify(this.modelConfig),
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': this.getCsrfToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.task_id) {
            // Poll for completion if using async tasks
            this.pollTaskStatus(data.task_id);
        }
    })
    .catch(error => {
        Alpine.store('app').stopLoading();
        this.showError('Training failed: ' + error.message);
    });
}
```

## Styling and Theming

### Default Colors
The animation uses `currentColor`, so it inherits the text color of its container:

```html
<!-- Blue loading indicator -->
<div class="text-brand-500">
    {% include 'core/_loading_animation.html' %}
</div>

<!-- Green loading indicator -->
<div class="text-green-500">
    {% include 'core/_loading_animation.html' %}
</div>

<!-- Dark mode compatible -->
<div class="text-brand-500 dark:text-darcula-accent">
    {% include 'core/_loading_animation.html' %}
</div>
```

### Custom Size
The SVG is scalable and responsive:

```html
<!-- Small loading indicator -->
<div class="w-16 h-16 text-brand-500">
    {% include 'core/_loading_animation.html' %}
</div>

<!-- Large loading indicator -->
<div class="w-32 h-32 text-brand-500">
    {% include 'core/_loading_animation.html' %}
</div>
```

## Integration Points

### Recommended Usage Locations
1. **Form Submissions**: All slide-over panels (Upload Data, New Project, New Experiment)
2. **AJAX Requests**: API calls, data fetching
3. **File Uploads**: Dataset uploads, file processing
4. **ML Operations**: Model training, predictions, analysis
5. **Navigation**: Page transitions, heavy content loading

### Performance Considerations
- The animation is lightweight and GPU-accelerated
- Uses native SMIL animations (no JavaScript required for animation)
- Minimal DOM impact with efficient SVG structure
- Automatically stops when overlay is hidden

## Accessibility Features

- **ARIA Labels**: Proper `role="dialog"` and `aria-modal="true"`
- **Screen Reader Support**: Descriptive aria-label on SVG
- **Keyboard Navigation**: Overlay traps focus appropriately
- **Color Independence**: Works with high contrast modes

## Browser Compatibility

- **Modern Browsers**: Full support (Chrome, Firefox, Safari, Edge)
- **SMIL Animations**: Supported in all modern browsers
- **Fallback**: If SMIL is not supported, static SVG still displays
- **Performance**: Optimized for 60fps animations

## Troubleshooting

### Common Issues

1. **Loading doesn't appear**:
   ```javascript
   // Check Alpine.js is loaded
   console.log(Alpine.store('app'));
   
   // Verify store initialization
   Alpine.store('app').startLoading('Test');
   ```

2. **Animation not smooth**:
   - Ensure CSS `will-change` properties are not conflicting
   - Check for excessive DOM manipulation during animation

3. **Colors not updating**:
   - Verify `currentColor` inheritance chain
   - Check Tailwind CSS compilation

### Debug Commands
```javascript
// Check loading state
console.log(Alpine.store('app').isLoading);

// Force start loading
Alpine.store('app').startLoading('Debug Test');

// Force stop loading
Alpine.store('app').stopLoading();
```

## Animation Details

### Primary Animation Timing
- **Central Core**: 2s pulsing cycle
- **Neural Branches**: 2.4s flowing animation with staggered delays
- **Inner Connections**: 1.8s dash animation
- **Node Pulsing**: 2s and 1.6s cycles for variety
- **Rotating Glow**: 3s rotation cycle

### Technical Specifications
- **SVG Viewbox**: 120x120 units
- **Animation Type**: SMIL (native SVG animations)
- **Color Support**: `currentColor` for full theme compatibility
- **Performance**: GPU-accelerated transforms and opacity changes
- **Accessibility**: Semantic markup with proper ARIA attributes

This neural network loading animation provides a sophisticated, performant, and accessible loading experience that enhances the user experience during long-running operations in the HydroML application.
