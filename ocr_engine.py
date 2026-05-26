import pytesseract
import easyocr
import paddleocr
import cv2
import numpy as np
from typing import Dict, List, Tuple, Union
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OCREngine:
    """Multiple OCR engines with fallback support."""
    
    def __init__(self):
        self.pytesseract_config = r'--oem 3 --psm 6'
        self.easyocr_reader = None
        self.paddleocr_reader = None
    
    @staticmethod
    def pytesseract_ocr(image: np.ndarray, config: str = r'--oem 3 --psm 6') -> str:
        """Extract text using Tesseract OCR."""
        try:
            text = pytesseract.image_to_string(image, config=config)
            logger.info("Tesseract OCR completed")
            return text
        except Exception as e:
            logger.error(f"Tesseract OCR error: {e}")
            return ""
    
    def easyocr_extract(self, image: np.ndarray, languages: List[str] = ['en']) -> Tuple[str, List]:
        """Extract text using EasyOCR with better accuracy."""
        try:
            if self.easyocr_reader is None:
                self.easyocr_reader = easyocr.Reader(languages)
            
            results = self.easyocr_reader.readtext(image)
            text = '\n'.join([text for (bbox, text, confidence) in results if confidence > 0.3])
            
            logger.info(f"EasyOCR completed with {len(results)} detections")
            return text, results
        except Exception as e:
            logger.error(f"EasyOCR error: {e}")
            return "", []
    
    def paddleocr_extract(self, image: np.ndarray) -> Tuple[str, List]:
        """Extract text using PaddleOCR (best for tables)."""
        try:
            if self.paddleocr_reader is None:
                self.paddleocr_reader = paddleocr.PaddleOCR(use_angle_cls=True, lang='en')
            
            results = self.paddleocr_reader.ocr(image, cls=True)
            text_lines = []
            
            for line in results:
                for word_info in line:
                    text = word_info[1][0]
                    confidence = word_info[1][1]
                    if confidence > 0.3:
                        text_lines.append(text)
            
            text = '\n'.join(text_lines)
            logger.info(f"PaddleOCR completed with {len(results)} lines")
            return text, results
        except Exception as e:
            logger.error(f"PaddleOCR error: {e}")
            return "", []
    
    def hybrid_ocr(self, image: np.ndarray, use_easyocr: bool = True, 
                   use_paddle: bool = True) -> Dict[str, Union[str, List]]:
        """Combine multiple OCR engines for better accuracy."""
        results = {}
        
        # Tesseract baseline
        results['tesseract'] = self.pytesseract_ocr(image)
        
        # EasyOCR for better accuracy
        if use_easyocr:
            text, detections = self.easyocr_extract(image)
            results['easyocr'] = text
            results['easyocr_detections'] = detections
        
        # PaddleOCR for table detection
        if use_paddle:
            text, detections = self.paddleocr_extract(image)
            results['paddleocr'] = text
            results['paddleocr_detections'] = detections
        
        return results
    
    @staticmethod
    def get_text_with_confidence(image: np.ndarray) -> Dict:
        """Extract text with confidence scores from Tesseract."""
        try:
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            
            result = {
                'text': [],
                'confidence': [],
                'bounding_boxes': []
            }
            
            for i in range(len(data['text'])):
                if int(data['conf'][i]) > 30:  # Confidence threshold
                    result['text'].append(data['text'][i])
                    result['confidence'].append(int(data['conf'][i]))
                    result['bounding_boxes'].append({
                        'x': data['left'][i],
                        'y': data['top'][i],
                        'w': data['width'][i],
                        'h': data['height'][i]
                    })
            
            logger.info(f"Extracted {len(result['text'])} text elements")
            return result
        except Exception as e:
            logger.error(f"Error extracting text with confidence: {e}")
            return {'text': [], 'confidence': [], 'bounding_boxes': []}


class AdvancedOCRConfig:
    """Optimized configurations for different scenarios."""
    
    # High accuracy mode
    HIGH_ACCURACY = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789.,- '
    
    # Fast mode
    FAST = r'--oem 1 --psm 6'
    
    # Table mode
    TABLE = r'--oem 3 --psm 11'
    
    # Document mode
    DOCUMENT = r'--oem 3 --psm 3'
    
    @staticmethod
    def get_config(mode: str = 'high_accuracy') -> str:
        """Get appropriate config based on mode."""
        configs = {
            'high_accuracy': AdvancedOCRConfig.HIGH_ACCURACY,
            'fast': AdvancedOCRConfig.FAST,
            'table': AdvancedOCRConfig.TABLE,
            'document': AdvancedOCRConfig.DOCUMENT
        }
        return configs.get(mode, AdvancedOCRConfig.HIGH_ACCURACY)
