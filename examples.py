"""
Example usage of the Bank Statement OCR Extractor

This script demonstrates how to use the OCR pipeline with various preprocessing options.
"""

import cv2
import json
from image_preprocessing import ImagePreprocessor, PDFProcessor
from ocr_engine import OCREngine, AdvancedOCRConfig
from table_extraction import TableDetector, BankStatementParser, StructuredExtractor
from error_handler import ErrorHandler, LoggingHandler
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_1_basic_image_extraction():
    """Example 1: Extract text from a scanned bank statement image."""
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic Image Extraction")
    print("="*60)
    
    try:
        # Load and preprocess image
        image_path = 'sample_bank_statement.jpg'
        processed_image = ImagePreprocessor.preprocess_for_ocr(image_path)
        
        # Extract text using Tesseract
        ocr_engine = OCREngine()
        ocr_text = ocr_engine.pytesseract_ocr(processed_image)
        
        print(f"\n✅ Extracted Text:\n{ocr_text[:200]}...")
        
        # Extract transactions
        transactions = BankStatementParser.extract_transactions(ocr_text)
        validated = BankStatementParser.validate_transactions(transactions)
        
        print(f"\n✅ Extracted {len(validated)} valid transactions")
        for i, trans in enumerate(validated[:3]):
            print(f"   Transaction {i+1}: {trans['Date']} | {trans['Description']} | {trans['Balance']}")
        
    except Exception as e:
        logger.error(f"Error in example 1: {e}")
        print(f"❌ Error: {str(e)}")


def example_2_hybrid_ocr():
    """Example 2: Use multiple OCR engines for better accuracy."""
    print("\n" + "="*60)
    print("EXAMPLE 2: Hybrid OCR (Multiple Engines)")
    print("="*60)
    
    try:
        # Load and preprocess image
        image_path = 'sample_bank_statement.jpg'
        processed_image = ImagePreprocessor.preprocess_for_ocr(image_path)
        
        # Use hybrid OCR
        ocr_engine = OCREngine()
        results = ocr_engine.hybrid_ocr(processed_image)
        
        print("\n✅ OCR Results from Multiple Engines:")
        for engine, text in results.items():
            if isinstance(text, str):
                print(f"\n   {engine.upper()}:")
                print(f"   Text length: {len(text)} characters")
                print(f"   Preview: {text[:100]}...")
        
        # Use best result (PaddleOCR)
        best_text = results.get('paddleocr', results.get('easyocr', ''))
        transactions = BankStatementParser.extract_transactions(best_text)
        
        print(f"\n✅ Extracted {len(transactions)} transactions using PaddleOCR")
        
    except Exception as e:
        logger.error(f"Error in example 2: {e}")
        print(f"❌ Error: {str(e)}")


def example_3_advanced_preprocessing():
    """Example 3: Advanced preprocessing with custom options."""
    print("\n" + "="*60)
    print("EXAMPLE 3: Advanced Preprocessing")
    print("="*60)
    
    try:
        # Load image
        image_path = 'sample_bank_statement.jpg'
        image = ImagePreprocessor.load_image(image_path)
        
        print("✅ Original Image Loaded")
        print(f"   Dimensions: {image.shape}")
        
        # Apply preprocessing steps
        print("\n📍 Applying preprocessing steps:")
        
        # Step 1: Deskew
        image = ImagePreprocessor.correct_skew(image)
        print("   ✓ Skew corrected")
        
        # Step 2: Denoise
        image = ImagePreprocessor.denoise_image(image)
        print("   ✓ Image denoised")
        
        # Step 3: Sharpen
        image = ImagePreprocessor.sharpen_image(image)
        print("   ✓ Image sharpened")
        
        # Step 4: Scale
        image = ImagePreprocessor.scale_image(image, scale_factor=2.0)
        print("   ✓ Image scaled (2x)")
        
        # Step 5: Threshold
        image = ImagePreprocessor.apply_thresholding(image, method='adaptive')
        print("   ✓ Adaptive thresholding applied")
        
        print(f"\n✅ Final Image Dimensions: {image.shape}")
        
        # Perform OCR on processed image
        ocr_engine = OCREngine()
        ocr_text = ocr_engine.pytesseract_ocr(image)
        
        transactions = BankStatementParser.extract_transactions(ocr_text)
        print(f"\n✅ Extracted {len(transactions)} transactions")
        
    except Exception as e:
        logger.error(f"Error in example 3: {e}")
        print(f"❌ Error: {str(e)}")


