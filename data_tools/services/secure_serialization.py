"""
Secure serialization module for DataFrame storage in Redis cache.
Replaces pickle with JSON + compression for security and performance.
"""

import json
import gzip
import logging
from typing import Optional, Dict, Any, List
from io import StringIO, BytesIO

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class DataFrameJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for pandas DataFrames and numpy data types."""
    
    def default(self, obj):
        if isinstance(obj, pd.DataFrame):
            return self.encode_dataframe(obj)
        elif isinstance(obj, pd.Series):
            return self.encode_series(obj)
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif pd.isna(obj):
            return None
        elif isinstance(obj, (pd.Timestamp, pd.Timedelta)):
            return str(obj)
        return super().default(obj)
    
    def encode_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Encode DataFrame as JSON-serializable dictionary."""
        return {
            '__type__': 'DataFrame',
            'columns': list(df.columns),
            'index': list(df.index),
            'data': df.values.tolist(),
            'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
            'shape': df.shape
        }
    
    def encode_series(self, series: pd.Series) -> Dict[str, Any]:
        """Encode Series as JSON-serializable dictionary."""
        return {
            '__type__': 'Series',
            'name': series.name,
            'index': list(series.index),
            'data': series.values.tolist(),
            'dtype': str(series.dtype)
        }


class DataFrameJSONDecoder:
    """Custom JSON decoder for pandas DataFrames and numpy data types."""
    
    @staticmethod
    def decode_dataframe(data: Dict[str, Any]) -> pd.DataFrame:
        """Decode dictionary back to DataFrame."""
        df = pd.DataFrame(
            data=data['data'],
            columns=data['columns'],
            index=data['index']
        )
        
        # Restore original data types
        for col, dtype_str in data['dtypes'].items():
            try:
                if dtype_str.startswith('datetime'):
                    df[col] = pd.to_datetime(df[col])
                elif dtype_str.startswith('timedelta'):
                    df[col] = pd.to_timedelta(df[col])
                elif dtype_str != 'object':  # Avoid converting strings unnecessarily
                    df[col] = df[col].astype(dtype_str)
            except (ValueError, TypeError) as e:
                logger.warning(f"Could not restore dtype {dtype_str} for column {col}: {e}")
        
        return df
    
    @staticmethod
    def decode_series(data: Dict[str, Any]) -> pd.Series:
        """Decode dictionary back to Series."""
        series = pd.Series(
            data=data['data'],
            index=data['index'],
            name=data['name']
        )
        
        # Restore original data type
        try:
            dtype_str = data['dtype']
            if dtype_str.startswith('datetime'):
                series = pd.to_datetime(series)
            elif dtype_str.startswith('timedelta'):
                series = pd.to_timedelta(series)
            elif dtype_str != 'object':
                series = series.astype(dtype_str)
        except (ValueError, TypeError) as e:
            logger.warning(f"Could not restore dtype {data['dtype']} for series: {e}")
        
        return series
    
    @classmethod
    def object_hook(cls, obj: Dict[str, Any]) -> Any:
        """JSON object hook for automatic DataFrame/Series reconstruction."""
        if isinstance(obj, dict) and '__type__' in obj:
            if obj['__type__'] == 'DataFrame':
                return cls.decode_dataframe(obj)
            elif obj['__type__'] == 'Series':
                return cls.decode_series(obj)
        return obj


