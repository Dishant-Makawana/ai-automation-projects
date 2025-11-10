import os, json, time, random, logging
from datetime import datetime, date, timedelta
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from telethon import TelegramClient

# ================== BOOTSTRAP ==================
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

load_dotenv(BASE_DIR / ".env")

API_ID       = int(os.getenv("API_ID"))
API_HASH     = os.getenv("API_HASH")
SESSION_NAME = os.getenv("SESSION_NAME", "dishant_business_orch")
DEST_CHAT    = int(os.getenv("DEST_CHAT"))
UPDATE_SEC   = int(os.getenv("UPDATE_INTERVAL", "1800"))

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

logging.basicConfig(
    filename=str(BASE_DIR / "business_orchestrator.log"),
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

# ================== HELPERS ==================
def today_str():
    return date.today().strftime("%Y-%m-%d")

def yday_str():
    return (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")

def ensure_demo_files():
    """
    If expected files for today are missing, create realistic demo data
    so the orchestrator works out of the box for portfolio/demo.
    """
    # Sales: CSV with columns: order_id, amount
    sales_path = DATA_DIR / "sales_today.csv"
    if not sales_path.exists():
        rows = []
        order_count = random.randint(15, 45)
        for i in range(order_count):
            amt = random.randint(1500, 15000)  # INR
            rows.append({"order_id": f"{today_str()}-{1000+i}", "amount": amt})
        pd.DataFrame(rows).to_csv(sales_path, index=False)

    # Leads: JSON array of {name, source}
    leads_path = DATA_DIR / "leads_today.json"
    if not leads_path.exists():
        sources = ["Website", "Instagram", "Referral", "LinkedIn", "Ads"]
        leads = []
        for i in range(random.randint(10, 60)):
            leads.append({
                "name": f"Lead-{i+1}",
                "source": random.choice(sources)
            })
        with open(leads_path, "w", encoding="utf-8") as f:
            json.dump(leads, f, ensure_ascii=False, indent=2)

    # Attendance: CSV with columns: employee, present (1/0)
    att_path = DATA_DIR / "attendance_today.csv"
    if not att_path.exists():
        staff = [f"Emp-{i+1:02d}" for i in range(18, 28)]  # 18–27 employees
        rows = []
        for e in staff:
            present = 1 if random.random() > 0.06 else 0  # ~94% attendance
            rows.append({"employee": e, "present": present})
        pd.DataFrame(rows).to_csv(att_path, index=False)

def load_sales(path: Path):
    df = pd.read_csv(path)
    total_sales = int(df["amount"].sum())
    orders = int(len(df))
    avg_order = int(total_sales / orders) if orders > 0 else 0
    return {"total_sales": total_sales, "orders": orders, "avg_order": avg_order}

def load_leads(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        leads = json.load(f)
    count = len(leads)
    by_source = {}
    for l in leads:
        src = l.get("source", "Unknown")
        by_source[src] = by_source.get(src, 0) + 1
    # top 2 sources
    top_sources = sorted(by_source.items(), key=lambda x: x[1], reverse=True)[:2]
    top_fmt = " | ".join([f"{s}: {c}" for s, c in top_sources]) if top_sources else "N/A"
    return {"leads_count": count, "top_sources": top_fmt}

def load_attendance(path: Path):
    df = pd.read_csv(path)
    total = len(df)
    present = int(df["present"].sum())
    rate = round(100 * present / total, 1) if total > 0 else 0.0
    absents = total - present
    return {"headcount": total, "present": present, "absent": absents, "rate": rate}

def kpi_delta(today_val: int, yday_val: int):
    if yday_val is None or yday_val == 0:
        return None
    change = round(100 * (today_val - yday_val) / yday_val, 1)
    return change

def load_yday_metric(metric_name: str):
    """Optional: read yesterday snapshot from CSV log for delta."""
    log_path = BASE_DIR / "business_summary_log.csv"
    if not log_path.exists():
        return None
    try:
        df = pd.read_csv(log_path)
        df = df[df["date"] == yday_str()]
        if df.empty or metric_name not in df.columns:
            return None
        val = df[metric_name].values[-1]
        return float(val)
    except Exception:
        return None

def ai_style_insights(total_sales, leads_count, att_rate, d_sales, d_leads, d_att):
    # sales tone
    if d_sales is None:
        sales_line = f"Sales today look stable at ₹{total_sales:,}."
    elif d_sales >= 10:
        sales_line = f"Sales momentum is strong (↑{d_sales}%) at ₹{total_sales:,}."
    elif d_sales <= -10:
        sales_line = f"Sales under pressure (↓{abs(d_sales)}%) with ₹{total_sales:,}."
    else:
        sales_line = f"Sales steady (±{abs(d_sales)}%) at ₹{total_sales:,}."

    # leads tone
    if d_leads is None:
        leads_line = f"Leads captured: {leads_count}."
    elif d_leads >= 10:
        leads_line = f"Lead flow improving (↑{d_leads}%) with {leads_count} new inquiries."
    elif d_leads <= -10:
        leads_line = f"Lead flow slowed (↓{abs(d_leads)}%) with {leads_count} inquiries."
    else:
        leads_line = f"Lead flow stable (±{abs(d_leads)}%) with {leads_count} inquiries."

    # attendance tone
    if d_att is None:
        att_line = f"Attendance at {att_rate}%."
    elif d_att >= 2:
        att_line = f"Team presence improving (↑{d_att}%) at {att_rate}%."
    elif d_att <= -2:
        att_line = f"Team presence dipped (↓{abs(d_att)}%) at {att_rate}%."
    else:
        att_line = f"Team presence steady (±{abs(d_att)}%) at {att_rate}%."

    return sales_line, leads_line, att_line

def save_summary_row(row: dict):
    log_path = BASE_DIR / "business_summary_log.csv"
    df = pd.DataFrame([row])
    exists = log_path.exists()
    df.to_csv(log_path, mode="a", header=not exists, index=False)

# ================== MAIN ORCHESTRATION ==================
def run_once():
    ensure_demo_files()

    # Load today's files
    sales = load_sales(DATA_DIR / "sales_today.csv")
    leads = load_leads(DATA_DIR / "leads_today.json")
    att   = load_attendance(DATA_DIR / "attendance_today.csv")

    # Yesterday metrics (for delta %)
    y_sales = load_yday_metric("total_sales")
    y_leads = load_yday_metric("leads_count")
    y_att   = load_yday_metric("attendance_rate")

    d_sales = kpi_delta(sales["total_sales"], y_sales)
    d_leads = kpi_delta(leads["leads_count"], y_leads)
    d_att   = kpi_delta(att["rate"], y_att)

    # Insights
    s_line, l_line, a_line = ai_style_insights(
        sales["total_sales"], leads["leads_count"], att["rate"],
        d_sales, d_leads, d_att
    )

    # Build summary row for CSV
    row = {
        "date": today_str(),
        "total_sales": sales["total_sales"],
        "orders": sales["orders"],
        "avg_order": sales["avg_order"],
        "leads_count": leads["leads_count"],
        "attendance_rate": att["rate"],
        "absents": att["absent"],
        "delta_sales_pct": d_sales if d_sales is not None else "",
        "delta_leads_pct": d_leads if d_leads is not None else "",
        "delta_attendance_pct": d_att if d_att is not None else "",
        "time": datetime.now().strftime("%H:%M:%S"),
    }
    save_summary_row(row)

    # Human message
    header = f"📅 Daily Business Summary — {today_str()} • {row['time']}\n"
    kpis = (
        f"\n💰 Sales: ₹{sales['total_sales']:,} ({'—' if d_sales is None else ('+' if d_sales>=0 else '')}{'' if d_sales is None else d_sales}% vs yday)"
        f"\n🧾 Orders: {sales['orders']} | Avg Order: ₹{sales['avg_order']:,}"
        f"\n🧑‍💼 Leads: {leads['leads_count']} ({'—' if d_leads is None else ('+' if d_leads>=0 else '')}{'' if d_leads is None else d_leads}%)"
        f"\n🏢 Attendance: {att['rate']}% ({'—' if d_att is None else ('+' if d_att>=0 else '')}{'' if d_att is None else d_att}%) | Absents: {att['absent']}"
    )
    insights = (
        "\n\n🧠 **Insights**"
        f"\n• {s_line}"
        f"\n• {l_line}"
        f"\n• {a_line}"
        f"\n— updates every {UPDATE_SEC//60 if UPDATE_SEC>=60 else UPDATE_SEC} "
        f"{'min' if UPDATE_SEC>=60 else 'sec'}"
    )
    message = header + kpis + insights

    return message

async def send_telegram(message: str):
    await client.send_message(DEST_CHAT, message)

def main_loop():
    logging.info("Business Orchestrator started.")
    with client:
        while True:
            try:
                msg = run_once()
                client.loop.run_until_complete(send_telegram(msg))
                logging.info("Cycle success.")
            except Exception as e:
                logging.error(f"Cycle error: {e}")
            time.sleep(UPDATE_SEC)

if __name__ == "__main__":
    main_loop()
