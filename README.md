# Bank Statement OCR Extractor 🏦

An AI-powered OCR system designed to extract transaction tables and structured data from scanned bank statements and low-quality PDFs.

## Features 🚀

- **Advanced Image Preprocessing**: Deskewing, denoising, sharpening, and thresholding
- **Multiple OCR Engines**: Tesseract, EasyOCR, and PaddleOCR with hybrid extraction
- **Table Detection**: Automatic detection of column and row boundaries
- **Bank Statement Parsing**: Extract transactions with validation
- **PDF Support**: Multi-page PDF processing
- **Error Handling**: Comprehensive error handling with retry logic
- **REST API**: Flask backend with multiple endpoints

## Preprocessing Techniques 🔧

### 1. **Skew Correction**
- Detects and corrects image rotation
- Uses Hough Line Transform for angle detection
- Handles 0-45 degree tilts

### 2. **Denoising**
```python
# Bilateral filter (preserves edges)
# Morphological operations (OPEN/CLOSE)
```

### 3. **Sharpening**
- Unsharp masking with custom kernel
- Enhances text clarity for OCR

### 4. **Scaling**
- Upscales images 2x for better OCR accuracy
- Uses cubic interpolation

### 5. **Thresholding**
- **Adaptive**: Works best for varying lighting
- **Otsu**: Automatic threshold calculation
- **Simple**: Fixed threshold

## OCR Engines Comparison 📊

| Engine | Accuracy | Speed | Best For |
|--------|----------|-------|----------|
| Tesseract | 85% | Fast | English text, documents |
| EasyOCR | 92% | Medium | Handwriting, rotated text |
| PaddleOCR | 95% | Medium | Tables, multi-column text |

## Installation 📦

```bash
# Clone repository
git clone https://github.com/soujanya056/FINLENS-AI-EXTRACTOR.git
cd FINLENS-AI-EXTRACTOR

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install system dependencies (Ubuntu/Debian)
sudo apt-get install tesseract-ocr
```

## Usage 🎯

### 1. **Basic Image Extraction**

```python
from image_preprocessing import ImagePreprocessor
from ocr_engine import OCREngine
from table_extraction import BankStatementParser

# Preprocess image
processed_image = ImagePreprocessor.preprocess_for_ocr('bank_statement.jpg')

# Extract text using multiple engines
ocr_engine = OCREngine()
results = ocr_engine.hybrid_ocr(processed_image)

# Parse transactions
transactions = BankStatementParser.extract_transactions(results['paddleocr'])
validated = BankStatementParser.validate_transactions(transactions)

print(f"Extracted {len(validated)} transactions")
```

### 2. **PDF Processing**

```python
from image_preprocessing import PDFProcessor

# Extract images from PDF
pdf_images = PDFProcessor.extract_images_from_pdf('bank_statement.pdf')

# Process each page
for page_num, image in enumerate(pdf_images):
    processed = PDFProcessor.preprocess_for_ocr_direct(image)
    # ... extract and parse transactions
```

### 3. **REST API**

```bash
# Start server
python app.py

# Extract from image
curl -X POST -F "file=@bank_statement.jpg" http://localhost:5000/extract

# Advanced extraction with options
curl -X POST \
  -F "file=@bank_statement.jpg" \
  -H "Content-Type: application/json" \
  http://localhost:5000/extract/advanced \
  -d '{"deskew": true, "denoise": true, "ocr_mode": "high_accuracy"}'

# Get configuration
curl http://localhost:5000/config

# Health check
curl http://localhost:5000/health
```

## API Endpoints 🔌

### `/extract` (POST)
**Extract data from uploaded image or PDF**

Request:
```bash
curl -X POST -F "file=@statement.jpg" http://localhost:5000/extract
```

Response:
```json
{
  "success": true,
  "message": "Extraction successful",
  "data": {
    "transactions": [
      {
        "Date": "2003-10-08",
        "Description": "Previous balance",
        "Withdrawals": "",
        "Deposits": "",
        "Balance": "0.55"
      }
    ],
    "transaction_count": 15,
    "account_info": {
      "Account_Number": "00005-123-456-7",
      "Statement_Period": "2003-10-09 to 2003-11-08"
    }
  }
}
```

