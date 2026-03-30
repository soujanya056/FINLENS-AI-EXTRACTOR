import os
import json
import io
import pandas as pd
import requests
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
from extractor import extract_text_from_pdf, extract_transactions_regex, get_ai_insights, extract_data_from_image
from coa_mapper import map_coa
from anomaly import detect_anomalies

# ── INITIALIZE BACKEND ────────────────────────────────────────────────────────
app = FastAPI(title="FinLens Agentia 2.0 Backend")

LATEST_DATA = None

@app.get("/")
def home():
    return {"status": "Online", "engine": "Ollama (Llama3/Moondream)"}

@app.post("/chat")
async def chat_api(request: dict):
    prompt = request.get("prompt", "")
    context = request.get("context", "")
    
    full_prompt = f"""
    You are FinLens AI, a professional financial analyst.
    Use the following bank statement summary to answer the user's question:
    
    CONTEXT:
    {context}
    
    USER QUESTION:
    {prompt}
    
    Provide a sharp, professional answer. Keep it concise but insightful.
    """
    
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "llama3", "prompt": full_prompt, "stream": False},
            timeout=90
        )
        return {"response": response.json().get("response", "I'm standing by to help.")}
    except requests.exceptions.Timeout:
        return {"response": "⏳ Llama 3 took too long to respond. Please try a shorter question."}
    except Exception as e:
        return {"response": f"🔌 Could not reach Ollama. Make sure it's running. ({str(e)[:60]})"}

@app.post("/extract")
async def extract_api(file: UploadFile = File(...)):
    global LATEST_DATA
    try:
        content = await file.read()
        filename = file.filename.lower()
        
        # 1. ROUTE BY FILE TYPE
        if filename.endswith((".png", ".jpg", ".jpeg")):
            res = extract_data_from_image(content)
            transactions = res.get("transactions", [])
            # Build analysis text from actual transaction data for AI insights
            if transactions:
                lines = []
                for t in transactions:
                    lines.append(
                        f"{t.get('Date','')}: {t.get('Description','')} "
                        f"DR:{t.get('Withdrawal',0)} CR:{t.get('Deposit',0)}"
                    )
                analysis_text = "\n".join(lines[:60])  # send up to 60 rows to Llama3
            else:
                analysis_text = "No transactions could be extracted from this image."
        elif filename.endswith((".xlsx", ".xls", ".csv")):
            # Handle Excel/CSV files
            try:
                if filename.endswith(".csv"):
                    df_raw = pd.read_csv(io.BytesIO(content))
                else:
                    df_raw = pd.read_excel(io.BytesIO(content))
                transactions = df_raw.to_dict(orient="records")
                analysis_text = df_raw.to_string(max_rows=60)
            except Exception as ex:
                return {"error": f"Could not read file: {ex}"}
        else:
            raw_text = extract_text_from_pdf(content)
            if not raw_text: return {"error": "Could not read PDF text."}
            transactions = extract_transactions_regex(raw_text)
            analysis_text = raw_text[:2000]

        # 2. GET AI INSIGHTS (Llama 3)
        ai_data = get_ai_insights(analysis_text)
        llm_insights = ai_data.get("insights", [])
        llm_anomalies = ai_data.get("anomalies", [])

        # 3. NORMALIZE & ENHANCE
        df = pd.DataFrame(transactions)
        if df.empty:
            return {
                "error": "No transactions found.",
                "hint": "For images: ensure the statement is clear/high-res. For PDFs: ensure text is selectable (not scanned)."
            }
            
        # Ensure standard columns
        for col in ["Withdrawal", "Deposit", "Date", "Description"]:
            if col not in df.columns: df[col] = 0.0 if col in ["Withdrawal", "Deposit"] else "N/A"
        
        df = map_coa(df)
        if "CoA_Category" in df.columns:
            df["CoA"] = df["CoA_Category"]
        
        df["Debit"] = df["Withdrawal"]
        df["Credit"] = df["Deposit"]
        
        try:
            df = detect_anomalies(df)
        except: pass

        # 4. CLEAN FOR JSON (Replace NaNs with 0)
        df = df.fillna(0)
        df["Withdrawal"] = pd.to_numeric(df["Withdrawal"], errors='coerce').fillna(0)
        df["Deposit"] = pd.to_numeric(df["Deposit"], errors='coerce').fillna(0)
        
        # 5. PREPARE RESPONSE
        total_dr = float(df["Withdrawal"].sum())
        total_cr = float(df["Deposit"].sum())
        
        LATEST_DATA = df.copy()
        
        return {
            "transactions": df.to_dict(orient="records"),
            "summary": {
                "total_debit": total_dr,
                "total_credit": total_cr,
                "transaction_count": len(df),
                "net_balance": total_cr - total_dr,
                "bank": "Detected Bank"
            },
            "narrative": " ".join(llm_insights) if llm_insights else "Analysis complete.",
            "llm_anomalies": llm_anomalies
        }
    except Exception as e:
        return {"error": f"Internal Engine Error: {str(e)}"}

@app.get("/download")
async def download_excel():
    global LATEST_DATA
    if LATEST_DATA is None: return {"error": "No data."}
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        LATEST_DATA.to_excel(writer, index=False, sheet_name='Data')
    output.seek(0)
    return StreamingResponse(output, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', headers={"Content-Disposition": 'attachment; filename="Report.xlsx"'})
