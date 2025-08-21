/**
 * DataComponent - Specialized component for data display and management
 * 
 * Extends BaseComponent with data-specific features like loading,
 * filtering, sorting, pagination, and real-time updates.
 */

class DataComponent extends BaseComponent {
  constructor(element, options = {}) {
    super(element, options);
    
    this.data = [];
    this.filteredData = [];
    this.sortConfig = { column: null, direction: 'asc' };
    this.filterConfig = {};
    this.pagination = { page: 1, perPage: 10, total: 0 };
    this.loading = false;
  }
  
  /**
   * Initialize data component
   */
  init() {
    super.init();
    
    this.setupDataLoading();
    this.setupFiltering();
    this.setupSorting();
    this.setupPagination();
    
    // Auto-load data if URL is provided
    if (this.options.dataUrl) {
      this.loadData();
    }
    
    return this;
  }
  
  /**
   * Initialize data-specific state
   */
  initializeState() {
    return {
      ...super.initializeState(),
      isLoading: false,
      hasData: false,
      isEmpty: true,
      dataCount: 0,
      filteredCount: 0,
      lastRefresh: null,
      sortColumn: null,
      sortDirection: 'asc',
      currentPage: 1,
      totalPages: 0,
      searchTerm: ''
    };
  }
  
  /**
   * Validate data-specific options
   */
  validateOptions(options) {
    const defaults = {
      ...super.validateOptions(options),
      dataUrl: null,
      autoRefresh: false,
      refreshInterval: 30000, // 30 seconds
      enableSearch: true,
      enableSort: true,
      enablePagination: true,
      perPage: 10,
      searchFields: [],
      dateFields: [],
      numberFields: [],
      trackChanges: false,
      realtime: false
    };
    
    return { ...defaults, ...options };
  }
  
  /**
   * Setup data loading functionality
   */
  setupDataLoading() {
    // Auto-refresh if enabled
    if (this.options.autoRefresh && this.options.refreshInterval > 0) {
      this.setupAutoRefresh();
    }
    
    // Real-time updates if enabled
    if (this.options.realtime) {
      this.setupRealtimeUpdates();
    }
  }
  
  /**
   * Load data from URL or source
   * @param {string} url - Optional URL to load from
   */
  async loadData(url = null) {
    const dataUrl = url || this.options.dataUrl;
    
    if (!dataUrl) {
      console.warn('[DataComponent] No data URL provided');
      return;
    }
    
    this.setLoading(true);
    
    try {
      this.emit('data:load-start', { url: dataUrl });
      
      const response = await fetch(dataUrl, {
        headers: {
          'Accept': 'application/json',
          'X-Requested-With': 'XMLHttpRequest'
        }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const result = await response.json();
      
      // Handle different response formats
      const data = result.data || result.results || result;
      
      this.setData(data);
      
      this.setState({
        lastRefresh: new Date().toISOString(),
        hasData: true,
        isEmpty: data.length === 0
      });
      
      this.emit('data:loaded', { data: this.data, count: this.data.length });
      
    } catch (error) {
      console.error('[DataComponent] Failed to load data:', error);
      
      this.setState({
        hasError: true,
        errorMessage: `Failed to load data: ${error.message}`
      });
      
      this.emit('data:load-error', { error });
      
    } finally {
      this.setLoading(false);
    }
  }
  
  /**
   * Set loading state
   * @param {boolean} loading - Loading state
   */
  setLoading(loading) {
    this.loading = loading;
    this.setState({ isLoading: loading });
    
    // Update UI loading indicators
    this.updateLoadingUI(loading);
    
    this.emit('data:loading-changed', { loading });
  }
  
  /**
   * Set data and process it
   * @param {Array} data - Data array
   */
  setData(data) {
    if (!Array.isArray(data)) {
      console.warn('[DataComponent] Data must be an array');
      data = [];
    }
    
    this.data = data;
    this.processData();
    
    this.setState({
      dataCount: this.data.length,
      hasData: this.data.length > 0,
      isEmpty: this.data.length === 0
    });
    
    this.emit('data:changed', { data: this.data });
  }
  
  /**
   * Process data (filter, sort, paginate)
   */
  processData() {
    let processedData = [...this.data];
    
    // Apply filters
    processedData = this.applyFilters(processedData);
    
    // Apply sorting
    processedData = this.applySorting(processedData);
    
    this.filteredData = processedData;
    
    // Update pagination
    this.updatePagination();
    
    this.setState({
      filteredCount: this.filteredData.length
    });
    
    this.emit('data:processed', {
      originalCount: this.data.length,
      filteredCount: this.filteredData.length
    });
  }
  
  /**
   * Setup filtering functionality
   */
  setupFiltering() {
    if (!this.options.enableSearch) return;
    
    // Setup search input if present
    const searchInput = this.element.querySelector('[data-search]');
    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        this.search(e.target.value);
      });
    }
    
