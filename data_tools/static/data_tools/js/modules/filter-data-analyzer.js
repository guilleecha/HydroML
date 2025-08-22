/**
 * FilterDataAnalyzer - Data Analysis for Filters
 * Responsabilidad única: Análisis de datos para construcción de filtros
 * 
 * Filosofía: Pure data analysis, no UI concerns, optimized with caching
 */

class FilterDataAnalyzer {
    constructor(gridApi) {
        this.gridApi = gridApi;
        this.cache = new Map();
        this.cacheExpiry = new Map();
        this.defaultCacheDuration = 5 * 60 * 1000; // 5 minutes
    }

    // === COLUMN TYPE DETECTION ===

    detectColumnTypes(columnDefs) {
        if (!columnDefs || !Array.isArray(columnDefs)) {
            console.warn('Invalid column definitions for type detection');
            return {};
        }

        const types = {};
        
        columnDefs.forEach(col => {
            if (!col.field || col.field === 'rowNumber') return;
            
            types[col.field] = this.getColumnType(col.field);
        });

        return types;
    }

    getColumnType(field) {
        if (!field || !this.gridApi) return 'text';

        // Check cache first
        const cacheKey = `type_${field}`;
        if (this.isCacheValid(cacheKey)) {
            return this.cache.get(cacheKey);
        }

        let type = 'text'; // default
        
        try {
            // Sample the first few non-null values to determine type
            const sampleValues = [];
            let sampleCount = 0;
            const maxSamples = 50;

            this.gridApi.forEachNode((node) => {
                if (sampleCount >= maxSamples) return;
                
                const value = node.data[field];
                if (value !== null && value !== undefined && value !== '') {
                    sampleValues.push(value);
                    sampleCount++;
                }
            });

            if (sampleValues.length === 0) {
                type = 'text';
            } else {
                type = this.inferTypeFromSamples(sampleValues, field);
            }

        } catch (error) {
            console.error(`Error detecting type for field ${field}:`, error);
            type = 'text';
        }

        // Cache the result
        this.setCacheValue(cacheKey, type);
        return type;
    }

    inferTypeFromSamples(samples, field) {
        // Check for date fields by name patterns
        if (this.isDateField(field)) {
            return 'date';
        }

        // Check for numeric fields
        const numericCount = samples.filter(value => 
            this.isNumericValue(value)
        ).length;

        const numericRatio = numericCount / samples.length;

        if (numericRatio >= 0.8) {
            return 'number';
        }

        // Check for categorical fields (limited unique values)
        const uniqueValues = new Set(samples.map(v => String(v).toLowerCase()));
        const uniqueRatio = uniqueValues.size / samples.length;

        if (uniqueRatio <= 0.5 && uniqueValues.size <= 20) {
            return 'category';
        }

        return 'text';
    }

    isDateField(field) {
        const datePatterns = [
            /date/i, /time/i, /created/i, /updated/i, /modified/i,
            /timestamp/i, /datetime/i, /_at$/i, /_on$/i
        ];
        
        return datePatterns.some(pattern => pattern.test(field));
    }

    isNumericValue(value) {
        if (value === null || value === undefined || value === '') return false;
        
        // Try to parse as number
        const num = Number(value);
        return !isNaN(num) && isFinite(num);
    }

    // === DATA EXTRACTION ===

    getUniqueValues(field, maxValues = 100, useCache = true) {
        if (!field || !this.gridApi) {
            console.warn('Invalid field or grid API for unique values');
            return [];
        }

        const cacheKey = `unique_${field}_${maxValues}`;
        
        if (useCache && this.isCacheValid(cacheKey)) {
            return this.cache.get(cacheKey);
        }

        const uniqueValues = new Set();
        const values = [];

        try {
            this.gridApi.forEachNode((node) => {
                const value = node.data[field];
                
                if (value !== null && value !== undefined && value !== '') {
                    const stringValue = String(value).trim();
                    
                    if (!uniqueValues.has(stringValue)) {
                        uniqueValues.add(stringValue);
                        values.push(stringValue);
                        
                        // Stop if we've reached max values
                        if (values.length >= maxValues) {
                            return false; // Break forEachNode loop
                        }
                    }
                }
            });

            // Sort values alphabetically for better UX
            values.sort((a, b) => {
                // Try numeric sort first
                const numA = Number(a);
                const numB = Number(b);
                
                if (!isNaN(numA) && !isNaN(numB)) {
                    return numA - numB;
                }
                
                // Fallback to string sort
                return a.localeCompare(b);
            });

        } catch (error) {
            console.error(`Error getting unique values for field ${field}:`, error);
            return [];
        }

        // Cache the result
        this.setCacheValue(cacheKey, values);
        return values;
    }

