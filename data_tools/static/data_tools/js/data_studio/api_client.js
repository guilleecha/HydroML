/**
 * API Client Module - Handles all backend API interactions and data fetching
 */

export class ApiClient {
    constructor() {
        this.baseUrl = '';
        this.csrfToken = this.getCSRFToken();
    }

    /**
     * Get CSRF token from DOM
     */
    getCSRFToken() {
        const tokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
        return tokenElement ? tokenElement.value : '';
    }

    /**
     * Generic fetch wrapper with error handling
     */
    async fetchWithErrorHandling(url, options = {}) {
        try {
            // Add CSRF token to headers if not already present
            const headers = {
                'X-CSRFToken': this.csrfToken,
                'Content-Type': 'application/json',
                ...options.headers
            };

            const response = await fetch(url, {
                ...options,
                headers
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`HTTP ${response.status}: ${errorText}`);
            }

            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            } else {
                return await response.text();
            }
        } catch (error) {
            console.error('Fetch error:', error);
            throw error;
        }
    }

    /**
     * Load dataset from file upload
     */
    async loadDataset(file) {
        try {
            console.log('Loading dataset:', file.name);
            
            const formData = new FormData();
            formData.append('file', file);
            
            const response = await fetch('/data_tools/load-dataset/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': this.csrfToken
                }
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Failed to load dataset: ${errorText}`);
            }

            const result = await response.json();
            console.log('Dataset loaded successfully:', result.data?.length || 0, 'rows');
            
            return result;
        } catch (error) {
            console.error('Error loading dataset:', error);
            throw error;
        }
    }

    /**
     * Apply transformation to current data
     */
    async applyTransformation(transformationType, params, data) {
        try {
            console.log('Applying transformation:', transformationType, params);
            
            const requestData = {
                transformation_type: transformationType,
                params: params,
                data: data
            };

            const result = await this.fetchWithErrorHandling('/data_tools/apply-transformation/', {
                method: 'POST',
                body: JSON.stringify(requestData)
            });

            console.log('Transformation applied successfully');
            return result;
        } catch (error) {
            console.error('Error applying transformation:', error);
            throw error;
        }
    }

    /**
     * Get analysis summary for current data
     */
    async getAnalysisSummary(data) {
        try {
            console.log('Getting analysis summary for', data?.length || 0, 'rows');
            
            const result = await this.fetchWithErrorHandling('/data_tools/get-analysis/', {
                method: 'POST',
                body: JSON.stringify({ data: data })
            });

            console.log('Analysis summary retrieved successfully');
            return result;
        } catch (error) {
            console.error('Error getting analysis summary:', error);
            throw error;
        }
    }

    /**
     * Generate charts based on current data
     */
    async generateChart(chartType, columns, data) {
        try {
            console.log('Generating chart:', chartType, 'with columns:', columns);
            
            const requestData = {
                chart_type: chartType,
                columns: columns,
                data: data
            };

            const result = await this.fetchWithErrorHandling('/data_tools/generate-chart/', {
                method: 'POST',
                body: JSON.stringify(requestData)
            });

            console.log('Chart generated successfully');
            return result;
        } catch (error) {
            console.error('Error generating chart:', error);
            throw error;
        }
    }

    /**
     * Execute statistical analysis
     */
    async executeStatisticalAnalysis(analysisType, params, data) {
        try {
            console.log('Executing statistical analysis:', analysisType);
            
            const requestData = {
                analysis_type: analysisType,
                params: params,
                data: data
            };

            const result = await this.fetchWithErrorHandling('/data_tools/statistical-analysis/', {
                method: 'POST',
                body: JSON.stringify(requestData)
            });

            console.log('Statistical analysis completed successfully');
            return result;
        } catch (error) {
            console.error('Error executing statistical analysis:', error);
            throw error;
        }
    }

    /**
     * Save recipe (transformation steps)
     */
    async saveRecipe(recipeData) {
        try {
            console.log('Saving recipe:', recipeData.name);
            
            const result = await this.fetchWithErrorHandling('/data_tools/save-recipe/', {
                method: 'POST',
                body: JSON.stringify(recipeData)
            });

            console.log('Recipe saved successfully');
            return result;
        } catch (error) {
            console.error('Error saving recipe:', error);
            throw error;
        }
    }

    /**
     * Load saved recipe
     */
    async loadRecipe(recipeId) {
        try {
            console.log('Loading recipe:', recipeId);
            
            const result = await this.fetchWithErrorHandling(`/data_tools/load-recipe/${recipeId}/`);

            console.log('Recipe loaded successfully');
            return result;
        } catch (error) {
            console.error('Error loading recipe:', error);
            throw error;
        }
    }

    /**
     * Get list of saved recipes
     */
    async getRecipeList() {
        try {
            console.log('Fetching recipe list');
            
            const result = await this.fetchWithErrorHandling('/data_tools/recipes/');

            console.log('Recipe list retrieved successfully');
            return result;
        } catch (error) {
            console.error('Error fetching recipe list:', error);
            throw error;
        }
    }

    /**
     * Export data in specified format
     */
    async exportData(data, format = 'csv', filename = 'exported_data') {
        try {
            console.log('Exporting data in', format, 'format');
            
            const requestData = {
                data: data,
                format: format,
                filename: filename
            };

            const response = await fetch('/data_tools/export-data/', {
                method: 'POST',
                body: JSON.stringify(requestData),
                headers: {
                    'X-CSRFToken': this.csrfToken,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Export failed: ${errorText}`);
            }

            // Handle file download
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${filename}.${format}`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);

            console.log('Data exported successfully');
            return { success: true };
        } catch (error) {
            console.error('Error exporting data:', error);
            throw error;
        }
    }

    /**
     * Validate data quality
     */
    async validateDataQuality(data) {
        try {
            console.log('Validating data quality for', data?.length || 0, 'rows');
            
            const result = await this.fetchWithErrorHandling('/data_tools/validate-data/', {
                method: 'POST',
                body: JSON.stringify({ data: data })
            });

            console.log('Data quality validation completed');
            return result;
        } catch (error) {
            console.error('Error validating data quality:', error);
            throw error;
        }
    }

    /**
     * Get column statistics
     */
    async getColumnStatistics(data, columnName) {
        try {
            console.log('Getting statistics for column:', columnName);
            
            const requestData = {
                data: data,
                column: columnName
            };

            const result = await this.fetchWithErrorHandling('/data_tools/column-stats/', {
                method: 'POST',
                body: JSON.stringify(requestData)
            });

            console.log('Column statistics retrieved successfully');
            return result;
        } catch (error) {
            console.error('Error getting column statistics:', error);
            throw error;
        }
    }

    /**
     * Perform data profiling
     */
    async profileData(data) {
        try {
            console.log('Profiling data with', data?.length || 0, 'rows');
            
            const result = await this.fetchWithErrorHandling('/data_tools/profile-data/', {
                method: 'POST',
                body: JSON.stringify({ data: data })
            });

            console.log('Data profiling completed successfully');
            return result;
        } catch (error) {
            console.error('Error profiling data:', error);
            throw error;
        }
    }

    /**
     * Find correlations in data
     */
    async findCorrelations(data, columns = null) {
        try {
            console.log('Finding correlations in data');
            
            const requestData = {
                data: data,
                columns: columns
            };

            const result = await this.fetchWithErrorHandling('/data_tools/correlations/', {
                method: 'POST',
                body: JSON.stringify(requestData)
            });

            console.log('Correlation analysis completed successfully');
            return result;
        } catch (error) {
            console.error('Error finding correlations:', error);
            throw error;
        }
    }

    /**
     * Detect outliers in data
     */
    async detectOutliers(data, method = 'iqr') {
        try {
            console.log('Detecting outliers using', method, 'method');
            
            const requestData = {
                data: data,
                method: method
            };

            const result = await this.fetchWithErrorHandling('/data_tools/detect-outliers/', {
                method: 'POST',
                body: JSON.stringify(requestData)
            });

            console.log('Outlier detection completed successfully');
            return result;
        } catch (error) {
            console.error('Error detecting outliers:', error);
            throw error;
        }
    }

    /**
     * Apply advanced preprocessing
     */
    async applyPreprocessing(data, steps) {
        try {
            console.log('Applying preprocessing steps:', steps);
            
            const requestData = {
                data: data,
                steps: steps
            };

            const result = await this.fetchWithErrorHandling('/data_tools/preprocess/', {
                method: 'POST',
                body: JSON.stringify(requestData)
            });

            console.log('Preprocessing completed successfully');
            return result;
        } catch (error) {
            console.error('Error applying preprocessing:', error);
            throw error;
        }
    }
}
