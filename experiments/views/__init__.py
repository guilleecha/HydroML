# experiments/views/__init__.py

from .experiment_management_views import (
    MLExperimentUpdateView,
    MLExperimentDeleteView,
)
from .suite_views import (
    ExperimentSuiteCreateView,
    ExperimentSuiteDetailView,
)