    getNumericRange(field, useCache = true) {
        if (!field || !this.gridApi) {
            console.warn('Invalid field or grid API for numeric range');
            return { min: 0, max: 100 };
        }

        const cacheKey = `range_${field}`;
        
        if (useCache && this.isCacheValid(cacheKey)) {
            return this.cache.get(cacheKey);
        }

        let min = Infinity;
        let max = -Infinity;
        let hasNumericValues = false;

        try {
            this.gridApi.forEachNode((node) => {
                const value = node.data[field];
                
                if (value !== null && value !== undefined && value !== '') {
                    const numValue = Number(value);
                    
                    if (!isNaN(numValue) && isFinite(numValue)) {
                        hasNumericValues = true;
                        min = Math.min(min, numValue);
                        max = Math.max(max, numValue);
                    }
                }
            });

            // Fallback if no numeric values found
            if (!hasNumericValues) {
                min = 0;
                max = 100;
            }

        } catch (error) {
            console.error(`Error getting numeric range for field ${field}:`, error);
            min = 0;
            max = 100;
        }

        const range = { min, max };
        
        // Cache the result
        this.setCacheValue(cacheKey, range);
        return range;
    }

    getFilterSuggestions(field, query, limit = 10) {
        if (!field || !query || !this.gridApi) return [];

        const cacheKey = `suggestions_${field}_${query}_${limit}`;
        
        if (this.isCacheValid(cacheKey)) {
            return this.cache.get(cacheKey);
        }

        const suggestions = [];
        const queryLower = query.toLowerCase();
        const seen = new Set();

        try {
            this.gridApi.forEachNode((node) => {
                if (suggestions.length >= limit) return false;

                const value = node.data[field];
                
                if (value !== null && value !== undefined && value !== '') {
                    const stringValue = String(value).trim();
                    const stringLower = stringValue.toLowerCase();
                    
                    if (stringLower.includes(queryLower) && !seen.has(stringLower)) {
                        seen.add(stringLower);
                        suggestions.push(stringValue);
                    }
                }
            });

        } catch (error) {
            console.error(`Error getting suggestions for field ${field}:`, error);
            return [];
        }

        // Cache the result with shorter expiry for suggestions
        this.setCacheValue(cacheKey, suggestions, 60 * 1000); // 1 minute
        return suggestions;
    }

    // === DATA STATISTICS ===

    getFieldStatistics(field) {
        if (!field || !this.gridApi) return null;

        const cacheKey = `stats_${field}`;
        
        if (this.isCacheValid(cacheKey)) {
            return this.cache.get(cacheKey);
        }

        const stats = {
            totalCount: 0,
            nonNullCount: 0,
            nullCount: 0,
            uniqueCount: 0,
            type: this.getColumnType(field)
        };

        const uniqueValues = new Set();

        try {
            this.gridApi.forEachNode((node) => {
                stats.totalCount++;
                const value = node.data[field];
                
                if (value !== null && value !== undefined && value !== '') {
                    stats.nonNullCount++;
                    uniqueValues.add(String(value));
                } else {
                    stats.nullCount++;
                }
            });

            stats.uniqueCount = uniqueValues.size;
            stats.completeness = stats.totalCount > 0 
                ? (stats.nonNullCount / stats.totalCount) * 100 
                : 0;

        } catch (error) {
            console.error(`Error getting statistics for field ${field}:`, error);
            return null;
        }

        // Cache the result
        this.setCacheValue(cacheKey, stats);
        return stats;
    }

    // === CACHE MANAGEMENT ===

    setCacheValue(key, value, duration = null) {
        const expiry = Date.now() + (duration || this.defaultCacheDuration);
        this.cache.set(key, value);
        this.cacheExpiry.set(key, expiry);
    }

    isCacheValid(key) {
        if (!this.cache.has(key)) return false;
        
        const expiry = this.cacheExpiry.get(key);
        if (!expiry || Date.now() > expiry) {
            this.cache.delete(key);
            this.cacheExpiry.delete(key);
            return false;
        }
        
        return true;
    }

    clearCache() {
        this.cache.clear();
        this.cacheExpiry.clear();
    }

    invalidateFieldCache(field) {
        const keysToDelete = [];
        
        this.cache.forEach((value, key) => {
            if (key.includes(`_${field}_`) || key.includes(`_${field}`)) {
                keysToDelete.push(key);
            }
        });

        keysToDelete.forEach(key => {
            this.cache.delete(key);
            this.cacheExpiry.delete(key);
        });
    }

    getCacheStats() {
        const now = Date.now();
        let validEntries = 0;
        let expiredEntries = 0;

        this.cacheExpiry.forEach((expiry, key) => {
            if (now > expiry) {
                expiredEntries++;
            } else {
                validEntries++;
            }
        });

        return {
            totalEntries: this.cache.size,
            validEntries,
            expiredEntries,
            cacheHitRate: this.cacheHits / (this.cacheHits + this.cacheMisses) || 0
        };
    }

    // === CLEANUP ===

    destroy() {
        this.clearCache();
        this.gridApi = null;
    }

    // === GETTERS ===

    get cacheSize() {
        return this.cache.size;
    }

    get hasValidCache() {
        return this.cache.size > 0;
    }
}

// Export for use in other modules
window.FilterDataAnalyzer = FilterDataAnalyzer;

export default FilterDataAnalyzer;