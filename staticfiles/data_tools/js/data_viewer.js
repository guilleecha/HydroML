// Data Viewer using AG Grid
document.addEventListener('DOMContentLoaded', function() {
    console.log('Data Viewer JS loaded');

    // DOM Elements
    const loadingSpinner = document.getElementById('loading-spinner');
    const errorContainer = document.getElementById('error-container');
    const errorMessage = document.getElementById('error-message');
    const gridContainer = document.getElementById('data-viewer-grid');

    // Get API URL from template
    const scriptData = JSON.parse(document.getElementById('data-viewer-script-data').textContent);
    const apiUrl = scriptData.dataSourceUrl;

    // Main function to load data and initialize AG Grid
    async function loadDataAndInitializeGrid() {
        try {
            console.log('Fetching data from:', apiUrl);
            
            // Fetch data from API
            const response = await fetch(apiUrl);

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `Server error: ${response.status}`);
            }

            const jsonData = await response.json();

            if (jsonData.error) {
                throw new Error(jsonData.error);
            }

            console.log('Data received:', jsonData);

            // Hide loading spinner
            console.log('Hiding loading spinner...');
            loadingSpinner.style.display = 'none';
            
            // Show grid container
            console.log('Showing grid container...');
            gridContainer.classList.remove('hidden');

            // Prepare column definitions for AG Grid
            const columnDefs = jsonData.columns.map(columnName => ({
                headerName: columnName,
                field: columnName,
                sortable: true,
                filter: true,
                resizable: true,
                minWidth: 150,
                flex: 1
            }));

            // Prepare row data
            const rowData = jsonData.data;

            // AG Grid configuration
            const gridOptions = {
                columnDefs: columnDefs,
                rowData: rowData,
                defaultColDef: {
                    sortable: true,
                    filter: true,
                    resizable: true,
                    minWidth: 100,
                    flex: 1
                },
                pagination: true,
                paginationPageSize: 25,
                paginationPageSizeSelector: [10, 25, 50, 100],
                animateRows: true,
                suppressCellFocus: true,
                rowSelection: 'single',
                onGridReady: function(event) {
                    console.log('AG Grid ready!');
                    // Auto-size columns to fit content
                    event.api.sizeColumnsToFit();
                },
                onFirstDataRendered: function(event) {
                    console.log('AG Grid first data rendered!');
                    // Auto-size columns when data is first loaded
                    event.api.sizeColumnsToFit();
                }
            };

            // Check if AG Grid is available
            if (typeof agGrid === 'undefined') {
                throw new Error('AG Grid library not loaded');
            }

            // Create the grid
            console.log('Creating AG Grid...');
            const grid = agGrid.createGrid(gridContainer, gridOptions);
            console.log('AG Grid created successfully:', grid);

            // Store grid instance globally for potential future use
            window.dataViewerGrid = grid;

        } catch (error) {
            console.error('Error loading data:', error);
            
            // Hide loading spinner
            loadingSpinner.style.display = 'none';
            
            // Show error message
            errorMessage.textContent = `Error loading data: ${error.message}`;
            errorContainer.classList.remove('hidden');
        }
    }

    // Initialize data loading
    loadDataAndInitializeGrid();
});