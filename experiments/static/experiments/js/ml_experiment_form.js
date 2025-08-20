/**
 * ML Experiment Form JavaScript - LEGACY FILE
 * 
 * ⚠️ DEPRECATED: This file is no longer used for experiment form initialization.
 * 
 * As of the refactoring for slide-over panel consistency, all ML experiment 
 * forms are now created exclusively through the slide-over panel system.
 * 
 * The form initialization logic has been moved to:
 * - static/js/app.js -> initializeMLExperimentFormLogic() function
 * 
 * This file is kept for historical reference and potential future use,
 * but should NOT be loaded in any templates.
 * 
 * If you need to modify experiment form behavior, update the logic in:
 * - static/js/app.js (main application logic)
 * - experiments/templates/experiments/ml_experiment_form_partial.html (template)
 * - experiments/views/experiment_management_views.py -> ml_experiment_form_partial (view)
 * 
 * Last used in: Full-page experiment creation form (removed)
 * Replaced by: Dynamic slide-over panel system
 * Date deprecated: 2025-08-18
 */

console.warn('⚠️ ml_experiment_form.js is deprecated. Use app.js initializeMLExperimentFormLogic() instead.');