"""
Utility functions for the PDF processing application.
"""

import os
import time
from typing import List, Optional
from datetime import datetime


def format_bytes(bytes_size: int) -> str:
    """Format bytes into human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"


def get_timestamp() -> str:
    """Get current timestamp in ISO format."""
    return datetime.now().isoformat()


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage."""
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename


def is_pdf_file(filename: str) -> bool:
    """Check if a file is a PDF based on its extension."""
    return filename.lower().endswith('.pdf')


def get_output_filename(input_filename: str, suffix: str = "_searchable") -> str:
    """Generate output filename with suffix."""
    name, ext = os.path.splitext(input_filename)
    return f"{name}{suffix}{ext}"


def print_progress(current: int, total: int, operation: str = "Processing") -> None:
    """Print progress information."""
    percentage = (current / total) * 100 if total > 0 else 0
    print(f"📊 {operation}: {current}/{total} ({percentage:.1f}%)")


def print_header(title: str) -> None:
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_section(title: str) -> None:
    """Print a formatted section header."""
    print(f"\n--- {title} ---")


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human readable format."""
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} minutes"
    else:
        hours = seconds / 3600
        return f"{hours:.1f} hours"


def create_directory_if_not_exists(directory_path: str) -> None:
    """Create directory if it doesn't exist."""
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"📁 Created directory: {directory_path}")


def validate_environment_variable(var_name: str, var_value: Optional[str]) -> str:
    """Validate that an environment variable is set and not empty."""
    if not var_value:
        raise ValueError(f"Environment variable '{var_name}' is not set or is empty")
    return var_value


def get_config_int(var_name: str, default_value: int) -> int:
    """Get integer configuration value from environment variable with default."""
    value = os.getenv(var_name)
    if value is None:
        return default_value
    try:
        return int(value)
    except ValueError:
        print(f"⚠️  Invalid value for {var_name}: '{value}'. Using default: {default_value}")
        return default_value


def safe_print(message: str) -> None:
    """Safely print message, handling encoding errors."""
    try:
        print(message)
    except UnicodeEncodeError:
        # Fallback to ASCII-safe printing
        print(message.encode('ascii', errors='replace').decode('ascii'))


class ProgressTracker:
    """Track and display progress for long-running operations."""
    
    def __init__(self, total_items: int, operation_name: str = "Processing"):
        self.total_items = total_items
        self.operation_name = operation_name
        self.completed_items = 0
        self.failed_items = 0
        self.start_time = time.time()
        
    def update(self, increment: int = 1, failed: bool = False) -> None:
        """Update progress counter."""
        if failed:
            self.failed_items += increment
        else:
            self.completed_items += increment
            
        self._print_progress()
    
    def _print_progress(self) -> None:
        """Print current progress."""
        total_processed = self.completed_items + self.failed_items
        percentage = (total_processed / self.total_items) * 100 if self.total_items > 0 else 0
        
        elapsed_time = time.time() - self.start_time
        
        status_parts = []
        if self.completed_items > 0:
            status_parts.append(f"✅ {self.completed_items} completed")
        if self.failed_items > 0:
            status_parts.append(f"❌ {self.failed_items} failed")
            
        status = " | ".join(status_parts) if status_parts else "Starting..."
        
        print(f"📊 {self.operation_name}: {total_processed}/{self.total_items} ({percentage:.1f}%) - {status} - {format_duration(elapsed_time)}")
    
    def finish(self) -> None:
        """Print final summary."""
        total_time = time.time() - self.start_time
        print(f"\n🏁 {self.operation_name} completed in {format_duration(total_time)}")
        print(f"   ✅ Successful: {self.completed_items}")
        print(f"   ❌ Failed: {self.failed_items}")
        print(f"   📊 Total: {self.total_items}")


def retry_with_backoff(func, max_retries: int = 3, base_delay: float = 1.0):
    """Retry a function with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            
            delay = base_delay * (2 ** attempt)
            print(f"⚠️  Attempt {attempt + 1} failed: {str(e)}. Retrying in {delay:.1f} seconds...")
            time.sleep(delay)
    
    return None
