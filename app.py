from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime
import logging
from typing import Dict, Tuple
import cv2
import numpy as np

from image_preprocessing import ImagePreprocessor, PDFProcessor
from ocr_engine import OCREngine, AdvancedOCRConfig
from table_extraction import TableDetector, BankStatementParser, StructuredExtractor
from error_handler import (
    ErrorHandler, RetryPolicy, LoggingHandler, 
    OCRException, ImageProcessingError, OCRExtractionError
)

# Initialize Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'jpg', 'jpeg', 'png', 'tiff', 'bmp'}

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def process_image_with_retry(image_path: str, attempt: int = 0) -> Tuple[Dict, int]:
    """Process image with retry logic."""
    try:
        if attempt >= RetryPolicy.MAX_RETRIES:
            return ErrorHandler.handle_timeout_error(), 408
        
        # Preprocess image
        logger.info(f"Preprocessing image (attempt {attempt + 1})")
        processed_image = ImagePreprocessor.preprocess_for_ocr(image_path)
        
        # Initialize OCR engine
        ocr_engine = OCREngine()
        
        # Perform hybrid OCR
        logger.info("Performing hybrid OCR")
        ocr_results = ocr_engine.hybrid_ocr(processed_image)
        
        # Use best result (PaddleOCR is best for tables)
        ocr_text = ocr_results.get('paddleocr', ocr_results.get('easyocr', ocr_results.get('tesseract', '')))
        
        if not ocr_text.strip():
            logger.warning("OCR extraction returned empty text")
            return ErrorHandler.handle_ocr_error(Exception("No text extracted"), "hybrid"), 400
        
        # Extract transactions
        logger.info("Extracting transactions from OCR text")
        transactions = BankStatementParser.extract_transactions(ocr_text)
        
        # Validate transactions
        validated_transactions = BankStatementParser.validate_transactions(transactions)
        
        if not validated_transactions:
            logger.warning("No valid transactions extracted")
            return {
                'success': False,
                'message': 'No valid transactions found in the statement.',
                'ocr_text': ocr_text
            }, 200
        
        # Extract structured data
        structured_data = StructuredExtractor.extract_all_data(ocr_text, validated_transactions)
        
        # Log results
        LoggingHandler.log_extraction_results(
            image_path, 
            len(validated_transactions),
            100.0
        )
        
        return ErrorHandler.create_success_response({
            'transactions': validated_transactions,
            'account_info': structured_data['account_info'],
            'transaction_count': len(validated_transactions),
            'ocr_engines_used': list(ocr_results.keys())
        }, 'Extraction successful'), 200
    
    except (ImageProcessingError, OCRExtractionError) as e:
        logger.error(f"Extraction error: {str(e)}")
        if RetryPolicy.should_retry(type(e).__name__) and attempt < RetryPolicy.MAX_RETRIES - 1:
            logger.info(f"Retrying operation (attempt {attempt + 2})")
            return process_image_with_retry(image_path, attempt + 1)
        return ErrorHandler.handle_ocr_error(e), 400
    
    except MemoryError:
        return ErrorHandler.handle_memory_error(), 507
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return ErrorHandler.handle_preprocessing_error(e), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    }), 200


