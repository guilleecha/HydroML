# core/constants.py
"""
Shared constants and choices for the HydroML application.
"""

# Machine Learning Model Choices
ML_MODEL_CHOICES = [
    ('RandomForestRegressor', 'Random Forest'),
    ('GradientBoostingRegressor', 'Gradient Boosting'),
    ('LinearRegression', 'Regresión Lineal'),
]

# For form display (includes empty option)
ML_MODEL_FORM_CHOICES = [
    ('', 'Selecciona un modelo...'),
] + ML_MODEL_CHOICES