def example_4_pdf_processing():
    """Example 4: Process multi-page PDF."""
    print("\n" + "="*60)
    print("EXAMPLE 4: PDF Processing")
    print("="*60)
    
    try:
        pdf_path = 'sample_bank_statements.pdf'
        
        # Extract images from PDF
        print(f"📄 Extracting images from PDF: {pdf_path}")
        pdf_images = PDFProcessor.extract_images_from_pdf(pdf_path)
        
        print(f"✅ Extracted {len(pdf_images)} pages from PDF")
        
        all_transactions = []
        
        # Process each page
        for page_num, pdf_image in enumerate(pdf_images):
            print(f"\n📍 Processing page {page_num + 1}...")
            
            # Preprocess
            processed = PDFProcessor.preprocess_for_ocr_direct(pdf_image)
            
            # OCR
            ocr_engine = OCREngine()
            ocr_text = ocr_engine.pytesseract_ocr(processed)
            
            # Extract transactions
            transactions = BankStatementParser.extract_transactions(ocr_text)
            validated = BankStatementParser.validate_transactions(transactions)
            
            print(f"   ✓ Page {page_num + 1}: {len(validated)} transactions")
            all_transactions.extend(validated)
        
        print(f"\n✅ Total transactions extracted: {len(all_transactions)}")
        
    except Exception as e:
        logger.error(f"Error in example 4: {e}")
        print(f"❌ Error: {str(e)}")


def example_5_table_detection():
    """Example 5: Detect and extract table structure."""
    print("\n" + "="*60)
    print("EXAMPLE 5: Table Detection")
    print("="*60)
    
    try:
        # Load and preprocess image
        image_path = 'sample_bank_statement.jpg'
        image = ImagePreprocessor.load_image(image_path)
        processed_image = ImagePreprocessor.preprocess_for_ocr(image_path)
        
        # Detect table structure
        print("📍 Detecting table structure...")
        table_info = TableDetector.detect_table_structure(processed_image)
        print(f"✅ Detected {len(table_info['contours'])} contours")
        
        # Detect columns
        print("\n📍 Detecting columns...")
        columns = TableDetector.detect_columns(processed_image)
        print(f"✅ Detected {len(columns)} columns")
        for i, (start, end) in enumerate(columns):
            print(f"   Column {i+1}: x={start}-{end}")
        
        # Detect rows
        print("\n📍 Detecting rows...")
        rows = TableDetector.detect_rows(processed_image)
        print(f"✅ Detected {len(rows)} rows")
        for i, (start, end) in enumerate(rows[:5]):
            print(f"   Row {i+1}: y={start}-{end}")
        
        # Extract table cells
        if rows and columns:
            print("\n📍 Extracting table cells...")
            cells = TableDetector.extract_table_cells(processed_image, rows, columns)
            print(f"✅ Extracted {len(cells)} x {len(columns)} = {len(cells)*len(columns)} cells")
        
    except Exception as e:
        logger.error(f"Error in example 5: {e}")
        print(f"❌ Error: {str(e)}")


def example_6_ocr_configurations():
    """Example 6: Test different OCR configurations."""
    print("\n" + "="*60)
    print("EXAMPLE 6: OCR Configuration Modes")
    print("="*60)
    
    try:
        image_path = 'sample_bank_statement.jpg'
        image = ImagePreprocessor.load_image(image_path)
        
        modes = ['high_accuracy', 'fast', 'table', 'document']
        
        for mode in modes:
            print(f"\n📍 Testing {mode.upper()} mode...")
            config = AdvancedOCRConfig.get_config(mode)
            print(f"   Config: {config}")
            
            # Note: Actual OCR would require the image to be preprocessed
            # and proper installation of Tesseract
            print(f"   ✓ Configuration loaded")
        
        print("\n✅ All configurations tested")
        
    except Exception as e:
        logger.error(f"Error in example 6: {e}")
        print(f"❌ Error: {str(e)}")


