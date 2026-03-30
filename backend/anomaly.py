"""
anomaly_detector.py
-------------------
Explainable anomaly detection for bank transaction DataFrames.

Public API:
    detect_anomalies(df, z_threshold, high_value_threshold)
    -> df with added "Amount", "Anomaly", "Reason" columns

Integrates directly with extractor.py and coa_mapper.py output.
"""

import re
import pandas as pd
import numpy as np


# ── Config ─────────────────────────────────────────────────────────────────────

DEFAULT_HIGH_VALUE   = 50_000   # flag if amount exceeds this
DEFAULT_Z_THRESHOLD  = 2.5      # flag if z-score exceeds this
LATE_NIGHT_START     = 23      # 10 PM
LATE_NIGHT_END       = 5        # 5 AM


# ── Individual detection rules ─────────────────────────────────────────────────

def _rule_high_value(amount: float, threshold: float) -> str | None:
    if pd.notna(amount) and amount > threshold:
        return f"⚠️ High value transfer (₹{amount:,.0f} exceeds ₹{threshold:,.0f} limit)"
    return None


def _rule_zscore(amount: float, mean: float, std: float, threshold: float) -> str | None:
    if std == 0 or pd.isna(amount):
        return None
    z = abs((amount - mean) / std)
    if z > threshold:
        return f"Statistical spike (z-score={z:.2f})"
    return None


def _rule_duplicate(idx: int, df: pd.DataFrame) -> str | None:
    row = df.iloc[idx]
    dupes = df[
        (df["Amount"]      == row["Amount"]) &
        (df["Description"] == row["Description"].split("#")[0].strip()) &
        (df.index          != idx)
    ]
    if not dupes.empty:
        return f"Possible duplicate of row(s) {dupes.index.tolist()}"
    return None


def _rule_late_night(description: str, time_str: str = "") -> str | None:
    # Check dedicated Time column first (e.g. "23:45:00" or "23:45")
    time_to_check = str(time_str).strip() if time_str else ""
    if not time_to_check or time_to_check in ("", "nan", "0", "N/A"):
        # Fallback: find time pattern embedded in description
        time_to_check = str(description)
    match = re.search(r"\b(\d{1,2}):(\d{2})\b", time_to_check)
    if not match:
        return None
    hour = int(match.group(1))
    if hour >= LATE_NIGHT_START or hour < LATE_NIGHT_END:
        return f"🌙 Late-night transaction at {hour:02d}:{match.group(2)} (after 11 PM)"
    return None


def _rule_sudden_spike(idx: int, df: pd.DataFrame, multiplier: float = 3.0) -> str | None:
    row    = df.iloc[idx]
    amount = row["Amount"]
    col    = row["_type"]
    if pd.isna(amount) or amount == 0:
        return None

    same_type = df[df["_type"] == col]["Amount"].dropna()
    if len(same_type) < 3:
        return None

    past_values  = same_type.iloc[:idx] if idx > 0 else same_type
    rolling_mean = past_values.mean() if len(past_values) > 0 else same_type.mean()

    if rolling_mean > 0 and amount > multiplier * rolling_mean:
        return f"📈 Sudden spike ({multiplier:.0f}x rolling avg of ₹{rolling_mean:,.0f})"
    return None


# ── Main function ──────────────────────────────────────────────────────────────

def detect_anomalies(
    df: pd.DataFrame,
    high_value_threshold: float = DEFAULT_HIGH_VALUE,
    z_threshold: float          = DEFAULT_Z_THRESHOLD,
) -> pd.DataFrame:
    """
    Run all anomaly rules on the transaction DataFrame.

    Args:
        df:                   DataFrame with Date, Description, Debit, Credit columns.
        high_value_threshold: Flag transactions above this amount.
        z_threshold:          Flag transactions whose z-score exceeds this.

    Returns:
        New DataFrame with added columns: Amount, Anomaly, Reason.
    """
    df = df.copy().reset_index(drop=True)

    # ── Build unified Amount column ────────────────────────────────────────────
    df["Debit"]  = pd.to_numeric(df.get("Debit"),  errors="coerce")
    df["Credit"] = pd.to_numeric(df.get("Credit"), errors="coerce")
    df["Amount"] = df["Debit"].fillna(df["Credit"])
    df["_type"]  = df.apply(
        lambda r: "Debit" if pd.notna(r["Debit"]) else "Credit", axis=1
    )

    # ── Pre-compute stats for z-score ─────────────────────────────────────────
    amounts     = df["Amount"].dropna()
    global_mean = amounts.mean()
    global_std  = amounts.std()

    # ── Evaluate each row ──────────────────────────────────────────────────────
    anomaly_flags  = []
    reason_strings = []

    for i, row in df.iterrows():
        amt      = row["Amount"]
        desc     = str(row.get("Description", ""))
        time_val = str(row.get("Time", ""))  # Check for dedicated Time column
        reasons  = []

        for r in (
            _rule_high_value(amt, high_value_threshold),
            _rule_zscore(amt, global_mean, global_std, z_threshold),
            _rule_duplicate(i, df),
            _rule_late_night(desc, time_val),
            _rule_sudden_spike(i, df),
        ):
            if r:
                reasons.append(r)

        anomaly_flags.append("Yes" if reasons else "No")
        reason_strings.append("; ".join(reasons) if reasons else "-")

    df["Anomaly"] = anomaly_flags
    df["Reason"]  = reason_strings
    df = df.drop(columns=["_type"])

    return df


