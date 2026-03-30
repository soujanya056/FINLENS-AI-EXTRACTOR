import io
import pdfplumber
import json
import re
import requests
import base64
try:
    from PIL import Image, ImageFilter, ImageEnhance
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import pytesseract
    # Common Windows Tesseract path
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False


def extract_text_from_pdf(file_bytes):
    """
    Step 1: Raw PDF Text Extraction
    """
    print("📂 [1/2] Extracting raw text from PDF...")
    extracted_text = ""
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    extracted_text += text + "\n"
        
        if not extracted_text.strip():
            return None 
            
        print(f"✅ Extracted {len(extracted_text)} characters.")
        return extracted_text.strip()
    except Exception as e:
        print(f"❌ Extraction Error: {e}")
        return {"error": f"Failed to extract text from PDF: {str(e)}"}

def extract_transactions_regex(text):
    """
    ULTRA-FAST PARSER: Uses Regex to extract transactions in milliseconds.
    Upgraded for 3-column (Withdrawal, Deposit, Balance) support.
    """
    print("⚡ [2/3] Running Smart Regex Parser...")
    transactions = []
    
    # Improved pattern: Date | Narration | [ValueDate] | [Ref] | Num1 | Num2 | Num3
    # We look for lines starting with a date and ending with 1-3 numbers
    pattern = re.compile(
        r"(\d{1,4}[-/\.]\w{2,3}[-/\.]\d{2,4}|\d{1,2}[-/\.]\d{1,2}[-/\.]\d{2,4}|\d{1,2}\s+[a-zA-Z]{3,4}\s+\d{2,4}|\d{1,2}[-/\.]\d{1,2})\s+" # Date (Very forgiving)
        r"(.*?)\s+"                                    # Narration (Lazy match)
        r"([\d,]+\.\d{2})\s*"                          # Number 1
        r"([\d,]+\.\d{2})?\s*"                         # Optional Number 2
        r"([\d,]+\.\d{2})?\s*$"                        # Optional Number 3 (Balance)
    )

    lines = [line.strip() for line in text.split('\n') if line.strip()]
    for line in lines:
        match = pattern.search(line)
        if match:
            date = match.group(1)
            narration = match.group(2).strip()
            
            # Extract all numeric values at the end of the line
            nums = []
            for i in [3, 4, 5]:
                if match.group(i):
                    nums.append(float(match.group(i).replace(',', '')))
            
            withdrawal, deposit = 0.0, 0.0
            
            if len(nums) == 3:
                # Format: Withdrawal | Deposit | Balance
                withdrawal, deposit = nums[0], nums[1]
            elif len(nums) == 2:
                # Format: (Withdrawal or Deposit) | Balance
                # We guess based on common descriptors
                val = nums[0]
                if any(x in narration.upper() for x in ["SALARY", "INTEREST", "REFUND", "CREDIT", "CR"]):
                    deposit = val
                else:
                    withdrawal = val
            
            if withdrawal > 0 or deposit > 0:
                transactions.append({
                    "Date": date,
                    "Description": narration,
                    "Withdrawal": withdrawal,
                    "Deposit": deposit,
                    "Category": "Others"
                })
                
    print(f"✅ Parser found {len(transactions)} valid transactions.")
    return transactions

def get_ai_insights(text):
    """
    THE ANALYST: Uses Llama 3 for high-level insights.
    """
    print("🤖 [3/3] AI is generating short financial insights...")
    
    text_snippet = text[:2000]
    
    prompt = f"""
    Analyze these transactions and provide 3 SHORT financial insights.
    Respond in STRICT JSON ONLY.
    
    Format:
    {{
      "insights": ["insight 1", "insight 2", "insight 3"],
      "anomalies": [{{"desc": "...", "amount": 0.0, "reason": "..."}}]
    }}
    
    DATA:
    {text_snippet}
    """

    try:
        response = requests.post(
            "http://127.0.0.1:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False,
                "options": {"num_ctx": 4096, "temperature": 0.0, "num_predict": 300}
            },
            timeout=30
        )
        
        if response.status_code == 200:
            res_content = response.json().get('response', '')
            match = re.search(r"\{.*\}", res_content, re.DOTALL)
            if match:
                return json.loads(match.group())
        
        return {"insights": ["Unable to generate AI insights."], "anomalies": []}
    except:
        return {"insights": ["AI Analyst is offline."], "anomalies": []}

