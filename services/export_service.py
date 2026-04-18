"""
Financial Report Export Service (FR-BO-23)
Generates PDF or CSV financial reports for a Business Owner.
"""

import io
import csv
from datetime import datetime


def get_transactions(cursor, bo_user_id: str, from_date: str = None, to_date: str = None,
                     tx_type: str = None) -> list:
    """Fetch transactions for a BO with optional filters."""
    sql = """
        SELECT Id, Type, Amount, BalanceAfter, StripePaymentIntentId, CreatedAt
        FROM Transactions
        WHERE BusinessOwnerId = ?
    """
    params = [bo_user_id]

    if from_date:
        sql += " AND CreatedAt >= ?"
        params.append(from_date)
    if to_date:
        sql += " AND CreatedAt <= ?"
        params.append(to_date + " 23:59:59")
    if tx_type:
        sql += " AND Type = ?"
        params.append(tx_type)

    sql += " ORDER BY CreatedAt DESC"
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    return [
        {
            "id": r[0],
            "type": r[1],
            "amount": float(r[2] or 0),
            "balance_after": float(r[3] or 0),
            "stripe_id": r[4] or "",
            "created_at": r[5].strftime("%Y-%m-%d %H:%M") if r[5] else "",
        }
        for r in rows
    ]


def compute_summary(transactions: list) -> dict:
    """Compute revenue, expenses, net profit from transactions."""
    revenue = sum(t["amount"] for t in transactions if t["amount"] > 0 and t["type"] == "Sale")
    expenses = abs(sum(t["amount"] for t in transactions if t["amount"] < 0))
    refunds = abs(sum(t["amount"] for t in transactions if t["type"] == "Refund"))
    fees = abs(sum(t["amount"] for t in transactions if t["type"] == "Fee"))
    net_profit = revenue - expenses
    return {
        "total_revenue": round(revenue, 2),
        "total_expenses": round(expenses, 2),
        "total_refunds": round(refunds, 2),
        "total_fees": round(fees, 2),
        "net_profit": round(net_profit, 2),
        "transaction_count": len(transactions),
    }


def export_csv(transactions: list, summary: dict) -> bytes:
    """Return CSV file as bytes — clean CRLF line endings for Excel."""
    output = io.StringIO(newline="")  # prevent double \r\n on Windows
    writer = csv.writer(output, lineterminator="\r\n")

    # Summary section
    writer.writerow(["=== FINANCIAL REPORT SUMMARY ==="])
    writer.writerow(["Total Revenue (EGP)", summary["total_revenue"]])
    writer.writerow(["Total Expenses (EGP)", summary["total_expenses"]])
    writer.writerow(["Total Refunds (EGP)", summary["total_refunds"]])
    writer.writerow(["Total Fees (EGP)", summary["total_fees"]])
    writer.writerow(["Net Profit (EGP)", summary["net_profit"]])
    writer.writerow(["Transaction Count", summary["transaction_count"]])
    writer.writerow([])

    # Transactions
    writer.writerow(["ID", "Type", "Amount (EGP)", "Balance After", "Stripe ID", "Date"])
    for t in transactions:
        writer.writerow([
            t["id"], t["type"], t["amount"],
            t["balance_after"], t["stripe_id"], t["created_at"]
        ])

    # BOM prefix for Excel UTF-8 compatibility
    return b"\xef\xbb\xbf" + output.getvalue().encode("utf-8")


def export_pdf(transactions: list, summary: dict, bo_user_id: str) -> bytes:
    """Return PDF file as bytes using reportlab."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    except ImportError:
        # Fallback to CSV if reportlab not installed
        return export_csv(transactions, summary)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    title_style = ParagraphStyle("Title", parent=styles["Heading1"],
                                  fontSize=18, textColor=colors.HexColor("#2C3E50"))
    elements.append(Paragraph("Talentree — Financial Report", title_style))
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles["Normal"]))
    elements.append(Spacer(1, 0.5*cm))

    # Summary table
    summary_data = [
        ["Metric", "Amount (EGP)"],
        ["Total Revenue", f"{summary['total_revenue']:,.2f}"],
        ["Total Expenses", f"{summary['total_expenses']:,.2f}"],
        ["Total Refunds", f"{summary['total_refunds']:,.2f}"],
        ["Total Fees", f"{summary['total_fees']:,.2f}"],
        ["Net Profit", f"{summary['net_profit']:,.2f}"],
        ["Transactions", str(summary['transaction_count'])],
    ]
    summary_table = Table(summary_data, colWidths=[8*cm, 6*cm])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2C3E50")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#27AE60")),
        ("TEXTCOLOR", (0, -1), (-1, -1), colors.white),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#ECF0F1")]),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 0.8*cm))

    # Transactions table (limited to first 100 to keep PDF manageable)
    elements.append(Paragraph("Transactions", styles["Heading2"]))
    tx_data = [["ID", "Type", "Amount (EGP)", "Date"]]
    for t in transactions[:100]:
        tx_data.append([
            str(t["id"]), t["type"],
            f"{t['amount']:,.2f}", t["created_at"]
        ])
    tx_table = Table(tx_data, colWidths=[2*cm, 4*cm, 5*cm, 6*cm])
    tx_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#34495E")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 1), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8F9FA")]),
    ]))
    elements.append(tx_table)

    if len(transactions) > 100:
        elements.append(Spacer(1, 0.3*cm))
        elements.append(Paragraph(
            f"* Showing 100 of {len(transactions)} transactions. Export as CSV for full data.",
            styles["Normal"]
        ))

    doc.build(elements)
    return buffer.getvalue()