@app.route('/extract', methods=['POST'])
def extract_from_image():
    """Extract data from uploaded image or PDF."""
    try:
        LoggingHandler.log_operation_start('extraction', request.remote_addr)
        
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify(ErrorHandler.handle_file_not_found('No file provided')), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify(ErrorHandler.handle_file_not_found('No file selected')), 400
        
        if not allowed_file(file.filename):
            return jsonify(ErrorHandler.handle_unsupported_format(
                file.filename.rsplit('.', 1)[1]
            )), 415
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        logger.info(f"File uploaded: {filename}")
        
        # Process based on file type
        file_ext = filename.rsplit('.', 1)[1].lower()
        
        if file_ext == 'pdf':
            # Handle PDF
            logger.info("Processing PDF file")
            try:
                pdf_images = PDFProcessor.extract_images_from_pdf(filepath)
                all_transactions = []
                
                for page_num, pdf_image in enumerate(pdf_images):
                    logger.info(f"Processing PDF page {page_num + 1}")
                    
                    # Save page image temporarily
                    page_image_path = os.path.join(
                        app.config['UPLOAD_FOLDER'],
                        f"{filename}_page_{page_num}.png"
                    )
                    cv2.imwrite(page_image_path, pdf_image)
                    
                    result, status = process_image_with_retry(page_image_path)
                    
                    if result.get('success') and result.get('data', {}).get('transactions'):
                        all_transactions.extend(result['data']['transactions'])
                    
                    # Clean up page image
                    os.remove(page_image_path)
                
                if not all_transactions:
                    return jsonify({
                        'success': False,
                        'message': 'No transactions extracted from PDF'
                    }), 400
                
                response = ErrorHandler.create_success_response({
                    'transactions': all_transactions,
                    'total_transactions': len(all_transactions),
                    'pages_processed': len(pdf_images)
                }, 'PDF extraction successful')
                
                return jsonify(response), 200
            
            except Exception as e:
                logger.error(f"PDF processing error: {str(e)}")
                return jsonify(ErrorHandler.handle_table_extraction_error(e)), 400
        
        else:
            # Handle image
            result, status = process_image_with_retry(filepath)
            
        # Clean up uploaded file
        os.remove(filepath)
        
        return jsonify(result), status
    
    except Exception as e:
        logger.error(f"Endpoint error: {str(e)}")
        return jsonify(ErrorHandler.handle_preprocessing_error(e)), 500


@app.route('/extract/advanced', methods=['POST'])
def extract_advanced():
    """Advanced extraction with preprocessing options."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        options = request.get_json() or {}
        
        if not allowed_file(file.filename):
            return jsonify(ErrorHandler.handle_unsupported_format(
                file.filename.rsplit('.', 1)[1]
            )), 415
        
        # Save file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Load image
        image = ImagePreprocessor.load_image(filepath)
        
        # Apply custom preprocessing
        if options.get('deskew', True):
            image = ImagePreprocessor.correct_skew(image)
        
        if options.get('denoise', True):
            image = ImagePreprocessor.denoise_image(image)
        
        if options.get('sharpen', True):
            image = ImagePreprocessor.sharpen_image(image)
        
        if options.get('scale', True):
            image = ImagePreprocessor.scale_image(image, scale_factor=2.0)
        
        threshold_method = options.get('threshold_method', 'adaptive')
        image = ImagePreprocessor.apply_thresholding(image, method=threshold_method)
        
        # Perform OCR
        ocr_engine = OCREngine()
        config_mode = options.get('ocr_mode', 'high_accuracy')
        config = AdvancedOCRConfig.get_config(config_mode)
        
        ocr_text = OCREngine.pytesseract_ocr(image, config)
        
        if not ocr_text.strip():
            return jsonify({'error': 'No text extracted'}), 400
        
        # Extract transactions
        transactions = BankStatementParser.extract_transactions(ocr_text)
        validated = BankStatementParser.validate_transactions(transactions)
        
        # Clean up
        os.remove(filepath)
        
        return jsonify(ErrorHandler.create_success_response({
            'transactions': validated,
            'transaction_count': len(validated),
            'preprocessing_options': options
        })), 200
    
    except Exception as e:
        logger.error(f"Advanced extraction error: {str(e)}")
        return jsonify(ErrorHandler.handle_preprocessing_error(e)), 500


@app.route('/config', methods=['GET'])
def get_config():
    """Get OCR configuration options."""
    return jsonify({
        'ocr_modes': ['high_accuracy', 'fast', 'table', 'document'],
        'threshold_methods': ['adaptive', 'otsu', 'simple'],
        'preprocessing_options': {
            'deskew': True,
            'denoise': True,
            'sharpen': True,
            'scale': True
        },
        'supported_formats': list(app.config['ALLOWED_EXTENSIONS']),
        'max_file_size_mb': 50
    }), 200


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error."""
    return jsonify({
        'error': 'File too large',
        'message': 'Maximum file size is 50MB'
    }), 413


@app.errorhandler(404)
def not_found(error):
    """Handle 404 error."""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_server_error(error):
    """Handle 500 error."""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
