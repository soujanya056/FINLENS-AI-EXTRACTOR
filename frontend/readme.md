# 🎨 FinLens Frontend — AI Financial Dashboard

This is the **frontend UI** for FinLens 2.0, an AI-powered bank statement analysis platform.

Built using **Streamlit**, this interface allows users to upload bank statements and visualize insights such as spending patterns, anomalies, tax estimates, and loan eligibility.

---

## 🚀 Features

### 📤 File Upload
- Upload bank statements in:
  - PDF
  - Excel (.xlsx)
  - CSV
  - Images 

---

### 📊 Dashboard
- Total Income, Expenses, Savings
- Monthly spending trends
- Category-wise expense breakdown
- AI-generated financial insights

---

### 📋 Transactions Viewer
- Displays all parsed transactions
- Clean tabular format
- Scrollable & interactive

---

### 🚨 AI Anomaly Detection
- Detects suspicious transactions based on:
  - Odd timings (11 PM – 4 AM)
  - High debit amounts
- Shows:
  - Flagged transactions
  - Reason for anomaly

---

### 📑 Tax & GST Estimation
- GST on income
- Deductible expenses
- Estimated tax liability

---

### 💬 AI Chat Assistant
- Ask questions about your finances
- Context-aware responses from backend AI

---

### 🏦 Loan Eligibility Check
- Estimated credit limit
- Financial health score
- Monthly spending insights

---

### 🌐 Multi-Language Support
- English
- Telugu
- Hindi

---

### 🎨 UI Features
- Light/Dark mode toggle
- Modern responsive design
- Interactive charts (Plotly)

---

## 🛠️ Tech Stack

- **Streamlit** — UI framework
- **Plotly** — Charts & visualization
- **Pandas** — Data handling
- **Requests** — API communication

---

## ⚙️ Setup Instructions

### 1️⃣ Install dependencies

```bash
pip install streamlit pandas plotly requests
````

---

### 2️⃣ Run the frontend

```bash
streamlit run app.py
```

---

## 🔗 Backend Requirement

This frontend connects to a backend API.

Make sure backend is running at:

```
http://127.0.0.1:8002
```

### Required endpoints:

* `/extract` → for statement processing
* `/chat` → for AI assistant

---

## 📂 Project Structure

```
frontend/
 └── app.py
```

---

## 📌 Notes

* Backend must be running before using the app
* Supports real-time analysis after file upload
* Works best with structured bank statements

---

## 👨‍💻 Team

**Team Ignite**
Built for SriCity Hackathon 🚀

---

## 📃 License

For educational and hackathon use only.
