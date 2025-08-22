/**
 * APIClient - Unified HTTP Client
 * Responsabilidad única: Gestión centralizada de llamadas API con CSRF
 * 
 * Filosofía: DRY principle, single implementation of CSRF handling
 */

class APIClient {
    static getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
               document.querySelector('meta[name="csrf-token"]')?.content || '';
    }

    static getDefaultHeaders() {
        return {
            'Content-Type': 'application/json',
            'X-CSRFToken': this.getCSRFToken(),
            'X-Requested-With': 'XMLHttpRequest'
        };
    }

    static async request(url, options = {}) {
        const config = {
            headers: this.getDefaultHeaders(),
            ...options,
            headers: {
                ...this.getDefaultHeaders(),
                ...options.headers
            }
        };

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            } else {
                return await response.text();
            }
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    static async get(url, options = {}) {
        return this.request(url, {
            method: 'GET',
            ...options
        });
    }

    static async post(url, data = null, options = {}) {
        const config = {
            method: 'POST',
            ...options
        };

        if (data) {
            if (data instanceof FormData) {
                // Remove Content-Type for FormData, let browser set it
                const { 'Content-Type': removed, ...headers } = config.headers || {};
                config.headers = headers;
                config.body = data;
            } else {
                config.body = JSON.stringify(data);
            }
        }

        return this.request(url, config);
    }

    static async put(url, data = null, options = {}) {
        return this.post(url, data, {
            method: 'PUT',
            ...options
        });
    }

    static async delete(url, options = {}) {
        return this.request(url, {
            method: 'DELETE',
            ...options
        });
    }

    static async patch(url, data = null, options = {}) {
        return this.post(url, data, {
            method: 'PATCH',
            ...options
        });
    }
}

// Export for use in other modules
window.APIClient = APIClient;