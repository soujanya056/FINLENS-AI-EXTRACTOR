## 🚀 LIVE DEMO STARTED

# team52
Here’s your **FULL COMBINED README (Frontend + Backend)** — clean, professional, and **ready to copy-paste into GitHub** 👇
(based on your actual app structure and tech stack )

---

````markdown
# 🏦 FinLens 2.0 — AI Bank Statement Intelligence

FinLens is an **AI-powered financial analytics platform** that transforms raw bank statements into meaningful insights using AI.

Upload your bank statement (PDF, Excel, CSV, or Image) and get:
- 📊 Financial dashboards
- 🚨 Anomaly detection
- 📑 Tax estimation
- 💬 AI-powered financial assistant
- 🏦 Loan eligibility insights

Built by **Team Ignite** 🚀

---

## 🚀 Features

### 📤 Smart File Upload
- Supports:
  - PDF
  - Excel (.xlsx)
  - CSV
  - Images 

---

### 📊 Financial Dashboard
- Total Income, Expenses, Savings
- Monthly spending trends
- Category-wise analysis
- Interactive charts (Plotly)

---

### 🚨 AI Anomaly Detection
Detects suspicious transactions based on:
- Odd timings (11 PM – 4 AM)
- High debit amounts

Outputs:
- Flagged transactions
- Reason for anomaly

---

### 📑 Tax & GST Estimation
- GST on income
- Deductible expenses
- Estimated tax liability

---

### 💬 AI Financial Assistant
- Ask questions about your data
- Context-aware responses using AI (Ollama / LLM)

---

### 🏦 Loan Eligibility Check
- Credit limit estimation
- Financial health score
- Expense analysis

---

### 🌐 Multi-Language Support
- English
- Telugu
- Hindi

---

### 🎨 UI Features
- Light/Dark mode
- Modern responsive design
- Interactive dashboards

---

## 🛠️ Tech Stack

### 🔹 Frontend
- Streamlit
- Plotly
- Pandas
- Requests

### 🔹 Backend
- FastAPI
- Uvicorn
- Python-Multipart

### 🔹 AI & Processing
- Ollama (LLM)
- PDFPlumber (PDF parsing)
- OpenPyXL (Excel support)
- dotenv (environment configs)

---

## 📦 Installation & Setup

### 1️⃣ Clone the repository

```bash
git clone <your-repo-url>
cd FinLens
````

---

### 2️⃣ Install dependencies

```bash
pip install streamlit pandas plotly requests pdfplumber python-dotenv ollama openpyxl fastapi uvicorn python-multipart
```

---

## ⚙️ Running the Project

### ▶️ Step 1: Start Backend

```bash
uvicorn api:app --reload --port 8002
```

Backend will run at:

```
http://127.0.0.1:8002
```

---

### ▶️ Step 2: Start Frontend

```bash
streamlit run app.py
```

---

## 🔗 API Endpoints

### 📌 `/extract`

* Input: Bank statement file
* Output:

```json
{
  "transactions": [...],
  "summary": {
    "total_credit": 50000,
    "total_debit": 30000,
    "net_balance": 20000
  },
  "narrative": "AI-generated insights"
}
```

---

### 📌 `/chat`

* Input: User query
* Output: AI-generated response

---

## 🧠 How It Works

```text
Upload File → Backend Processing → Data Cleaning → Analytics → Anomaly Detection → API → Frontend Dashboard
```

---

## 📂 Project Structure

```
FinLens/
│
├── frontend/
│   └── app.py          # Streamlit UI
│
├── backend/
│   └── api.py          # FastAPI backend
│
├── .env
├── requirements.txt
└── README.md
```

---

## 🔐 Privacy

* Runs locally (offline support with Ollama)
* No sensitive financial data is stored externally

---

## 🧪 Example Use Case

* Upload bank statement
* View spending insights
* Detect fraud/anomalies
* Ask AI questions
* Check loan eligibility

---

## 👨‍💻 Team

**Team Ignite**
SriCity Hackathon Project 🚀

---

## 🔮 Future Scope

* ML-based fraud detection
* Open banking integration (real-time data)
* Mobile app with voice assistant
* Predictive financial analytics
* Blockchain-based data security

---



