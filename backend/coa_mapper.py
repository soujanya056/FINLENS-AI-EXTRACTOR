"""
coa_mapper.py
-------------
Chart of Accounts (CoA) mapping for bank transactions.
Keyword-rule based, easy to extend, demo-ready.

Public API:
    map_coa(df)  →  df with added "CoA_Category" and "CoA_Reason" columns
"""

import re
import pandas as pd


# ── Rule table ─────────────────────────────────────────────────────────────────
# Each entry: (category_name, [keywords...])
# Rules are checked top-to-bottom; first match wins.
# To add a new category: just append a tuple here.

COA_RULES: list[tuple[str, list[str]]] = [
    ("Income",            ["salary", "payroll", "freelance", "interest credit", "int.pd",
                           "dividend", "bonus", "refund", "cashback", "reversal", "cr "]),

    ("Food & Dining",     ["swiggy", "zomato", "uber eats", "restaurant", "cafe",
                           "domino", "pizza", "barbeque", "mcdonalds", "kfc", "pos ",
                           "subway", "starbucks", "hotel", "dining", "food", "eat"]),

    ("Shopping",          ["amazon", "flipkart", "myntra", "ajio", "nykaa", "pos ",
                           "meesho", "snapdeal", "shopify", "bigbasket",
                           "blinkit", "zepto", "grofers", "supermarket",
                           "mall", "retail", "shop", "store", "dmart"]),

    ("Bills & Utilities", ["electricity", "water", "gas", "internet", "broadband",
                           "airtel", "jio", "vi ", "bsnl", "tata sky", "dth", "api ",
                           "bill payment", "utility", "recharge", "postpaid", "bbps",
                           "prepaid", "netflix", "spotify", "prime", "hotstar",
                           "insurance", "lic ", "premium", "chg", "fee", "tax"]),

    ("Transportation",    ["uber", "ola", "rapido", "metro", "fuel", "petrol",
                           "diesel", "parking", "fastag", "irctc", "train",
                           "flight", "airline", "indigo", "spicejet", "air india",
                           "bus", "cab", "auto", "toll"]),

    ("Healthcare",        ["hospital", "clinic", "pharmacy", "medical", "doctor",
                           "apollo", "fortis", "medicover", "health", "lab",
                           "diagnostic", "medicine", "chemist"]),

    ("Education",         ["school", "college", "university", "tuition", "course",
                           "udemy", "coursera", "fees", "coaching", "exam"]),

    ("Cash Withdrawal",   ["atm", "cash withdrawal", "cash wtdl", "wdl"]),

    ("Transfers",         ["neft", "rtgs", "imps", "upi", "transfer", "sent to",
                           "received from", "payment to", "pay to", "ft "]),

    ("Investments",       ["mutual fund", "sip", "zerodha", "groww", "upstox",
                           "kuvera", "stock", "equity", "nse", "bse", "gold",
                           "fd ", "fixed deposit", "rd ", "recurring deposit"]),

    ("Rent & Housing",    ["rent", "property", "maintenance", "housing", "society",
                           "landlord", "lease"]),
]

FALLBACK_CATEGORY = "Others"


# ── Core logic ─────────────────────────────────────────────────────────────────

def _match(description: str) -> tuple[str, str]:
    """
    Return (category, reason) for a single description string.
    Checks every rule; picks the first keyword that matches.
    """
    text = description.lower()
    # Tokenise loosely so "vi " matches "vi recharge" but not "advice"
    for category, keywords in COA_RULES:
        for kw in keywords:
            pattern = re.escape(kw.strip())
            if re.search(pattern, text):
                return category, f"matched '{kw.strip()}'"

    return FALLBACK_CATEGORY, "no keyword matched"


def map_coa(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add 'CoA_Category' and 'CoA_Reason' columns to the DataFrame.

    Args:
        df: Must contain a 'Description' column.

    Returns:
        New DataFrame with two extra columns appended.
    """
    df = df.copy()
    results = df["Description"].fillna("").apply(_match)
    df["CoA_Category"] = results.apply(lambda x: x[0])
    df["CoA_Reason"]   = results.apply(lambda x: x[1])
    return df


# ── Demo ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # sample = pd.DataFrame([
    #     {"Date": "01-06-2024", "Description": "NEFT SALARY CREDIT",            "Debit": None,    "Credit": 85000.0},
    #     {"Date": "02-06-2024", "Description": "UPI/AMAZON SHOPPING",            "Debit": 4500.0,  "Credit": None},
    #     {"Date": "03-06-2024", "Description": "SWIGGY ORDER #98123",            "Debit": 450.0,   "Credit": None},
    #     {"Date": "05-06-2024", "Description": "ATM WITHDRAWAL SBI BRANCH",      "Debit": 10000.0, "Credit": None},
    #     {"Date": "07-06-2024", "Description": "BILL PAYMENT/ELECTRICITY BOARD", "Debit": 2300.0,  "Credit": None},
    #     {"Date": "10-06-2024", "Description": "IMPS/RENT TRANSFER TO OWNER",    "Debit": 25000.0, "Credit": None},
    #     {"Date": "12-06-2024", "Description": "UPI/UBER CAB BOOKING",           "Debit": 320.0,   "Credit": None},
    #     {"Date": "15-06-2024", "Description": "INTEREST CREDIT Q2",             "Debit": None,    "Credit": 312.5},
    #     {"Date": "18-06-2024", "Description": "NEFT/LIC INSURANCE PREMIUM",     "Debit": 12500.0, "Credit": None},
    #     {"Date": "20-06-2024", "Description": "UPI/NETFLIX SUBSCRIPTION",       "Debit": 649.0,   "Credit": None},
    #     {"Date": "22-06-2024", "Description": "GROWW MUTUAL FUND SIP",          "Debit": 5000.0,  "Credit": None},
    #     {"Date": "25-06-2024", "Description": "APOLLO PHARMACY MEDICINES",      "Debit": 890.0,   "Credit": None},
    #     {"Date": "28-06-2024", "Description": "PETROL PUMP IOCL",               "Debit": 2000.0,  "Credit": None},
    #     {"Date": "30-06-2024", "Description": "UNKNOWN MERCHANT XYZ #4421",     "Debit": 150.0,   "Credit": None},
    # ])

    # result = map_coa(sample)

    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 120)
    pd.set_option("display.max_colwidth", 35)
    print(result[["Date", "Description", "Debit", "Credit", "CoA_Category", "CoA_Reason"]].to_string(index=False))

    print("\n── Category breakdown ─────────────────────────────")
    print(result["CoA_Category"].value_counts().to_string())

