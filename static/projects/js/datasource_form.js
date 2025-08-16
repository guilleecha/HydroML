document.addEventListener('DOMContentLoaded', function() {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('id_file'); // Updated to use generic ID
    const defaultState = document.getElementById('drop-zone-default');
    const hoverState = document.getElementById('drop-zone-hover');
    const selectedState = document.getElementById('drop-zone-selected');
    const selectedFilename = document.getElementById('selected-filename');
    const submitButton = document.getElementById('submit-button');
    const submitText = document.getElementById('submit-text');
    const uploadForm = document.getElementById('upload-form');

    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    // Highlight drop zone when item is dragged over it
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });

    // Handle dropped files
    dropZone.addEventListener('drop', handleDrop, false);

    // Handle file selection via click
    fileInput.addEventListener('change', handleFileSelect, false);

    // Form submission handling
    uploadForm.addEventListener('submit', function(e) {
        submitButton.disabled = true;
        submitText.textContent = 'Subiendo...';
        submitButton.querySelector('svg').innerHTML = `
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15">
                <animateTransform attributeName="transform" attributeType="XML" type="rotate" from="0 12 12" to="360 12 12" dur="1s" repeatCount="indefinite"/>
            </path>
        `;
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    function highlight(e) {
        dropZone.classList.add('border-brand-300', 'bg-brand-50');
        dropZone.classList.remove('border-border-muted', 'bg-background-secondary');
        showState('hover');
    }

    function unhighlight(e) {
        dropZone.classList.remove('border-brand-300', 'bg-brand-50');
        dropZone.classList.add('border-border-muted', 'bg-background-secondary');
        
        if (!fileInput.files.length) {
            showState('default');
        } else {
            showState('selected');
        }
    }

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;

        if (files.length > 0) {
            fileInput.files = files;
            handleFileSelect();
        }
    }

    function handleFileSelect() {
        if (fileInput.files.length > 0) {
            const file = fileInput.files[0];
            selectedFilename.textContent = file.name;
            showState('selected');
            
            // Update drop zone styling for selected state
            dropZone.classList.remove('border-border-muted', 'bg-background-secondary');
            dropZone.classList.add('border-success-300', 'bg-success-50');
        }
    }

    function showState(state) {
        // Hide all states
        defaultState.classList.add('hidden');
        hoverState.classList.add('hidden');
        selectedState.classList.add('hidden');

        // Show requested state
        switch(state) {
            case 'default':
                defaultState.classList.remove('hidden');
                break;
            case 'hover':
                hoverState.classList.remove('hidden');
                break;
            case 'selected':
                selectedState.classList.remove('hidden');
                break;
        }
    }
});