def example_7_error_handling():
    """Example 7: Demonstrate error handling."""
    print("\n" + "="*60)
    print("EXAMPLE 7: Error Handling")
    print("="*60)
    
    # Simulate various error scenarios
    errors = [
        ('IMAGE_LOAD_ERROR', ErrorHandler.handle_image_load_error(Exception("File not found"))),
        ('PREPROCESSING_ERROR', ErrorHandler.handle_preprocessing_error(Exception("Invalid image format"))),
        ('OCR_ERROR', ErrorHandler.handle_ocr_error(Exception("OCR timeout"), "tesseract")),
        ('TABLE_EXTRACTION_ERROR', ErrorHandler.handle_table_extraction_error(Exception("No table found"))),
        ('VALIDATION_ERROR', ErrorHandler.handle_validation_error(Exception("Invalid data format"))),
    ]
    
    for error_type, error_response in errors:
        print(f"\n{error_type}:")
        print(f"  ✗ {error_response['message']}")
        print(f"  Type: {error_response['error_type']}")


def example_8_structured_extraction():
    """Example 8: Extract complete structured data."""
    print("\n" + "="*60)
    print("EXAMPLE 8: Structured Data Extraction")
    print("="*60)
    
    try:
        # Sample OCR text
        ocr_text = """
        FIRST BANK OF WIKI
        1425 JAMES ST, PO BOX 4000
        VICTORIA BC V8X 3X4
        
        STATEMENT PERIOD
        2003-10-09 to 2003-11-08
        ACCOUNT NO. 00005-123-456-7
        
        2003-10-08    Previous balance                                           0.55
        2003-10-14    Payroll Deposit - HOTEL                      694.81        694.81
        2003-10-14    Web Bill Payment - MASTERCARD      9685      200.00        495.36
        2003-10-16    ATM Withdrawal - INTERAC           3990       21.25        474.11
        """
        
        # Extract account info
        print("📍 Extracting account information...")
        account_info = StructuredExtractor.extract_account_info(ocr_text)
        print(f"✅ Account Info:")
        print(f"   Account Number: {account_info['Account_Number']}")
        print(f"   Period: {account_info['Statement_Period']}")
        
        # Extract transactions
        print("\n📍 Extracting transactions...")
        transactions = BankStatementParser.extract_transactions(ocr_text)
        validated = BankStatementParser.validate_transactions(transactions)
        print(f"✅ Extracted {len(validated)} transactions")
        
        # Create structured output
        structured_data = StructuredExtractor.extract_all_data(ocr_text, validated)
        
        # Convert to DataFrame
        df = BankStatementParser.transactions_to_dataframe(validated)
        
        print(f"\n✅ Structured Data:")
        print(f"   Total Transactions: {len(df)}")
        print(f"\n📊 DataFrame Preview:")
        print(df.head())
        
    except Exception as e:
        logger.error(f"Error in example 8: {e}")
        print(f"❌ Error: {str(e)}")


def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("BANK STATEMENT OCR EXTRACTOR - EXAMPLES")
    print("="*60)
    
    examples = [
        ("Basic Image Extraction", example_1_basic_image_extraction),
        ("Hybrid OCR", example_2_hybrid_ocr),
        ("Advanced Preprocessing", example_3_advanced_preprocessing),
        ("PDF Processing", example_4_pdf_processing),
        ("Table Detection", example_5_table_detection),
        ("OCR Configurations", example_6_ocr_configurations),
        ("Error Handling", example_7_error_handling),
        ("Structured Extraction", example_8_structured_extraction),
    ]
    
    print("\n📋 Available Examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"   {i}. {name}")
    
    print("\n💡 Uncomment examples you want to run in main():")
    
    # Uncomment examples to run:
    # example_1_basic_image_extraction()
    # example_2_hybrid_ocr()
    # example_3_advanced_preprocessing()
    # example_4_pdf_processing()
    # example_5_table_detection()
    # example_6_ocr_configurations()
    # example_7_error_handling()
    # example_8_structured_extraction()


if __name__ == '__main__':
    main()
