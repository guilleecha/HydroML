/**
 * Enhanced API Client for Data Studio with WebSocket support
 * Provides comprehensive API integration with real-time updates
 */

class EnhancedDataStudioAPI {
    constructor(datasourceId, options = {}) {
        this.datasourceId = datasourceId;
        this.baseUrl = '/data-tools/api/studio/' + datasourceId + '/';
        this.bulkUrl = '/data-tools/api/bulk-operation/';
        this.websocketUrl = this.getWebSocketUrl();
        this.options = {
            enableWebSocket: true,
            autoReconnect: true,
            maxReconnectAttempts: 5,
            reconnectDelay: 1000,
            ...options
        };
        
        // WebSocket state
        this.ws = null;
        this.wsConnected = false;
        this.reconnectAttempts = 0;
        this.subscriptions = new Set();
        
        // Event listeners
        this.eventListeners = {
            connection: [],
            disconnection: [],
            transformation_progress: [],
            bulk_progress: [],
            session_update: [],
            data_preview: [],
            error: [],
            notification: []
        };
        
        // Request interceptors
        this.requestInterceptors = [];
        this.responseInterceptors = [];
        
        if (this.options.enableWebSocket) {
            this.initializeWebSocket();
        }
    }
    
    /**
     * WebSocket Management
     */
    getWebSocketUrl() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.host;
        return `${protocol}//${host}/ws/data-studio/${this.datasourceId}/`;
    }
    
    initializeWebSocket() {
        try {
            this.ws = new WebSocket(this.websocketUrl);
            
            this.ws.onopen = () => {
                console.log('Enhanced API: WebSocket connected');
                this.wsConnected = true;
                this.reconnectAttempts = 0;
                this.emit('connection', { timestamp: Date.now() });
                
                // Resubscribe to previous subscriptions
                this.subscriptions.forEach(operationId => {
                    this.subscribeToOperation(operationId);
                });
            };
            
            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleWebSocketMessage(data);
                } catch (error) {
                    console.error('Enhanced API: Failed to parse WebSocket message:', error);
                }
            };
            
            this.ws.onclose = () => {
                console.log('Enhanced API: WebSocket disconnected');
                this.wsConnected = false;
                this.emit('disconnection', { timestamp: Date.now() });
                
                if (this.options.autoReconnect && this.reconnectAttempts < this.options.maxReconnectAttempts) {
                    setTimeout(() => {
                        this.reconnectAttempts++;
                        console.log(`Enhanced API: Reconnecting... (${this.reconnectAttempts}/${this.options.maxReconnectAttempts})`);
                        this.initializeWebSocket();
                    }, this.options.reconnectDelay * Math.pow(2, this.reconnectAttempts));
                }
            };
            
            this.ws.onerror = (error) => {
                console.error('Enhanced API: WebSocket error:', error);
                this.emit('error', { type: 'websocket', error: error.message });
            };
            
        } catch (error) {
            console.error('Enhanced API: Failed to initialize WebSocket:', error);
        }
    }
    
    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'transformation_progress':
                this.emit('transformation_progress', data);
                break;
            case 'bulk_progress':
                this.emit('bulk_progress', data);
                break;
            case 'session_update':
                this.emit('session_update', data);
                break;
            case 'data_preview':
                this.emit('data_preview', data);
                break;
            case 'error':
                this.emit('error', data);
                break;
            case 'notification':
                this.emit('notification', data);
                break;
            case 'pong':
                // Handle ping/pong for connection health
                break;
            default:
                console.log('Enhanced API: Unknown WebSocket message type:', data.type);
        }
    }
    
    subscribeToOperation(operationId) {
        this.subscriptions.add(operationId);
        if (this.wsConnected) {
            this.ws.send(JSON.stringify({
                type: 'subscribe_to_operation',
                operation_id: operationId
            }));
        }
    }
    
    unsubscribeFromOperation(operationId) {
        this.subscriptions.delete(operationId);
        if (this.wsConnected) {
            this.ws.send(JSON.stringify({
                type: 'unsubscribe_from_operation',
                operation_id: operationId
            }));
        }
    }
    
    ping() {
        if (this.wsConnected) {
            this.ws.send(JSON.stringify({ type: 'ping' }));
        }
    }
    
    /**
     * Event Management
     */
    on(event, callback) {
        if (this.eventListeners[event]) {
            this.eventListeners[event].push(callback);
        } else {
            console.warn(`Enhanced API: Unknown event type: ${event}`);
        }
    }
    
    off(event, callback) {
        if (this.eventListeners[event]) {
            const index = this.eventListeners[event].indexOf(callback);
            if (index > -1) {
                this.eventListeners[event].splice(index, 1);
            }
        }
    }
    
    emit(event, data) {
        if (this.eventListeners[event]) {
            this.eventListeners[event].forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error(`Enhanced API: Error in ${event} callback:`, error);
                }
            });
        }
    }
    
    /**
     * HTTP Request Management
     */
    addRequestInterceptor(interceptor) {
        this.requestInterceptors.push(interceptor);
    }
    
    addResponseInterceptor(interceptor) {
        this.responseInterceptors.push(interceptor);
    }
    
    async request(url, options = {}) {
        // Apply request interceptors
        let requestOptions = {
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken(),
                ...options.headers
            },
            ...options
        };
        
        for (const interceptor of this.requestInterceptors) {
            requestOptions = await interceptor(requestOptions);
        }
        
        try {
            const response = await fetch(url, requestOptions);
            let result = response;
            
            // Apply response interceptors
            for (const interceptor of this.responseInterceptors) {
                result = await interceptor(result);
            }
            
            // Handle rate limiting
            if (response.status === 429) {
                const retryAfter = response.headers.get('Retry-After');
                throw new APIError('Rate limit exceeded', 429, { retryAfter });
            }
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new APIError(errorData.error || 'API request failed', response.status, errorData);
            }
            
            return await response.json();
            
        } catch (error) {
            if (error instanceof APIError) {
                throw error;
            }
            throw new APIError('Network error', 0, { originalError: error });
        }
    }
    
    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
               document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
    }
    
    /**
     * Session Management APIs
     */
    async initializeSession() {
        return this.request(this.baseUrl + 'session/initialize/', {
            method: 'POST'
        });
    }
    
    async getSessionStatus() {
        return this.request(this.baseUrl + 'session/status/', {
            method: 'GET'
        });
    }
    
    async undoOperation() {
        return this.request(this.baseUrl + 'session/undo/', {
            method: 'POST'
        });
    }
    
    async redoOperation() {
        return this.request(this.baseUrl + 'session/redo/', {
            method: 'POST'
        });
    }
    
    async saveSession(name = null, description = null) {
        return this.request(this.baseUrl + 'session/save/', {
            method: 'POST',
            body: JSON.stringify({ name, description })
        });
    }
    
    async clearSession() {
        return this.request(this.baseUrl + 'session/clear/', {
            method: 'POST'
        });
    }
    
    /**
     * Bulk Operations APIs
     */
    async startBulkOperation(operationType, items, parameters = {}, options = {}) {
        const result = await this.request(this.baseUrl + 'bulk/', {
            method: 'POST',
            body: JSON.stringify({
                operation_type: operationType,
                items: items,
                parameters: parameters,
                options: options
            })
        });
        
        // Auto-subscribe to operation updates
        if (result.success && result.data.operation_id) {
            this.subscribeToOperation(result.data.operation_id);
        }
        
        return result;
    }
    
    async getBulkOperationStatus(operationId) {
        return this.request(this.bulkUrl + operationId + '/status/', {
            method: 'GET'
        });
    }
    
    async cancelBulkOperation(operationId) {
        const result = await this.request(this.bulkUrl + operationId + '/cancel/', {
            method: 'POST'
        });
        
        // Unsubscribe from updates
        this.unsubscribeFromOperation(operationId);
        
        return result;
    }
    
    /**
     * Transformation APIs
     */
    async applyImputation(columns, method, customValue = null) {
        return this.request(this.baseUrl + 'transform/imputation/', {
            method: 'POST',
            body: JSON.stringify({
                columns: columns,
                method: method,
                custom_value: customValue
            })
        });
    }
    
    async applyEncoding(columns, encodingType) {
        return this.request(this.baseUrl + 'transform/encoding/', {
            method: 'POST',
            body: JSON.stringify({
                columns: columns,
                encoding_type: encodingType
            })
        });
    }
    
    async applyScaling(columns, scalerType) {
        return this.request(this.baseUrl + 'transform/scaling/', {
            method: 'POST',
            body: JSON.stringify({
                columns: columns,
                scaler_type: scalerType
            })
        });
    }
    
    /**
     * Data Access APIs
     */
    async getDataPreview(page = 1, pageSize = 25, sortBy = null, sortOrder = 'asc') {
        const params = new URLSearchParams({
            page: page.toString(),
            page_size: pageSize.toString()
        });
        
        if (sortBy) {
            params.append('sort_by', sortBy);
            params.append('sort_order', sortOrder);
        }
        
        return this.request(this.baseUrl + 'data/?' + params.toString(), {
            method: 'GET'
        });
    }
    
    /**
     * Monitoring APIs
     */
    async getAPIStats() {
        return this.request('/data-tools/api/stats/', {
            method: 'GET'
        });
    }
    
    async checkAPIHealth() {
        return this.request('/data-tools/api/health/', {
            method: 'GET'
        });
    }
    
    /**
     * Utility Methods
     */
    disconnect() {
        if (this.ws) {
            this.options.autoReconnect = false; // Prevent reconnection
            this.ws.close();
        }
    }
    
    reconnect() {
        if (!this.wsConnected) {
            this.reconnectAttempts = 0;
            this.initializeWebSocket();
        }
    }
    
    isConnected() {
        return this.wsConnected;
    }
    
    getConnectionInfo() {
        return {
            websocket: this.wsConnected,
            subscriptions: Array.from(this.subscriptions),
            reconnectAttempts: this.reconnectAttempts
        };
    }
}

