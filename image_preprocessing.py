import cv2
import numpy as np
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
from skimage import filters, restoration
from scipy import ndimage
import io
from typing import Tuple, List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImagePreprocessor:
    """Advanced image preprocessing for bank statement OCR."""
    
    @staticmethod
    def load_image(image_path: str) -> np.ndarray:
        """Load image from file path."""
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Unable to load image: {image_path}")
        return img
    
    @staticmethod
    def convert_to_grayscale(image: np.ndarray) -> np.ndarray:
        """Convert image to grayscale."""
        if len(image.shape) == 3:
            return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return image
    
    @staticmethod
    def denoise_image(image: np.ndarray) -> np.ndarray:
        """Remove noise using multiple techniques."""
        # Apply bilateral filter (preserves edges)
        denoised = cv2.bilateralFilter(image, 9, 75, 75)
        
        # Apply morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        denoised = cv2.morphologyEx(denoised, cv2.MORPH_CLOSE, kernel)
        denoised = cv2.morphologyEx(denoised, cv2.MORPH_OPEN, kernel)
        
        return denoised
    
    @staticmethod
    def correct_skew(image: np.ndarray) -> np.ndarray:
        """Detect and correct image skew/rotation."""
        gray = ImagePreprocessor.convert_to_grayscale(image)
        
        # Detect edges
        edges = cv2.Canny(gray, 50, 150)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=100, maxLineGap=10)
        
        if lines is not None and len(lines) > 0:
            angles = []
            for line in lines:
                x1, y1, x2, y2 = line[0]
                if x2 - x1 != 0:
                    angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
                    if abs(angle) < 45:  # Filter valid angles
                        angles.append(angle)
            
            if angles:
                angle = np.median(angles)
                h, w = image.shape[:2]
                center = (w // 2, h // 2)
                rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
                image = cv2.warpAffine(image, rotation_matrix, (w, h), 
                                      borderMode=cv2.BORDER_REPLICATE)
        
        return image
    
    @staticmethod
    def apply_thresholding(image: np.ndarray, method: str = 'adaptive') -> np.ndarray:
        """Apply thresholding to binarize image."""
        gray = ImagePreprocessor.convert_to_grayscale(image)
        
        if method == 'adaptive':
            # Adaptive thresholding works better for varying lighting
            binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                          cv2.THRESH_BINARY, 11, 2)
        elif method == 'otsu':
            # Otsu's thresholding
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        else:
            # Simple thresholding
            _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
        
        return binary
    
    @staticmethod
    def sharpen_image(image: np.ndarray) -> np.ndarray:
        """Sharpen image to enhance text clarity."""
        kernel = np.array([[-1, -1, -1],
                          [-1,  9, -1],
                          [-1, -1, -1]]) / 9
        sharpened = cv2.filter2D(image, -1, kernel)
        return cv2.addWeighted(image, 1.5, sharpened, -0.5, 0)
    
    @staticmethod
    def scale_image(image: np.ndarray, scale_factor: float = 2.0) -> np.ndarray:
        """Upscale image for better OCR results."""
        h, w = image.shape[:2]
        new_w = int(w * scale_factor)
        new_h = int(h * scale_factor)
        return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
    
    @staticmethod
    def remove_background(image: np.ndarray) -> np.ndarray:
        """Remove background to isolate text."""
        gray = ImagePreprocessor.convert_to_grayscale(image)
        
        # Use morphological opening to remove small objects
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        opened = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel)
        
        # Subtract background
        background = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
        foreground = cv2.subtract(gray, background)
        
        return foreground
    
    @staticmethod
    def preprocess_for_ocr(image_path: str, enhance: bool = True) -> np.ndarray:
        """Complete preprocessing pipeline for OCR."""
        logger.info(f"Preprocessing image: {image_path}")
        
        # Load image
        image = ImagePreprocessor.load_image(image_path)
        
        # Correct skew
        image = ImagePreprocessor.correct_skew(image)
        logger.info("Skew corrected")
        
        # Convert to grayscale
        image = ImagePreprocessor.convert_to_grayscale(image)
        
        # Denoise
        image = ImagePreprocessor.denoise_image(image)
        logger.info("Denoising complete")
        
        # Sharpen
        image = ImagePreprocessor.sharpen_image(image)
        logger.info("Sharpening complete")
        
        # Scale up
        image = ImagePreprocessor.scale_image(image, scale_factor=2.0)
        logger.info("Image scaled")
        
        # Apply thresholding
        image = ImagePreprocessor.apply_thresholding(image, method='adaptive')
        logger.info("Thresholding applied")
        
        return image


class PDFProcessor:
    """Handle PDF document processing."""
    
    @staticmethod
    def extract_images_from_pdf(pdf_path: str, dpi: int = 300) -> List[np.ndarray]:
        """Extract images from PDF."""
        logger.info(f"Extracting images from PDF: {pdf_path}")
        try:
            images = convert_from_path(pdf_path, dpi=dpi)
            return [np.array(img) for img in images]
        except Exception as e:
            logger.error(f"Error extracting PDF: {e}")
            raise
    
    @staticmethod
    def process_pdf_for_ocr(pdf_path: str) -> List[np.ndarray]:
        """Process all pages from PDF for OCR."""
        images = PDFProcessor.extract_images_from_pdf(pdf_path)
        processed_images = []
        
        for idx, img in enumerate(images):
            # Convert PIL to OpenCV format
            cv_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            processed_img = ImagePreprocessor.preprocess_for_ocr_direct(cv_img)
            processed_images.append(processed_img)
            logger.info(f"Processed PDF page {idx + 1}")
        
        return processed_images
    
    @staticmethod
    def preprocess_for_ocr_direct(image: np.ndarray) -> np.ndarray:
        """Preprocess already loaded image array."""
        image = ImagePreprocessor.correct_skew(image)
        image = ImagePreprocessor.convert_to_grayscale(image)
        image = ImagePreprocessor.denoise_image(image)
        image = ImagePreprocessor.sharpen_image(image)
        image = ImagePreprocessor.scale_image(image, scale_factor=2.0)
        image = ImagePreprocessor.apply_thresholding(image, method='adaptive')
        return image


# Add method to ImagePreprocessor class
ImagePreprocessor.preprocess_for_ocr_direct = PDFProcessor.preprocess_for_ocr_direct