    // Setup filter inputs
    const filterInputs = this.element.querySelectorAll('[data-filter]');
    filterInputs.forEach(input => {
      const filterField = input.getAttribute('data-filter');
      input.addEventListener('change', (e) => {
        this.setFilter(filterField, e.target.value);
      });
    });
  }
  
  /**
   * Search through data
   * @param {string} searchTerm - Search term
   */
  search(searchTerm) {
    this.setState({ searchTerm });
    
    if (!searchTerm.trim()) {
      delete this.filterConfig.search;
    } else {
      this.filterConfig.search = {
        term: searchTerm.toLowerCase(),
        fields: this.options.searchFields.length > 0 
          ? this.options.searchFields 
          : Object.keys(this.data[0] || {})
      };
    }
    
    this.processData();
    this.emit('data:search', { searchTerm, resultsCount: this.filteredData.length });
  }
  
  /**
   * Set a filter
   * @param {string} field - Field to filter on
   * @param {*} value - Filter value
   */
  setFilter(field, value) {
    if (!value || value === '') {
      delete this.filterConfig[field];
    } else {
      this.filterConfig[field] = value;
    }
    
    this.processData();
    this.emit('data:filter-changed', { field, value, filtersCount: Object.keys(this.filterConfig).length });
  }
  
  /**
   * Apply filters to data
   * @param {Array} data - Data to filter
   */
  applyFilters(data) {
    let filtered = data;
    
    Object.entries(this.filterConfig).forEach(([field, filter]) => {
      if (field === 'search') {
        // Text search across multiple fields
        filtered = filtered.filter(item => {
          return filter.fields.some(searchField => {
            const value = item[searchField];
            return value && String(value).toLowerCase().includes(filter.term);
          });
        });
      } else {
        // Exact match filter
        filtered = filtered.filter(item => {
          return String(item[field]).toLowerCase() === String(filter).toLowerCase();
        });
      }
    });
    
    return filtered;
  }
  
  /**
   * Setup sorting functionality
   */
  setupSorting() {
    if (!this.options.enableSort) return;
    
    // Setup sortable headers
    const sortableHeaders = this.element.querySelectorAll('[data-sort]');
    sortableHeaders.forEach(header => {
      const sortField = header.getAttribute('data-sort');
      
      header.style.cursor = 'pointer';
      header.addEventListener('click', () => {
        this.sort(sortField);
      });
    });
  }
  
  /**
   * Sort data by field
   * @param {string} field - Field to sort by
   */
  sort(field) {
    if (this.sortConfig.column === field) {
      // Toggle direction
      this.sortConfig.direction = this.sortConfig.direction === 'asc' ? 'desc' : 'asc';
    } else {
      // New field
      this.sortConfig.column = field;
      this.sortConfig.direction = 'asc';
    }
    
    this.setState({
      sortColumn: this.sortConfig.column,
      sortDirection: this.sortConfig.direction
    });
    
    this.processData();
    this.updateSortingUI();
    
    this.emit('data:sorted', {
      field: this.sortConfig.column,
      direction: this.sortConfig.direction
    });
  }
  
  /**
   * Apply sorting to data
   * @param {Array} data - Data to sort
   */
  applySorting(data) {
    if (!this.sortConfig.column) return data;
    
    return data.sort((a, b) => {
      const aVal = a[this.sortConfig.column];
      const bVal = b[this.sortConfig.column];
      
      // Handle different data types
      let comparison = 0;
      
      if (this.options.dateFields.includes(this.sortConfig.column)) {
        // Date comparison
        comparison = new Date(aVal) - new Date(bVal);
      } else if (this.options.numberFields.includes(this.sortConfig.column)) {
        // Number comparison
        comparison = parseFloat(aVal) - parseFloat(bVal);
      } else {
        // String comparison
        comparison = String(aVal).localeCompare(String(bVal));
      }
      
      return this.sortConfig.direction === 'asc' ? comparison : -comparison;
    });
  }
  
  /**
   * Setup pagination functionality
   */
  setupPagination() {
    if (!this.options.enablePagination) return;
    
    // Setup pagination controls
    const prevButton = this.element.querySelector('[data-page="prev"]');
    const nextButton = this.element.querySelector('[data-page="next"]');
    const pageInput = this.element.querySelector('[data-page="input"]');
    
    if (prevButton) {
      prevButton.addEventListener('click', () => this.previousPage());
    }
    
    if (nextButton) {
      nextButton.addEventListener('click', () => this.nextPage());
    }
    
    if (pageInput) {
      pageInput.addEventListener('change', (e) => {
        this.goToPage(parseInt(e.target.value));
      });
    }
  }
  
  /**
   * Update pagination info
   */
  updatePagination() {
    this.pagination.total = this.filteredData.length;
    this.pagination.perPage = this.options.perPage;
    
    const totalPages = Math.ceil(this.pagination.total / this.pagination.perPage);
    this.pagination.totalPages = totalPages;
    
    // Ensure current page is valid
    if (this.pagination.page > totalPages) {
      this.pagination.page = Math.max(1, totalPages);
    }
    
    this.setState({
      currentPage: this.pagination.page,
      totalPages: this.pagination.totalPages
    });
  }
  
  /**
   * Go to specific page
   * @param {number} page - Page number
   */
  goToPage(page) {
    const totalPages = this.pagination.totalPages;
    
    if (page < 1 || page > totalPages) {
      console.warn(`[DataComponent] Invalid page number: ${page}`);
      return;
    }
    
    this.pagination.page = page;
    this.setState({ currentPage: page });
    
    this.updatePaginationUI();
    this.emit('data:page-changed', { page, totalPages });
  }
  
  /**
   * Go to next page
   */
  nextPage() {
    if (this.pagination.page < this.pagination.totalPages) {
      this.goToPage(this.pagination.page + 1);
    }
  }
  
  /**
   * Go to previous page
   */
  previousPage() {
    if (this.pagination.page > 1) {
      this.goToPage(this.pagination.page - 1);
    }
  }
  
  /**
   * Get current page data
   */
  getCurrentPageData() {
    if (!this.options.enablePagination) {
      return this.filteredData;
    }
    
    const start = (this.pagination.page - 1) * this.pagination.perPage;
    const end = start + this.pagination.perPage;
    
    return this.filteredData.slice(start, end);
  }
  
  /**
   * Setup auto-refresh
   */
  setupAutoRefresh() {
    this.refreshInterval = setInterval(() => {
      this.loadData();
    }, this.options.refreshInterval);
    
    // Clean up on destroy
    this.on('component:destroyed', () => {
      if (this.refreshInterval) {
        clearInterval(this.refreshInterval);
      }
    });
  }
  
  /**
   * Setup real-time updates via WebSocket
   */
  setupRealtimeUpdates() {
    // This would integrate with Django Channels or similar
    // Placeholder for real-time functionality
    console.log('[DataComponent] Real-time updates would be set up here');
  }
  
  /**
   * Update loading UI indicators
   * @param {boolean} loading - Loading state
   */
  updateLoadingUI(loading) {
    const loadingIndicators = this.element.querySelectorAll('[data-loading]');
    
    loadingIndicators.forEach(indicator => {
      if (loading) {
        indicator.style.display = 'block';
      } else {
        indicator.style.display = 'none';
      }
    });
  }
  
  /**
   * Update sorting UI indicators
   */
  updateSortingUI() {
    const sortableHeaders = this.element.querySelectorAll('[data-sort]');
    
    sortableHeaders.forEach(header => {
      const field = header.getAttribute('data-sort');
      
      // Remove existing sort classes
      header.classList.remove('sort-asc', 'sort-desc');
      
      // Add current sort class
      if (field === this.sortConfig.column) {
        header.classList.add(`sort-${this.sortConfig.direction}`);
      }
    });
  }
  
  /**
   * Update pagination UI
   */
  updatePaginationUI() {
    const pageDisplay = this.element.querySelector('[data-page="display"]');
    const prevButton = this.element.querySelector('[data-page="prev"]');
    const nextButton = this.element.querySelector('[data-page="next"]');
    
    if (pageDisplay) {
      pageDisplay.textContent = `Page ${this.pagination.page} of ${this.pagination.totalPages}`;
    }
    
    if (prevButton) {
      prevButton.disabled = this.pagination.page <= 1;
    }
    
    if (nextButton) {
      nextButton.disabled = this.pagination.page >= this.pagination.totalPages;
    }
  }
  
  /**
   * Refresh data
   */
  refresh() {
    this.loadData();
  }
  
  /**
   * Clear all filters
   */
  clearFilters() {
    this.filterConfig = {};
    this.setState({ searchTerm: '' });
    
    // Clear UI filter inputs
    const filterInputs = this.element.querySelectorAll('[data-filter], [data-search]');
    filterInputs.forEach(input => {
      input.value = '';
    });
    
    this.processData();
    this.emit('data:filters-cleared');
  }
  
  /**
   * Export data in various formats
   * @param {string} format - Export format (json, csv)
   */
  exportData(format = 'json') {
    const data = this.filteredData;
    
    switch (format.toLowerCase()) {
      case 'json':
        return this.exportAsJSON(data);
      case 'csv':
        return this.exportAsCSV(data);
      default:
        console.warn(`[DataComponent] Unsupported export format: ${format}`);
        return null;
    }
  }
  
  /**
   * Export data as JSON
   * @param {Array} data - Data to export
   */
  exportAsJSON(data) {
    const jsonData = JSON.stringify(data, null, 2);
    const blob = new Blob([jsonData], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `data-export-${new Date().toISOString()}.json`;
    link.click();
    
    URL.revokeObjectURL(url);
    
    this.emit('data:exported', { format: 'json', count: data.length });
  }
  
  /**
   * Export data as CSV
   * @param {Array} data - Data to export
   */
  exportAsCSV(data) {
    if (data.length === 0) return;
    
    const headers = Object.keys(data[0]);
    const csvContent = [
      headers.join(','),
      ...data.map(row => 
        headers.map(header => 
          JSON.stringify(row[header] || '')
        ).join(',')
      )
    ].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `data-export-${new Date().toISOString()}.csv`;
    link.click();
    
    URL.revokeObjectURL(url);
    
    this.emit('data:exported', { format: 'csv', count: data.length });
  }
  
  /**
   * Cleanup data-specific resources
   */
  destroy() {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
    }
    
    this.data = [];
    this.filteredData = [];
    this.filterConfig = {};
    
    super.destroy();
  }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = DataComponent;
}

// Global registration for browser usage
if (typeof window !== 'undefined') {
  window.HydroML = window.HydroML || {};
  window.HydroML.DataComponent = DataComponent;
}