/**
 * Custom API Error class
 */
class APIError extends Error {
    constructor(message, status = 0, details = {}) {
        super(message);
        this.name = 'APIError';
        this.status = status;
        this.details = details;
    }
}

/**
 * Bulk Operation Helper
 */
class BulkOperationHelper {
    constructor(apiClient) {
        this.api = apiClient;
        this.activeOperations = new Map();
    }
    
    async deleteRows(rowIndices, options = {}) {
        const operation = await this.api.startBulkOperation('delete_rows', rowIndices, {}, options);
        if (operation.success) {
            this.trackOperation(operation.data.operation_id, 'delete_rows');
        }
        return operation;
    }
    
    async updateCells(updates, options = {}) {
        const operation = await this.api.startBulkOperation('update_cells', updates, {}, options);
        if (operation.success) {
            this.trackOperation(operation.data.operation_id, 'update_cells');
        }
        return operation;
    }
    
    async applyTransformations(transformations, options = {}) {
        const operation = await this.api.startBulkOperation('apply_transformations', transformations, {}, options);
        if (operation.success) {
            this.trackOperation(operation.data.operation_id, 'transformations');
        }
        return operation;
    }
    
    async columnOperations(operations, options = {}) {
        const operation = await this.api.startBulkOperation('column_operations', operations, {}, options);
        if (operation.success) {
            this.trackOperation(operation.data.operation_id, 'column_operations');
        }
        return operation;
    }
    
    trackOperation(operationId, type) {
        this.activeOperations.set(operationId, {
            type,
            startTime: Date.now(),
            status: 'running'
        });
        
        // Listen for progress updates
        this.api.on('bulk_progress', (data) => {
            if (data.operation_id === operationId) {
                const operation = this.activeOperations.get(operationId);
                if (operation) {
                    operation.status = data.status;
                    operation.progress = data.processed / data.total;
                    operation.processed = data.processed;
                    operation.total = data.total;
                    operation.errors = data.errors;
                    
                    if (data.status === 'completed' || data.status === 'failed') {
                        operation.endTime = Date.now();
                        operation.duration = operation.endTime - operation.startTime;
                    }
                }
            }
        });
    }
    
    getOperationStatus(operationId) {
        return this.activeOperations.get(operationId);
    }
    
    getAllOperations() {
        return Object.fromEntries(this.activeOperations);
    }
}

// Make classes globally available
window.EnhancedDataStudioAPI = EnhancedDataStudioAPI;
window.BulkOperationHelper = BulkOperationHelper;
window.APIError = APIError;