class SecureDataFrameSerializer:
    """Secure DataFrame serializer using JSON + gzip compression."""
    
    def __init__(self, compression_level: int = 6):
        """
        Initialize serializer with compression level.
        
        Args:
            compression_level: gzip compression level (1-9, higher = better compression)
        """
        self.compression_level = compression_level
        self.encoder = DataFrameJSONEncoder()
        self.decoder = DataFrameJSONDecoder()
    
    def serialize_dataframe(self, df: pd.DataFrame) -> bytes:
        """
        Serialize DataFrame to compressed JSON bytes.
        
        Args:
            df: DataFrame to serialize
            
        Returns:
            bytes: Compressed JSON representation
        """
        try:
            # Convert DataFrame to JSON string
            json_str = json.dumps(df, cls=DataFrameJSONEncoder, separators=(',', ':'))
            
            # Compress with gzip
            compressed_data = gzip.compress(
                json_str.encode('utf-8'), 
                compresslevel=self.compression_level
            )
            
            logger.debug(f"DataFrame serialized: {len(json_str)} chars -> {len(compressed_data)} bytes")
            return compressed_data
            
        except Exception as e:
            logger.error(f"DataFrame serialization failed: {e}")
            raise
    
    def deserialize_dataframe(self, data: bytes) -> pd.DataFrame:
        """
        Deserialize compressed JSON bytes back to DataFrame.
        
        Args:
            data: Compressed JSON bytes
            
        Returns:
            pd.DataFrame: Reconstructed DataFrame
        """
        try:
            # Decompress gzip data
            json_str = gzip.decompress(data).decode('utf-8')
            
            # Parse JSON with custom decoder
            df = json.loads(json_str, object_hook=self.decoder.object_hook)
            
            if not isinstance(df, pd.DataFrame):
                raise ValueError("Deserialized object is not a DataFrame")
            
            logger.debug(f"DataFrame deserialized: {len(data)} bytes -> {df.shape}")
            return df
            
        except Exception as e:
            logger.error(f"DataFrame deserialization failed: {e}")
            raise
    
    def serialize_metadata(self, metadata: Dict[str, Any]) -> bytes:
        """
        Serialize metadata dictionary to compressed JSON bytes.
        
        Args:
            metadata: Metadata dictionary
            
        Returns:
            bytes: Compressed JSON representation
        """
        try:
            json_str = json.dumps(metadata, cls=DataFrameJSONEncoder, separators=(',', ':'))
            return gzip.compress(json_str.encode('utf-8'), compresslevel=self.compression_level)
        except Exception as e:
            logger.error(f"Metadata serialization failed: {e}")
            raise
    
    def deserialize_metadata(self, data: bytes) -> Dict[str, Any]:
        """
        Deserialize compressed JSON bytes back to metadata dictionary.
        
        Args:
            data: Compressed JSON bytes
            
        Returns:
            Dict[str, Any]: Reconstructed metadata
        """
        try:
            json_str = gzip.decompress(data).decode('utf-8')
            return json.loads(json_str, object_hook=self.decoder.object_hook)
        except Exception as e:
            logger.error(f"Metadata deserialization failed: {e}")
            raise
    
    def estimate_compression_ratio(self, df: pd.DataFrame) -> float:
        """
        Estimate compression ratio for a DataFrame.
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            float: Compression ratio (compressed_size / original_size)
        """
        try:
            json_str = json.dumps(df, cls=DataFrameJSONEncoder, separators=(',', ':'))
            original_size = len(json_str.encode('utf-8'))
            compressed_size = len(gzip.compress(json_str.encode('utf-8'), compresslevel=self.compression_level))
            
            ratio = compressed_size / original_size if original_size > 0 else 1.0
            logger.debug(f"Compression ratio: {ratio:.3f} ({original_size} -> {compressed_size} bytes)")
            return ratio
            
        except Exception as e:
            logger.error(f"Compression ratio estimation failed: {e}")
            return 1.0


# Global serializer instance
_serializer = SecureDataFrameSerializer()


def serialize_dataframe(df: pd.DataFrame) -> bytes:
    """Serialize DataFrame using the global serializer instance."""
    return _serializer.serialize_dataframe(df)


def deserialize_dataframe(data: bytes) -> pd.DataFrame:
    """Deserialize DataFrame using the global serializer instance."""
    return _serializer.deserialize_dataframe(data)


def serialize_metadata(metadata: Dict[str, Any]) -> bytes:
    """Serialize metadata using the global serializer instance."""
    return _serializer.serialize_metadata(metadata)


def deserialize_metadata(data: bytes) -> Dict[str, Any]:
    """Deserialize metadata using the global serializer instance."""
    return _serializer.deserialize_metadata(data)