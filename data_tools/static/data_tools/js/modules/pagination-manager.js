/**
 * PaginationManager - Pagination Logic Management
 * Responsabilidad única: Estado y navegación de paginación
 * 
 * Filosofía: Simple pagination state management, no mixed concerns
 */

class PaginationManager {
    constructor(gridController) {
        this.gridController = gridController;
        this.state = {
            currentPage: 1,
            totalPages: 1,
            pageSize: 25,
            totalRows: 0,
            availablePageSizes: [10, 25, 50, 100, 'All'],
            jumpToPage: 1
        };
        this.eventTarget = new EventTarget();
    }

    // === CORE PAGINATION OPERATIONS ===

    updateState(paginationInfo) {
        const { currentPage, totalPages, pageSize, totalRows } = paginationInfo;
        
        this.state.currentPage = currentPage || 1;
        this.state.totalPages = totalPages || 1;
        this.state.pageSize = pageSize || 25;
        this.state.totalRows = totalRows || 0;
        this.state.jumpToPage = currentPage || 1;
        
        this.dispatchEvent('pagination-state-updated', { ...this.state });
    }

    navigateToPage(page) {
        if (!this.isValidPage(page)) {
            console.warn(`Invalid page number: ${page}. Valid range: 1-${this.state.totalPages}`);
            return false;
        }

        const success = this.gridController.navigateToPage(page);
        if (success) {
            this.dispatchEvent('pagination-navigate', { page, previousPage: this.state.currentPage });
        }
        return success;
    }

    navigateToFirstPage() {
        return this.navigateToPage(1);
    }

    navigateToLastPage() {
        return this.navigateToPage(this.state.totalPages);
    }

    navigateToNextPage() {
        if (this.canGoNext()) {
            return this.navigateToPage(this.state.currentPage + 1);
        }
        return false;
    }

    navigateToPreviousPage() {
        if (this.canGoPrevious()) {
            return this.navigateToPage(this.state.currentPage - 1);
        }
        return false;
    }

    jumpToPageInput() {
        const page = parseInt(this.state.jumpToPage);
        if (this.isValidPage(page)) {
            return this.navigateToPage(page);
        } else {
            // Reset to current page if invalid
            this.state.jumpToPage = this.state.currentPage;
            this.dispatchEvent('pagination-jump-invalid', { 
                invalidPage: page, 
                resetTo: this.state.currentPage 
            });
            return false;
        }
    }

    changePageSize(newSize) {
        const size = newSize === 'All' ? this.state.totalRows : parseInt(newSize);
        
        if (!this.isValidPageSize(size)) {
            console.warn(`Invalid page size: ${newSize}`);
            return false;
        }

        const success = this.gridController.changePageSize(newSize);
        if (success) {
            this.dispatchEvent('pagination-page-size-changed', { 
                newSize: size, 
                previousSize: this.state.pageSize 
            });
        }
        return success;
    }

    // === VALIDATION METHODS ===

    isValidPage(page) {
        return Number.isInteger(page) && page >= 1 && page <= this.state.totalPages;
    }

    isValidPageSize(size) {
        return Number.isInteger(size) && size > 0 && size <= this.state.totalRows;
    }

    canGoNext() {
        return this.state.currentPage < this.state.totalPages;
    }

    canGoPrevious() {
        return this.state.currentPage > 1;
    }

    canGoToFirst() {
        return this.state.currentPage > 1;
    }

    canGoToLast() {
        return this.state.currentPage < this.state.totalPages;
    }

    // === CALCULATION METHODS ===

    getPageRange() {
        const { currentPage, pageSize, totalRows } = this.state;
        const startRow = (currentPage - 1) * pageSize + 1;
        const endRow = Math.min(currentPage * pageSize, totalRows);
        
        return { startRow, endRow };
    }

    getPageInfo() {
        return {
            ...this.state,
            ...this.getPageRange(),
            canGoNext: this.canGoNext(),
            canGoPrevious: this.canGoPrevious(),
            canGoToFirst: this.canGoToFirst(),
            canGoToLast: this.canGoToLast()
        };
    }

    calculateTotalPages(totalRows, pageSize) {
        if (pageSize === 'All' || pageSize >= totalRows) {
            return 1;
        }
        return Math.ceil(totalRows / pageSize);
    }

    // === STATE SETTERS ===

    setJumpToPage(page) {
        this.state.jumpToPage = parseInt(page) || 1;
        this.dispatchEvent('pagination-jump-page-changed', { jumpToPage: this.state.jumpToPage });
    }

    // === EVENT SYSTEM ===

    dispatchEvent(eventName, detail = {}) {
        this.eventTarget.dispatchEvent(new CustomEvent(eventName, { detail }));
    }

    addEventListener(eventName, handler) {
        this.eventTarget.addEventListener(eventName, handler);
    }

    removeEventListener(eventName, handler) {
        this.eventTarget.removeEventListener(eventName, handler);
    }

    // === GETTERS ===

    get currentState() {
        return { ...this.state };
    }

    get currentPage() {
        return this.state.currentPage;
    }

    get totalPages() {
        return this.state.totalPages;
    }

    get pageSize() {
        return this.state.pageSize;
    }

    get totalRows() {
        return this.state.totalRows;
    }

    get availablePageSizes() {
        return [...this.state.availablePageSizes];
    }

    // === UTILITY METHODS ===

    reset() {
        this.state = {
            currentPage: 1,
            totalPages: 1,
            pageSize: 25,
            totalRows: 0,
            availablePageSizes: [10, 25, 50, 100, 'All'],
            jumpToPage: 1
        };
        this.dispatchEvent('pagination-reset');
    }

    toString() {
        const { currentPage, totalPages, pageSize, totalRows } = this.state;
        return `Page ${currentPage}/${totalPages} (${pageSize} per page, ${totalRows} total)`;
    }
}

// Export for use in other modules
window.PaginationManager = PaginationManager;

// Export removed for script tag compatibility