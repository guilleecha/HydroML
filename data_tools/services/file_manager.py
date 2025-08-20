"""
Export File Manager - Secure file management for export operations.

This module handles file path generation, storage management, security,
and cleanup operations for export files.
"""

import os
import uuid
import hashlib
import logging
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


class ExportFileManager:
    """
    Manager for secure handling of export files.
    
    This class provides utilities for:
    - Secure file path generation
    - Storage directory management
    - File cleanup and lifecycle management
    - Security validation
    """
    
    def __init__(self):
        # Get export directory from settings
        self.base_export_dir = getattr(
            settings, 
            'EXPORT_FILES_ROOT', 
            os.path.join(settings.MEDIA_ROOT, 'exports')
        )
        
        # Ensure export directory exists
        os.makedirs(self.base_export_dir, exist_ok=True)
        
        # Maximum file size (default 2GB)
        self.max_file_size = getattr(settings, 'EXPORT_MAX_FILE_SIZE', 2 * 1024 * 1024 * 1024)
        
        # Allowed extensions
        self.allowed_extensions = {'.csv', '.json', '.parquet', '.xlsx'}
    
    def generate_file_path(self, export_job) -> str:
        """
        Generate a secure file path for an export job.
        
        Args:
            export_job: ExportJob instance
            
        Returns:
            str: Full path where the export file should be saved
        """
        try:
            # Create date-based subdirectory for organization
            date_dir = datetime.now().strftime('%Y/%m/%d')
            
            # Create user-specific subdirectory for security
            user_dir = self._get_user_directory_name(export_job.user)
            
            # Generate secure filename
            filename = self._generate_secure_filename(export_job)
            
            # Combine path components
            full_path = os.path.join(
                self.base_export_dir,
                user_dir,
                date_dir,
                filename
            )
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            logger.info(f"Generated export file path: {full_path}")
            
            return full_path
            
        except Exception as e:
            logger.error(f"Error generating file path for export job {export_job.id}: {str(e)}")
            raise Exception(f"Failed to generate file path: {str(e)}")
    
    def validate_file_path(self, file_path: str) -> bool:
        """
        Validate that a file path is safe and within allowed directories.
        
        Args:
            file_path: File path to validate
            
        Returns:
            bool: True if path is safe, False otherwise
        """
        try:
            # Resolve absolute path
            abs_path = os.path.abspath(file_path)
            abs_base = os.path.abspath(self.base_export_dir)
            
            # Check if file is within base directory
            if not abs_path.startswith(abs_base):
                logger.error(f"File path outside allowed directory: {file_path}")
                return False
            
            # Check file extension
            extension = Path(file_path).suffix.lower()
            if extension not in self.allowed_extensions:
                logger.error(f"Invalid file extension: {extension}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating file path {file_path}: {str(e)}")
            return False
    
    def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Get information about an export file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dict with file information or None if file doesn't exist
        """
        try:
            if not os.path.exists(file_path):
                return None
            
            stat = os.stat(file_path)
            
            return {
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime),
                'modified': datetime.fromtimestamp(stat.st_mtime),
                'extension': Path(file_path).suffix.lower(),
                'filename': Path(file_path).name,
                'exists': True
            }
            
        except Exception as e:
            logger.error(f"Error getting file info for {file_path}: {str(e)}")
            return None
    
    def delete_file(self, file_path: str, force: bool = False) -> bool:
        """
        Safely delete an export file.
        
        Args:
            file_path: Path to the file to delete
            force: If True, ignore validation errors
            
        Returns:
            bool: True if file was deleted successfully
        """
        try:
            if not force and not self.validate_file_path(file_path):
                logger.error(f"Cannot delete file - path validation failed: {file_path}")
                return False
            
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Export file deleted: {file_path}")
                
                # Try to clean up empty parent directories
                self._cleanup_empty_directories(os.path.dirname(file_path))
                
                return True
            else:
                logger.warning(f"File to delete not found: {file_path}")
                return True  # Consider it success if already gone
            
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {str(e)}")
            return False
    
    def cleanup_expired_files(self, retention_days: int = 7) -> Dict[str, int]:
        """
        Clean up expired export files.
        
        Args:
            retention_days: Number of days to retain files
            
        Returns:
            Dict with cleanup statistics
        """
        stats = {
            'files_deleted': 0,
            'bytes_freed': 0,
            'errors': 0
        }
        
        try:
            cutoff_date = timezone.now() - timedelta(days=retention_days)
            
            # Walk through all export directories
            for root, dirs, files in os.walk(self.base_export_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    try:
                        # Get file modification time
                        mtime = os.path.getmtime(file_path)
                        file_date = datetime.fromtimestamp(mtime)
                        
                        # Check if file is expired
                        if timezone.make_aware(file_date) < cutoff_date:
                            file_size = os.path.getsize(file_path)
                            
                            if self.delete_file(file_path, force=True):
                                stats['files_deleted'] += 1
                                stats['bytes_freed'] += file_size
                            else:
                                stats['errors'] += 1
                                
                    except Exception as e:
                        logger.error(f"Error processing file {file_path} during cleanup: {str(e)}")
                        stats['errors'] += 1
            
            logger.info(
                f"Export file cleanup completed. "
                f"Deleted {stats['files_deleted']} files, "
                f"freed {stats['bytes_freed']} bytes"
            )
            
        except Exception as e:
            logger.error(f"Error during export file cleanup: {str(e)}")
            stats['errors'] += 1
        
        return stats
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get storage statistics for export files.
        
        Returns:
            Dict with storage information
        """
        stats = {
            'total_files': 0,
            'total_size': 0,
            'by_extension': {},
            'by_date': {},
            'storage_path': self.base_export_dir
        }
        
        try:
            if not os.path.exists(self.base_export_dir):
                return stats
            
            for root, dirs, files in os.walk(self.base_export_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    try:
                        file_size = os.path.getsize(file_path)
                        extension = Path(file).suffix.lower()
                        
                        stats['total_files'] += 1
                        stats['total_size'] += file_size
                        
                        # Count by extension
                        if extension not in stats['by_extension']:
                            stats['by_extension'][extension] = {'count': 0, 'size': 0}
                        stats['by_extension'][extension]['count'] += 1
                        stats['by_extension'][extension]['size'] += file_size
                        
                        # Count by date (using file modification date)
                        mtime = os.path.getmtime(file_path)
                        date_key = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
                        
                        if date_key not in stats['by_date']:
                            stats['by_date'][date_key] = {'count': 0, 'size': 0}
                        stats['by_date'][date_key]['count'] += 1
                        stats['by_date'][date_key]['size'] += file_size
                        
                    except Exception as e:
                        logger.error(f"Error processing file {file_path} for stats: {str(e)}")
        
        except Exception as e:
            logger.error(f"Error getting storage stats: {str(e)}")
        
        return stats
    
    def check_storage_health(self) -> Dict[str, Any]:
        """
        Check the health of the export storage system.
        
        Returns:
            Dict with health information and recommendations
        """
        health = {
            'status': 'healthy',
            'issues': [],
            'recommendations': [],
            'storage_available': True,
            'permissions_ok': True
        }
        
        try:
            # Check if base directory exists and is writable
            if not os.path.exists(self.base_export_dir):
                health['issues'].append("Export directory does not exist")
                health['status'] = 'error'
                health['storage_available'] = False
            elif not os.access(self.base_export_dir, os.W_OK):
                health['issues'].append("Export directory is not writable")
                health['status'] = 'error'
                health['permissions_ok'] = False
            
            # Check disk space
            if health['storage_available']:
                statvfs = os.statvfs(self.base_export_dir)
                available_bytes = statvfs.f_frsize * statvfs.f_bavail
                
                # Warn if less than 1GB available
                if available_bytes < 1024 * 1024 * 1024:
                    health['issues'].append(f"Low disk space: {available_bytes / 1024 / 1024:.1f} MB available")
                    health['status'] = 'warning'
                    health['recommendations'].append("Consider cleaning up old export files")
            
            # Get storage stats
            stats = self.get_storage_stats()
            
            # Warn if too many files
            if stats['total_files'] > 10000:
                health['issues'].append(f"Large number of export files: {stats['total_files']}")
                health['status'] = 'warning'
                health['recommendations'].append("Consider reducing file retention period")
            
            # Warn if storage is getting large
            if stats['total_size'] > 10 * 1024 * 1024 * 1024:  # 10GB
                health['issues'].append(f"Large storage usage: {stats['total_size'] / 1024 / 1024 / 1024:.1f} GB")
                health['status'] = 'warning'
                health['recommendations'].append("Consider implementing automatic cleanup")
        
        except Exception as e:
            health['status'] = 'error'
            health['issues'].append(f"Health check failed: {str(e)}")
            logger.error(f"Error during storage health check: {str(e)}")
        
        return health
    
    # Private helper methods
    
    def _get_user_directory_name(self, user) -> str:
        """Generate a safe directory name for a user."""
        # Use user ID with hash for privacy and security
        user_hash = hashlib.md5(f"user_{user.id}".encode()).hexdigest()[:8]
        return f"user_{user.id}_{user_hash}"
    
    def _generate_secure_filename(self, export_job) -> str:
        """Generate a secure filename for an export job."""
        # Use job ID and timestamp for uniqueness
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Create base filename
        base_name = f"export_{export_job.id}_{timestamp}"
        
        # Add format extension
        extension = self._get_extension_for_format(export_job.format)
        
        return f"{base_name}{extension}"
    
    def _get_extension_for_format(self, format_type: str) -> str:
        """Get file extension for export format."""
        extensions = {
            'csv': '.csv',
            'json': '.json',
            'parquet': '.parquet',
            'excel': '.xlsx'
        }
        
        return extensions.get(format_type, '.dat')
    
    def _cleanup_empty_directories(self, directory: str):
        """Remove empty parent directories up to base export dir."""
        try:
            abs_directory = os.path.abspath(directory)
            abs_base = os.path.abspath(self.base_export_dir)
            
            # Don't delete the base export directory
            if abs_directory == abs_base:
                return
            
            # Only delete if within base directory
            if not abs_directory.startswith(abs_base):
                return
            
            # Remove if empty
            if os.path.exists(abs_directory) and not os.listdir(abs_directory):
                os.rmdir(abs_directory)
                logger.info(f"Removed empty directory: {abs_directory}")
                
                # Recursively try parent directory
                self._cleanup_empty_directories(os.path.dirname(abs_directory))
                
        except Exception as e:
            # Not critical, just log and continue
            logger.debug(f"Could not cleanup directory {directory}: {str(e)}")