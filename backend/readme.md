Here is your **🔥 FINAL COMPLETE BACKEND README (copy-paste ready for GitHub)** including your `api.py` (FastAPI backend) + all modules.

---

# 🚀 FinLens Agentia 2.0 – Backend

An **AI-powered financial analysis backend** that extracts, processes, categorizes, and detects anomalies in bank transactions from PDFs, images, and spreadsheets.

---

## 📌 Overview

This backend provides an **end-to-end pipeline**:

> 📂 Upload → 📊 Extract → 🧠 Analyze → ⚠️ Detect Anomalies → 📈 Insights

It integrates:

* Rule-based data processing
* AI-powered insights using Llama3
* OCR + Vision fallback for images

---

## 🧠 Core Features

### 📄 1. Multi-Format Data Extraction

* PDF parsing using `pdfplumber`
* Image OCR using `pytesseract`
* AI Vision fallback (Moondream via Ollama)
* Excel/CSV support

Handled in: 

---

### ⚡ 2. Smart Transaction Parsing

* Ultra-fast regex-based extraction
* Supports multiple bank formats
* Handles:

  * Withdrawal / Deposit / Balance formats

---

### 🧾 3. Chart of Accounts (CoA)

* Auto categorization of transactions:

  * Food 🍔
  * Shopping 🛒
  * Bills 💡
  * Investments 📈

Handled in: 

---

### ⚠️ 4. Anomaly Detection Engine

Detects:

* High-value transactions
* Statistical outliers (z-score)
* Duplicate transactions
* Late-night activity
* Sudden spikes

Handled in: 

---

### 🤖 5. AI Financial Insights

* Powered by **Llama3 (Ollama)**
* Generates:

  * Insights
  * AI-detected anomalies

---

### 💬 6. AI Chat Assistant

* Ask questions about your transactions
* Context-aware financial assistant

---

### 📥 7. Excel Export

* Download processed transactions as `.xlsx`

---

## 🗂️ Project Structure

```bash
backend/
│
├── api.py              # FastAPI backend (main server)
├── extractor.py        # PDF/Image/OCR/AI extraction
├── coa_mapper.py       # Transaction categorization
├── anomaly.py          # Anomaly detection engine
├── requirements.txt    # Dependencies
```

---

## ⚙️ Tech Stack

* **Framework:** FastAPI
* **AI Engine:** Ollama (Llama3, Moondream)
* **Data Processing:** Pandas, NumPy
* **OCR:** Tesseract + Pillow
* **PDF Parsing:** pdfplumber
* **File Handling:** openpyxl
* **API Server:** Uvicorn

---

## 📥 Installation

```bash
# Clone repository
git clone <your-repo-url>
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

Dependencies: 

---

## ⚠️ Prerequisites

### 1. Install Tesseract OCR

```
C:\Program Files\Tesseract-OCR\tesseract.exe
```

---

### 2. Install & Run Ollama

```bash
ollama run llama3
ollama run moondream
```

Make sure this endpoint works:

```
http://localhost:11434
```

---

## ▶️ Running the Backend

```bash
uvicorn api:app --reload
```

Server runs at:

```
http://127.0.0.1:8000
```

---

## 🔌 API Endpoints

### 🏠 Health Check

```
GET /
```

Response:

```json
{
  "status": "Online",
  "engine": "Ollama (Llama3/Moondream)"
}
```

---

### 📂 Upload & Analyze File

```
POST /extract
```

Supports:

* PDF
* Image (JPG, PNG)
* Excel / CSV

Response:

```json
{
  "transactions": [...],
  "summary": {
    "total_debit": 50000,
    "total_credit": 80000,
    "transaction_count": 25,
    "net_balance": 30000
  },
  "narrative": "AI insights here",
  "llm_anomalies": [...]
}
```

---

### 💬 AI Chat

```
POST /chat
```

Body:

```json
{
  "prompt": "Where am I spending the most?",
  "context": "transaction summary here"
}
```

---

### 📥 Download Excel

```
GET /download
```

Downloads processed transaction report.

---

## 🔄 Processing Pipeline

### Step 1: Extraction

* PDF → Text → Regex
* Image → OCR → AI fallback

---

### Step 2: Categorization

Adds:

* `CoA_Category`
* `CoA_Reason`

---

### Step 3: Anomaly Detection

Adds:

* `Amount`
* `Anomaly`
* `Reason`

---

### Step 4: AI Insights

* Generates summary + anomalies

---

## 📊 Example Output

```json
{
  "Date": "15-06-2024",
  "Description": "PETROL PUMP",
  "Withdrawal": 2000,
  "Deposit": 0,
  "CoA": "Transportation",
  "Anomaly": "Yes",
  "Reason": "Late-night transaction"
}
```

---

## 🚨 Error Handling

* OCR failure → AI fallback
* AI failure → safe default insights
* No data → helpful error message

---

## 🌟 Key Highlights

* ⚡ Fast regex engine (milliseconds parsing)
* 🤖 AI + Rule-based hybrid system
* 🔄 Fully automated pipeline
* 🧩 Modular architecture

---

## 🚀 Future Enhancements

🤖 Advanced Machine Learning-Based Anomaly Detection
🔐 Intelligent Fraud Detection & Risk Analysis System
🚨 Real-Time High Spending & Smart Alert System

---

## 👥 Team Roles (Hackathon)

* Backend Developer → APIs + pipeline
* Data Engineer → Processing + anomaly logic
* Frontend Developer → Dashboard

---

## 🏁 Conclusion

This backend delivers a **powerful AI financial assistant** capable of:

✔ Extracting messy bank data
✔ Structuring it intelligently
✔ Detecting anomalies
✔ Providing actionable insights



Just tell 👍
