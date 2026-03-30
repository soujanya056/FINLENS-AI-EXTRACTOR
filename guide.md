# 🏦 Beginner's Guide: Offline Bank Statement AI

Welcome! This guide will help you set up and run your fully offline bank statement analysis tool. This project uses **FastAPI** for the backend, **Streamlit** for the dashboard, and **Llama 3 (Ollama)** as the local AI brain.

---

## 📂 Project Structure
Place your files in a folder named `bank-statement-ai`. It should look like this:

```text
bank-statement-ai/
├── api.py            # The Backend (FastAPI) - Handles logic & Excel
├── app.py            # The Frontend (Streamlit) - The Dashboard
├── extractor.py      # The Brain (Llama 3) - Parses the PDF text
├── coa_mapper.py     # Categorization logic
├── anomaly.py        # Risk detection logic
└── requirements.txt  # List of Python plugins needed
```

---

## 🛠️ Step 1: Install Python & Plugins
1.  **Install Python**: Download and install Python from [python.org](https://www.python.org/).
2.  **Open Terminal**: Navigate to your project folder (`bank-statement-ai`).
3.  **Install requirements**: Run this command to install all necessary tools:
    ```bash
    pip install -r requirements.txt
    ```

---

## 🤖 Step 2: Install Llama 3 (Ollama)
Since we are staying **100% Offline**, we need to run the AI on your computer.
1.  **Download Ollama**: Visit [ollama.com](https://ollama.com/) and download the app for Windows.
2.  **Run Ollama**: Once installed, open your command prompt (cmd) and type:
    ```bash
    ollama run llama3
    ```
    *This will download the 8GB Llama 3 model. Once it's done, you can close the terminal.*

---

## 🚀 Step 3: Run the Application
You need to have **TWO** terminal windows open to run the project.

### Part A: Start the Backend (The Engine)
In your first terminal, run:
```bash
uvicorn api:app --port 8001
```
*Wait until it says "Application startup complete".*

### Part B: Start the Frontend (The Dashboard)
In your second terminal, run:
```bash
streamlit run app.py
```
*Your browser will automatically open the dashboard!*

---

## 🏦 How to use it:
1.  **Upload PDF**: Drag and drop any Indian bank statement PDF.
2.  **AI Analysis**: The app sends the data to your local **Llama 3**. Wait about 20-30 seconds.
3.  **Review**: See your spending charts, detected anomalies, and totals.
4.  **Download**: Click the "Download Excel Report" button to get a professional file for your records.

---

## ⚠️ Common Troubleshooting
*   **"Llama 3 Not Found"**: Make sure you ran `ollama run llama3` at least once.
*   **"Connection Error"**: Ensure the Backend (api.py) is running on port 8001 before you upload a file.
*   **"PDF Error"**: Extremely complex or password-protected PDFs might fail. Use a standard clear PDF for best results.

---
**Enjoy your private and secure financial intelligence tool!**
