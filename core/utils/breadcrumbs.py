# core/utils/breadcrumbs.py
"""
Utility functions for generating breadcrumb navigation.

This module provides helper functions to standardize breadcrumb creation
across the application, ensuring consistent navigation patterns.
"""

from django.urls import reverse


def create_breadcrumb(name, url=None):
    """
    Create a single breadcrumb item.
    
    Args:
        name (str): Display name for the breadcrumb
        url (str, optional): URL for the breadcrumb link. If None, renders as text only.
    
    Returns:
        dict: Breadcrumb item with 'name' and optionally 'url'
    """
    breadcrumb = {'name': name}
    if url:
        breadcrumb['url'] = url
    return breadcrumb


def create_project_breadcrumbs(project, current_page_name=None):
    """
    Create standard breadcrumbs for project-related pages.
    
    Args:
        project: Project model instance
        current_page_name (str, optional): Name of current page to add as final breadcrumb
    
    Returns:
        list: List of breadcrumb dictionaries
    """
    breadcrumbs = [
        create_breadcrumb('Proyectos', reverse('projects:project_list')),
        create_breadcrumb(project.name, reverse('projects:project_detail', kwargs={'pk': project.pk}))
    ]
    
    if current_page_name:
        breadcrumbs.append(create_breadcrumb(current_page_name))
    
    return breadcrumbs


def create_experiment_breadcrumbs(experiment, current_page_name=None):
    """
    Create standard breadcrumbs for experiment-related pages.
    
    Args:
        experiment: MLExperiment model instance
        current_page_name (str, optional): Name of current page to add as final breadcrumb
    
    Returns:
        list: List of breadcrumb dictionaries
    """
    breadcrumbs = [
        create_breadcrumb('Proyectos', reverse('projects:project_list')),
        create_breadcrumb(experiment.project.name, reverse('projects:project_detail', kwargs={'pk': experiment.project.pk})),
        create_breadcrumb(experiment.name, reverse('experiments:ml_experiment_detail', kwargs={'pk': experiment.pk}))
    ]
    
    if current_page_name:
        breadcrumbs.append(create_breadcrumb(current_page_name))
    
    return breadcrumbs


def create_basic_breadcrumbs(*items):
    """
    Create breadcrumbs from a list of (name, url) tuples.
    The last item should only have a name (no URL) to represent the current page.
    
    Args:
        *items: Variable arguments of either strings (for final item) or (name, url) tuples
    
    Returns:
        list: List of breadcrumb dictionaries
    """
    breadcrumbs = []
    
    for item in items:
        if isinstance(item, str):
            # Final item - just name, no URL
            breadcrumbs.append(create_breadcrumb(item))
        elif isinstance(item, (list, tuple)) and len(item) == 2:
            # (name, url) pair
            name, url = item
            breadcrumbs.append(create_breadcrumb(name, url))
        else:
            raise ValueError(f"Invalid breadcrumb item: {item}. Expected string or (name, url) pair.")
    
    return breadcrumbs
