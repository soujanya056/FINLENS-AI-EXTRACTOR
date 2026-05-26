import cv2
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TableDetector:
    """Detect and extract tables from bank statements."""
    
    @staticmethod
    def detect_table_structure(image: np.ndarray) -> Dict:
        """Detect table structure using contour detection."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        
        # Detect horizontal and vertical lines
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 25))
        
        horizontal_lines = cv2.morphologyEx(gray, cv2.MORPH_OPEN, horizontal_kernel)
        vertical_lines = cv2.morphologyEx(gray, cv2.MORPH_OPEN, vertical_kernel)
        
        # Combine lines
        table_structure = cv2.add(horizontal_lines, vertical_lines)
        
        # Find contours
        contours, _ = cv2.findContours(table_structure, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        logger.info(f"Detected {len(contours)} contours")
        
        return {
            'structure': table_structure,
            'contours': contours,
            'horizontal_lines': horizontal_lines,
            'vertical_lines': vertical_lines
        }
    
    @staticmethod
    def detect_columns(image: np.ndarray) -> List[Tuple[int, int]]:
        """Detect column boundaries in table."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        
        # Detect vertical edges
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 20))
        vertical_lines = cv2.morphologyEx(gray, cv2.MORPH_OPEN, vertical_kernel)
        
        # Project columns
        col_sum = np.sum(vertical_lines, axis=0)
        
        # Find peaks (column boundaries)
        threshold = np.mean(col_sum) * 0.5
        col_peaks = []
        
        for i in range(1, len(col_sum) - 1):
            if col_sum[i] > threshold and col_sum[i] > col_sum[i-1] and col_sum[i] > col_sum[i+1]:
                col_peaks.append(i)
        
        # Group nearby peaks
        columns = []
        if col_peaks:
            current_group = [col_peaks[0]]
            for peak in col_peaks[1:]:
                if peak - current_group[-1] < 10:
                    current_group.append(peak)
                else:
                    columns.append((min(current_group), max(current_group)))
                    current_group = [peak]
            columns.append((min(current_group), max(current_group)))
        
        logger.info(f"Detected {len(columns)} columns")
        return columns
    
    @staticmethod
    def detect_rows(image: np.ndarray) -> List[Tuple[int, int]]:
        """Detect row boundaries in table."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        
        # Detect horizontal edges
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 1))
        horizontal_lines = cv2.morphologyEx(gray, cv2.MORPH_OPEN, horizontal_kernel)
        
        # Project rows
        row_sum = np.sum(horizontal_lines, axis=1)
        
        # Find peaks (row boundaries)
        threshold = np.mean(row_sum) * 0.5
        row_peaks = []
        
        for i in range(1, len(row_sum) - 1):
            if row_sum[i] > threshold and row_sum[i] > row_sum[i-1] and row_sum[i] > row_sum[i+1]:
                row_peaks.append(i)
        
        # Group nearby peaks
        rows = []
        if row_peaks:
            current_group = [row_peaks[0]]
            for peak in row_peaks[1:]:
                if peak - current_group[-1] < 10:
                    current_group.append(peak)
                else:
                    rows.append((min(current_group), max(current_group)))
                    current_group = [peak]
            rows.append((min(current_group), max(current_group)))
        
        logger.info(f"Detected {len(rows)} rows")
        return rows
    
    @staticmethod
    def extract_table_cells(image: np.ndarray, rows: List[Tuple[int, int]], 
                          columns: List[Tuple[int, int]]) -> List[List[np.ndarray]]:
        """Extract individual table cells."""
        cells = []
        for row_idx, (row_start, row_end) in enumerate(rows):
            row_cells = []
            for col_idx, (col_start, col_end) in enumerate(columns):
                cell = image[row_start:row_end, col_start:col_end]
                row_cells.append(cell)
            cells.append(row_cells)
        
        logger.info(f"Extracted {len(cells)}x{len(columns)} cells")
        return cells


class BankStatementParser:
    """Parse bank statement specific data structures."""
    
    # Define expected column headers for bank statements
    EXPECTED_COLUMNS = ['Date', 'Description', 'Ref', 'Withdrawals', 'Deposits', 'Balance']
    
    # Transaction patterns
    PATTERNS = {
        'date': r'\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}',
        'amount': r'\d+\.\d{2}',
        'negative_amount': r'-\d+\.\d{2}',
    }
    
    @staticmethod
    def extract_transactions(ocr_text: str) -> List[Dict]:
        """Extract transaction rows from OCR text."""
        lines = ocr_text.split('\n')
        transactions = []
        
        for line in lines:
            if not line.strip():
                continue
            
            # Check if line contains a date
            date_match = re.search(BankStatementParser.PATTERNS['date'], line)
            if date_match:
                transaction = BankStatementParser.parse_transaction_line(line)
                if transaction:
                    transactions.append(transaction)
        
        logger.info(f"Extracted {len(transactions)} transactions")
        return transactions
    
    @staticmethod
    def parse_transaction_line(line: str) -> Optional[Dict]:
        """Parse a single transaction line."""
        try:
            parts = re.split(r'\s{2,}', line.strip())
            
            if len(parts) < 3:
                return None
            
            transaction = {
                'Date': parts[0],
                'Description': parts[1] if len(parts) > 1 else '',
                'Ref': parts[2] if len(parts) > 2 else '',
                'Withdrawals': '',
                'Deposits': '',
                'Balance': ''
            }
            
            # Extract amounts
            amounts = re.findall(BankStatementParser.PATTERNS['amount'], line)
            if amounts:
                if len(amounts) >= 3:
                    transaction['Withdrawals'] = amounts[-3] if amounts[-3] else ''
                    transaction['Deposits'] = amounts[-2] if amounts[-2] else ''
                    transaction['Balance'] = amounts[-1]
                elif len(amounts) == 2:
                    transaction['Deposits'] = amounts[-2]
                    transaction['Balance'] = amounts[-1]
                elif len(amounts) == 1:
                    transaction['Balance'] = amounts[0]
            
            return transaction
        except Exception as e:
            logger.error(f"Error parsing line: {e}")
            return None
    
    @staticmethod
    def validate_transactions(transactions: List[Dict]) -> List[Dict]:
        """Validate extracted transactions."""
        validated = []
        
        for trans in transactions:
            # Check if date is valid
            if not trans.get('Date'):
                continue
            
            # Check if balance is numeric
            try:
                if trans.get('Balance'):
                    float(trans['Balance'])
                validated.append(trans)
            except ValueError:
                logger.warning(f"Invalid balance in transaction: {trans}")
                continue
        
        logger.info(f"Validated {len(validated)} transactions")
        return validated
    
    @staticmethod
    def transactions_to_dataframe(transactions: List[Dict]) -> pd.DataFrame:
        """Convert transactions to pandas DataFrame."""
        df = pd.DataFrame(transactions)
        
        # Convert numeric columns
        numeric_cols = ['Withdrawals', 'Deposits', 'Balance']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        logger.info(f"Created DataFrame with {len(df)} rows")
        return df


class StructuredExtractor:
    """Extract and structure all data from bank statement."""
    
    @staticmethod
    def extract_account_info(ocr_text: str) -> Dict:
        """Extract account information from OCR text."""
        info = {
            'Account_Holder': '',
            'Account_Number': '',
            'Statement_Period': '',
            'Bank_Name': ''
        }
        
        lines = ocr_text.split('\n')
        
        # Look for account number pattern
        for line in lines:
            account_match = re.search(r'Account[:\s]+(\d{6,})', line, re.IGNORECASE)
            if account_match:
                info['Account_Number'] = account_match.group(1)
            
            period_match = re.search(r'(\d{4}-\d{2}-\d{2})\s+to\s+(\d{4}-\d{2}-\d{2})', line)
            if period_match:
                info['Statement_Period'] = f"{period_match.group(1)} to {period_match.group(2)}"
        
        return info
    
    @staticmethod
    def extract_all_data(ocr_text: str, transactions: List[Dict]) -> Dict:
        """Extract complete structured data."""
        return {
            'account_info': StructuredExtractor.extract_account_info(ocr_text),
            'transactions': transactions,
            'raw_text': ocr_text,
            'transaction_count': len(transactions)
        }