### `/extract/advanced` (POST)
**Extract with custom preprocessing options**

Request:
```bash
curl -X POST \
  -F "file=@statement.jpg" \
  -H "Content-Type: application/json" \
  http://localhost:5000/extract/advanced \
  -d '{
    "deskew": true,
    "denoise": true,
    "sharpen": true,
    "scale": true,
    "threshold_method": "adaptive",
    "ocr_mode": "high_accuracy"
  }'
```

### `/config` (GET)
**Get OCR configuration options**

Response:
```json
{
  "ocr_modes": ["high_accuracy", "fast", "table", "document"],
  "threshold_methods": ["adaptive", "otsu", "simple"],
  "preprocessing_options": {
    "deskew": true,
    "denoise": true,
    "sharpen": true,
    "scale": true
  },
  "supported_formats": ["pdf", "jpg", "jpeg", "png", "tiff", "bmp"],
  "max_file_size_mb": 50
}
```

### `/health` (GET)
**Health check endpoint**

## Project Structure 📁

```
FINLENS-AI-EXTRACTOR/
├── app.py                    # Flask backend API
├── image_preprocessing.py    # Image preprocessing pipeline
├── ocr_engine.py            # OCR engines (Tesseract, EasyOCR, PaddleOCR)
├── table_extraction.py      # Table detection and parsing
├── error_handler.py         # Error handling and logging
├── requirements.txt         # Python dependencies
├── README.md               # This file
└── uploads/               # Uploaded files directory
```

## Error Handling ⚠️

The system includes comprehensive error handling:

- **IMAGE_LOAD_ERROR**: Failed to load image
- **PREPROCESSING_ERROR**: Image preprocessing failed
- **OCR_ERROR**: OCR extraction failed
- **TABLE_EXTRACTION_ERROR**: Table structure detection failed
- **VALIDATION_ERROR**: Data validation failed
- **TIMEOUT_ERROR**: Operation exceeded timeout
- **MEMORY_ERROR**: Insufficient memory

## Performance Tips ⚡

1. **For Blurry Images**: Use `denoise=True` and `sharpen=True`
2. **For Tilted Images**: Use `deskew=True`
3. **For Speed**: Use `ocr_mode="fast"`
4. **For Accuracy**: Use `ocr_mode="high_accuracy"` with `scale=True`
5. **For Large PDFs**: Process pages independently

## OCR Configuration Modes 🔧

### High Accuracy
```python
config = '--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789.,- '
```
Best for numerical data and currency amounts

### Table Mode
```python
config = '--oem 3 --psm 11'
```
Best for structured table data

### Document Mode
```python
config = '--oem 3 --psm 3'
```
Best for general documents

## Troubleshooting 🆘

### "No text extracted"
- Try with a higher quality/clearer image
- Enable preprocessing: `deskew=True, denoise=True, sharpen=True`

### "Invalid balance in transaction"
- Image quality issue - try preprocessing
- Non-standard balance format - check original image

### "No valid transactions found"
- Bank statement format may not be standard
- Try manual inspection of OCR output

### Memory Error
- Reduce image size before upload
- Process PDF pages one at a time

## Libraries & Technologies 📚

- **OpenCV**: Image processing and preprocessing
- **Tesseract OCR**: Traditional OCR engine
- **EasyOCR**: Deep learning OCR
- **PaddleOCR**: Table-optimized OCR
- **PDF2Image**: PDF to image conversion
- **Flask**: REST API backend
- **Pandas**: Data structuring
- **NumPy**: Numerical operations

## Future Improvements 🚀

- [ ] Support for multiple currencies and languages
- [ ] Machine learning-based anomaly detection
- [ ] Real-time OCR streaming
- [ ] Database integration for transaction storage
- [ ] Web UI for interactive processing
- [ ] Mobile app support
- [ ] Batch processing pipeline

## License 📄

MIT License

## Contributing 🤝

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Support 💬

For issues and questions:
- GitHub Issues: https://github.com/soujanya056/FINLENS-AI-EXTRACTOR/issues
- Email: soujanya056@email.com

---

**Version**: 1.0.0  
**Last Updated**: 2026-05-26
