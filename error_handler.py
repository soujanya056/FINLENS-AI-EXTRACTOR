import json
import logging
from typing import Dict, Optional, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OCRException(Exception):
    """Base exception for OCR operations."""
    pass


class ImageProcessingError(OCRException):
    """Raised when image preprocessing fails."""
    pass


class OCRExtractionError(OCRException):
    """Raised when OCR extraction fails."""
    pass


class TableExtractionError(OCRException):
    """Raised when table extraction fails."""
    pass


class ValidationError(OCRException):
    """Raised when data validation fails."""
    pass


class ErrorHandler:
    """Centralized error handling for OCR pipeline."""
    
    @staticmethod
    def handle_image_load_error(error: Exception) -> Dict:
        """Handle image loading errors."""
        logger.error(f"Image loading error: {str(error)}")
        return {
            'success': False,
            'error_type': 'IMAGE_LOAD_ERROR',
            'message': 'Failed to load image. Ensure file is a valid image or PDF.',
            'details': str(error)
        }
    
    @staticmethod
    def handle_preprocessing_error(error: Exception) -> Dict:
        """Handle preprocessing errors."""
        logger.error(f"Preprocessing error: {str(error)}")
        return {
            'success': False,
            'error_type': 'PREPROCESSING_ERROR',
            'message': 'Image preprocessing failed. Try with a clearer image.',
            'details': str(error)
        }
    
    @staticmethod
    def handle_ocr_error(error: Exception, engine: str = 'unknown') -> Dict:
        """Handle OCR extraction errors."""
        logger.error(f"OCR error ({engine}): {str(error)}")
        return {
            'success': False,
            'error_type': 'OCR_ERROR',
            'message': f'OCR extraction failed using {engine} engine.',
            'details': str(error),
            'engine': engine
        }
    
    @staticmethod
    def handle_table_extraction_error(error: Exception) -> Dict:
        """Handle table extraction errors."""
        logger.error(f"Table extraction error: {str(error)}")
        return {
            'success': False,
            'error_type': 'TABLE_EXTRACTION_ERROR',
            'message': 'Failed to extract table structure. Image may not contain a valid table.',
            'details': str(error)
        }
    
    @staticmethod
    def handle_validation_error(error: Exception) -> Dict:
        """Handle validation errors."""
        logger.error(f"Validation error: {str(error)}")
        return {
            'success': False,
            'error_type': 'VALIDATION_ERROR',
            'message': 'Extracted data failed validation. Please review the source image.',
            'details': str(error)
        }
    
    @staticmethod
    def handle_file_not_found(file_path: str) -> Dict:
        """Handle file not found errors."""
        logger.error(f"File not found: {file_path}")
        return {
            'success': False,
            'error_type': 'FILE_NOT_FOUND',
            'message': f'File not found: {file_path}',
            'details': 'Please ensure the file path is correct.'
        }
    
    @staticmethod
    def handle_unsupported_format(file_extension: str) -> Dict:
        """Handle unsupported file format errors."""
        logger.error(f"Unsupported file format: {file_extension}")
        return {
            'success': False,
            'error_type': 'UNSUPPORTED_FORMAT',
            'message': f'Unsupported file format: {file_extension}',
            'details': 'Supported formats: jpg, png, pdf'
        }
    
    @staticmethod
    def handle_timeout_error() -> Dict:
        """Handle timeout errors."""
        logger.error("OCR operation timed out")
        return {
            'success': False,
            'error_type': 'TIMEOUT_ERROR',
            'message': 'OCR operation timed out. Try with a smaller or clearer image.',
            'details': 'Operation exceeded maximum execution time.'
        }
    
    @staticmethod
    def handle_memory_error() -> Dict:
        """Handle memory errors."""
        logger.error("Memory error during OCR")
        return {
            'success': False,
            'error_type': 'MEMORY_ERROR',
            'message': 'Insufficient memory for OCR operation.',
            'details': 'Try with a smaller image or reduce preprocessing intensity.'
        }
    
    @staticmethod
    def create_error_response(status_code: int, error_type: str, 
                            message: str, details: Optional[str] = None) -> Tuple[Dict, int]:
        """Create standardized error response."""
        response = {
            'success': False,
            'error_type': error_type,
            'message': message
        }
        if details:
            response['details'] = details
        
        return response, status_code
    
    @staticmethod
    def create_success_response(data: Dict, message: str = 'Operation successful') -> Dict:
        """Create standardized success response."""
        return {
            'success': True,
            'message': message,
            'data': data
        }


class RetryPolicy:
    """Retry policy for failed OCR operations."""
    
    MAX_RETRIES = 3
    RETRY_DELAY = 2  # seconds
    
    @staticmethod
    def should_retry(error_type: str) -> bool:
        """Determine if operation should be retried."""
        retryable_errors = [
            'OCR_ERROR',
            'TIMEOUT_ERROR',
            'TEMPORARY_ERROR'
        ]
        return error_type in retryable_errors
    
    @staticmethod
    def get_retry_count(attempt: int) -> int:
        """Get number of retries remaining."""
        return max(0, RetryPolicy.MAX_RETRIES - attempt)
    
    @staticmethod
    def is_max_retries_exceeded(attempt: int) -> bool:
        """Check if max retries exceeded."""
        return attempt >= RetryPolicy.MAX_RETRIES


class LoggingHandler:
    """Centralized logging for OCR operations."""
    
    @staticmethod
    def log_operation_start(operation: str, file_name: str):
        """Log operation start."""
        logger.info(f"Starting {operation}: {file_name}")
    
    @staticmethod
    def log_operation_complete(operation: str, file_name: str, duration: float):
        """Log operation completion."""
        logger.info(f"Completed {operation}: {file_name} (Duration: {duration:.2f}s)")
    
    @staticmethod
    def log_extraction_results(file_name: str, transactions_count: int, confidence: float):
        """Log extraction results."""
        logger.info(f"Extraction results for {file_name}: "
                   f"{transactions_count} transactions, "
                   f"Confidence: {confidence:.2f}%")
    
    @staticmethod
    def log_warning(message: str, context: Dict = None):
        """Log warning with context."""
        if context:
            logger.warning(f"{message} | Context: {json.dumps(context)}")
        else:
            logger.warning(message)