# ── Summary helper (useful for Streamlit) ──────────────────────────────────────

def anomaly_summary(df: pd.DataFrame) -> dict:
    """Return quick stats after detect_anomalies() has been run."""
    flagged = df[df["Anomaly"] == "Yes"]
    return {
        "total":             len(df),
        "flagged":           len(flagged),
        "flagged_pct":       round(len(flagged) / len(df) * 100, 1) if len(df) else 0,
        "total_flagged_amt": round(flagged["Amount"].sum(), 2),
        "top_reasons": (
            flagged["Reason"]
            .str.split("; ")
            .explode()
            .value_counts()
            .head(5)
            .to_dict()
        ),
    }


# ── Demo ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    sample = pd.DataFrame([
        {"Date": "01-06-2024", "Description": "NEFT SALARY CREDIT",            "Debit": None,    "Credit": 85000.0},
        {"Date": "02-06-2024", "Description": "UPI/AMAZON SHOPPING",            "Debit": 4500.0,  "Credit": None},
        {"Date": "03-06-2024", "Description": "SWIGGY ORDER #98123",            "Debit": 450.0,   "Credit": None},
        {"Date": "05-06-2024", "Description": "ATM WITHDRAWAL SBI BRANCH",      "Debit": 10000.0, "Credit": None},
        {"Date": "07-06-2024", "Description": "BILL PAYMENT/ELECTRICITY BOARD", "Debit": 2300.0,  "Credit": None},
        {"Date": "10-06-2024", "Description": "IMPS/RENT TRANSFER TO OWNER",    "Debit": 25000.0, "Credit": None},
        {"Date": "12-06-2024", "Description": "UPI/SWIGGY ORDER #98123",        "Debit": 450.0,   "Credit": None},
        {"Date": "15-06-2024", "Description": "PETROL PUMP IOCL", "Time": "23:45", "Debit": 2000.0,  "Credit": None},
        {"Date": "18-06-2024", "Description": "NEFT/LIC INSURANCE PREMIUM",     "Debit": 12500.0, "Credit": None},
        {"Date": "20-06-2024", "Description": "UPI/NETFLIX SUBSCRIPTION",       "Debit": 649.0,   "Credit": None},
        {"Date": "22-06-2024", "Description": "GROWW MUTUAL FUND SIP",          "Debit": 5000.0,  "Credit": None},
        {"Date": "25-06-2024", "Description": "RTGS/PROPERTY TAX PAYMENT", "Time": "00:15", "Debit": 75000.0, "Credit": None},
        {"Date": "28-06-2024", "Description": "UPI/PETROL PUMP",                "Debit": 2000.0,  "Credit": None},
        {"Date": "30-06-2024", "Description": "INTEREST CREDIT Q2",             "Debit": None,    "Credit": 312.5},
    ])

    result = detect_anomalies(sample)

    pd.set_option("display.max_columns",  None)
    pd.set_option("display.width",        130)
    pd.set_option("display.max_colwidth", 55)

    print("── Full output ───────────────────────────────────────────────────────")
    print(result[["Date", "Description", "Amount", "Anomaly", "Reason"]].to_string(index=True))

    print("\n── Flagged only ──────────────────────────────────────────────────────")
    flagged = result[result["Anomaly"] == "Yes"]
    print(flagged[["Date", "Description", "Amount", "Reason"]].to_string(index=True))

    print("\n── Summary ───────────────────────────────────────────────────────────")
    for k, v in anomaly_summary(result).items():
        print(f"  {k:<22}: {v}")