def _preprocess_image_for_ocr(file_bytes):
    """Enhance image quality for better OCR accuracy."""
    img = Image.open(io.BytesIO(file_bytes)).convert("L")  # Grayscale
    img = img.filter(ImageFilter.SHARPEN)                   # Sharpen edges
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.0)                             # Boost contrast
    # Scale up small images for better OCR
    w, h = img.size
    if w < 1200:
        scale = 1200 / w
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    return img


def extract_data_from_image(file_bytes):
    """
    3-Stage Image Pipeline:
      Stage 1 (PRIMARY):  Pillow + Tesseract OCR → regex parser (same as PDF)
      Stage 2 (FALLBACK): Moondream vision → Llama 3 JSON structuring
      Stage 3 (LAST):     Direct regex on Moondream raw text
    """

    # ── STAGE 1: TESSERACT OCR (Best Quality) ─────────────────────────────────
    if PIL_AVAILABLE and TESSERACT_AVAILABLE:
        print("🔍 [1/3] Running Tesseract OCR on image...")
        try:
            img = _preprocess_image_for_ocr(file_bytes)
            ocr_text = pytesseract.image_to_string(img, config="--psm 6")
            print(f"✅ Tesseract extracted {len(ocr_text)} chars:\n{ocr_text[:400]}\n")
            if ocr_text and len(ocr_text) > 50:
                # Run same regex parser used for PDFs
                transactions = extract_transactions_regex(ocr_text)
                if transactions:
                    print(f"✅ OCR + Regex found {len(transactions)} transactions.")
                    return {"transactions": transactions}
                else:
                    print("⚠️ OCR text found but regex found 0 transactions. Trying AI stage...")
        except Exception as e:
            print(f"⚠️ Tesseract failed: {e}. Falling back to Moondream...")
    else:
        print("⚠️ Tesseract/Pillow not available. Using Moondream vision...")

    # ── STAGE 2: MOONDREAM + LLAMA 3 ──────────────────────────────────────────
    print("👁️ [2/3] Moondream reading image...")
    base64_image = base64.b64encode(file_bytes).decode("utf-8")
    vision_text  = ""
    try:
        resp = requests.post(
            "http://127.0.0.1:11434/api/generate",
            json={
                "model": "moondream",
                "prompt": (
                    "This is a bank statement image. "
                    "Read every row in the transactions table and output them line by line in this exact format:\n"
                    "DATE | DESCRIPTION | WITHDRAWAL_AMOUNT | DEPOSIT_AMOUNT\n"
                    "Use 0 if a field is empty. Output ONLY the rows, nothing else."
                ),
                "images": [base64_image],
                "stream": False,
                "options": {"num_ctx": 4096, "temperature": 0.0},
            },
            timeout=120,
        )
        if resp.status_code == 200:
            vision_text = resp.json().get("response", "").strip()
            print(f"✅ Moondream returned {len(vision_text)} chars:\n{vision_text[:400]}\n")
    except Exception as e:
        print(f"❌ Moondream error: {e}")

    if vision_text and len(vision_text) > 30:
        # Ask Llama 3 to structure Moondream's output
        print("🤖 [3/3] Llama 3 structuring Moondream output...")
        llm_prompt = f"""You are a bank statement parser. Parse the following text into a JSON array.

Each item MUST have exactly these keys:
- "Date" (string, e.g. "01-Jan-2024")
- "Description" (string)
- "Withdrawal" (float, 0.0 if none)
- "Deposit" (float, 0.0 if none)

Return ONLY the JSON array. No explanation. No markdown.

TEXT:
{vision_text[:3000]}

JSON:"""
        try:
            llm_resp = requests.post(
                "http://127.0.0.1:11434/api/generate",
                json={
                    "model": "llama3",
                    "prompt": llm_prompt,
                    "stream": False,
                    "options": {"num_ctx": 4096, "temperature": 0.0, "num_predict": 2048},
                },
                timeout=60,
            )
            if llm_resp.status_code == 200:
                raw   = llm_resp.json().get("response", "")
                match = re.search(r"\[.*?\]", raw, re.DOTALL)
                if match:
                    parsed = json.loads(match.group())
                    clean  = []
                    for t in parsed:
                        try:
                            clean.append({
                                "Date":        str(t.get("Date", "N/A")),
                                "Description": str(t.get("Description", "N/A")),
                                "Withdrawal":  float(t.get("Withdrawal", 0) or 0),
                                "Deposit":     float(t.get("Deposit",    0) or 0),
                            })
                        except Exception:
                            continue
                    if clean:
                        print(f"✅ Llama 3 structured {len(clean)} transactions.")
                        return {"transactions": clean}
        except Exception as e:
            print(f"⚠️ Llama 3 structuring failed: {e}")

        # ── STAGE 3: REGEX directly on Moondream text ─────────────────────────
        print("⚡ Regex fallback on Moondream text...")
        transactions = []
        for line in vision_text.split("\n"):
            line = line.strip()
            if not line:
                continue
            date_m = re.search(r"(\d{1,4}[-/\.]\w{2,3}[-/\.]\d{2,4}|\d{1,2}[-/\.]\d{1,2}[-/\.]\d{2,4}|\d{1,2}\s+[a-zA-Z]{3,4}\s+\d{2,4}|\d{1,2}[-/\.]\d{1,2})", line)
            nums   = re.findall(r"(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)", line)
            if nums:
                date  = date_m.group(0) if date_m else "N/A"
                parts = [p.strip() for p in line.split("|")]
                desc  = parts[1] if len(parts) > 1 else line[:60]
                vals  = [float(n.replace(",", "")) for n in nums if float(n.replace(",", "")) > 0]
                if not vals:
                    continue
                amt   = vals[0]
                is_cr = any(w in line.upper() for w in
                            ["SALARY","CREDIT","INWARD","DEPOSIT","REFUND","CR","INTEREST","RTGS IN"])
                transactions.append({
                    "Date":        date,
                    "Description": desc,
                    "Withdrawal":  0.0 if is_cr else amt,
                    "Deposit":     amt  if is_cr else 0.0,
                })
        if transactions:
            print(f"⚡ Regex fallback found {len(transactions)} transactions.")
            return {"transactions": transactions}

    print("⚠️ All AI extraction failed. Falling back to Demo Mode data to save the hackathon demo...")
    mock_transactions = [
        {"Date": "12-Oct-2023", "Description": "AMAZON RETAIL INDIA", "Withdrawal": 1499.0, "Deposit": 0.0},
        {"Date": "14-Oct-2023", "Description": "SWIGGY FOOD DELIVERY", "Withdrawal": 450.0, "Deposit": 0.0},
        {"Date": "15-Oct-2023", "Description": "SALARY CREDIT NEFT", "Withdrawal": 0.0, "Deposit": 85000.0},
        {"Date": "16-Oct-2023", "Description": "UBER INDIA RIDES", "Withdrawal": 320.0, "Deposit": 0.0},
        {"Date": "18-Oct-2023", "Description": "STARBUCKS COFFEE", "Withdrawal": 450.0, "Deposit": 0.0},
    ]
    return {"transactions": mock_transactions, "narrative": "Notice: Local Vision processing failed. Displaying simulated demo transactions."}


