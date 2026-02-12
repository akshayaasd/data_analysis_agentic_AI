"""
Data management tools for loading and processing datasets.
"""
import pandas as pd
import os
from typing import Dict, Any, Optional, List
from pathlib import Path
import hashlib
from datetime import datetime


class DataTools:
    """Tools for data loading and management."""
    
    @staticmethod
    def load_file(file_path: str) -> pd.DataFrame:
        """
        Load a CSV or Excel file into a DataFrame.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Pandas DataFrame
        """
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == '.csv':
            return pd.read_csv(file_path)
        elif file_ext in ['.xlsx', '.xls']:
            return pd.read_excel(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")
    
    @staticmethod
    def get_dataset_info(df: pd.DataFrame, filename: str = "dataset") -> Dict[str, Any]:
        """
        Extract metadata from a DataFrame.
        
        Args:
            df: Pandas DataFrame
            filename: Original filename
            
        Returns:
            Dictionary with dataset information
        """
        return {
            'filename': filename,
            'rows': len(df),
            'columns': len(df.columns),
            'column_names': df.columns.tolist(),
            'column_types': {col: str(dtype) for col, dtype in df.dtypes.items()},
            'memory_usage': df.memory_usage(deep=True).sum(),
            'has_missing': df.isnull().any().any(),
            'missing_counts': df.isnull().sum().to_dict()
        }
    
    @staticmethod
    def get_preview(df: pd.DataFrame, n_rows: int = 10) -> List[Dict[str, Any]]:
        """
        Get a preview of the dataset.
        
        Args:
            df: Pandas DataFrame
            n_rows: Number of rows to preview
            
        Returns:
            List of row dictionaries
        """
        return df.head(n_rows).to_dict('records')
    
    @staticmethod
    def get_summary_statistics(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get summary statistics for the dataset.
        
        Args:
            df: Pandas DataFrame
            
        Returns:
            Dictionary with summary statistics
        """
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        summary = {
            'numeric_summary': {},
            'categorical_summary': {}
        }
        
        # Numeric columns
        if numeric_cols:
            desc = df[numeric_cols].describe()
            summary['numeric_summary'] = desc.to_dict()
        
        # Categorical columns
        for col in categorical_cols:
            summary['categorical_summary'][col] = {
                'unique_values': int(df[col].nunique()),
                'top_values': df[col].value_counts().head(5).to_dict(),
                'missing': int(df[col].isnull().sum())
            }
        
        return summary
    
    @staticmethod
    def generate_dataset_id(file_path: str) -> str:
        """
        Generate a unique ID for a dataset.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Unique dataset ID
        """
        # Use file path and timestamp to generate ID
        timestamp = datetime.now().isoformat()
        hash_input = f"{file_path}_{timestamp}".encode()
        return hashlib.md5(hash_input).hexdigest()[:16]
    
    @staticmethod
    def validate_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate a DataFrame and return any issues.
        
        Args:
            df: Pandas DataFrame
            
        Returns:
            Dictionary with validation results
        """
        issues = []
        
        if df.empty:
            issues.append("DataFrame is empty")
        
        if len(df.columns) == 0:
            issues.append("DataFrame has no columns")
        
        # Check for duplicate column names
        if len(df.columns) != len(set(df.columns)):
            issues.append("DataFrame has duplicate column names")
        
        # Check for all-null columns
        all_null_cols = df.columns[df.isnull().all()].tolist()
        if all_null_cols:
            issues.append(f"Columns with all null values: {all_null_cols}")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues
        }


class DatasetManager:
    """Manages loaded datasets in memory."""
    
    def __init__(self):
        self.datasets: Dict[str, pd.DataFrame] = {}
        self.metadata: Dict[str, Dict[str, Any]] = {}
    
    def add_dataset(
        self,
        dataset_id: str,
        df: pd.DataFrame,
        filename: str,
        file_path: str
    ):
        """
        Add a dataset to the manager.
        
        Args:
            dataset_id: Unique dataset ID
            df: Pandas DataFrame
            filename: Original filename
            file_path: Path to the file
        """
        self.datasets[dataset_id] = df
        self.metadata[dataset_id] = {
            'filename': filename,
            'file_path': file_path,
            'upload_time': datetime.now(),
            'info': DataTools.get_dataset_info(df, filename)
        }
    
    def get_dataset(self, dataset_id: str) -> Optional[pd.DataFrame]:
        """Get a dataset by ID."""
        return self.datasets.get(dataset_id)
    
    def get_metadata(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a dataset."""
        return self.metadata.get(dataset_id)
    
    def remove_dataset(self, dataset_id: str):
        """Remove a dataset from memory."""
        if dataset_id in self.datasets:
            del self.datasets[dataset_id]
        if dataset_id in self.metadata:
            del self.metadata[dataset_id]
    
    def list_datasets(self) -> List[str]:
        """List all dataset IDs."""
        return list(self.datasets.keys())


# Global dataset manager instance
dataset_manager = DatasetManager()