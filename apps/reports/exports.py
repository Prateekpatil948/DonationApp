"""CSV / Excel / PDF export helpers shared by every report view."""

import csv
import io
from typing import Any

from django.http import HttpResponse
from django.template.loader import render_to_string

import openpyxl
from weasyprint import HTML


def export_csv(rows: list[dict[str, Any]], filename: str) -> HttpResponse:
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{filename}.csv"'

    writer = csv.writer(response)
    if rows:
        writer.writerow(rows[0].keys())
        for row in rows:
            writer.writerow(row.values())
    return response


def export_excel(rows: list[dict[str, Any]], filename: str) -> HttpResponse:
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = filename[:31]

    if rows:
        sheet.append(list(rows[0].keys()))
        for row in rows:
            sheet.append([str(value) for value in row.values()])

    buffer = io.BytesIO()
    workbook.save(buffer)
    buffer.seek(0)

    response = HttpResponse(
        buffer.read(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}.xlsx"'
    return response


def export_pdf(title: str, rows: list[dict[str, Any]], filename: str) -> HttpResponse:
    columns = list(rows[0].keys()) if rows else []
    html_string = render_to_string(
        "reports/report_table.html", {"title": title, "columns": columns, "rows": rows}
    )
    pdf_bytes = HTML(string=html_string).write_pdf()

    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}.pdf"'
    return response


def build_export_response(
    export_format: str | None, title: str, rows: list[dict[str, Any]], filename: str
) -> HttpResponse | None:
    """Returns an export ``HttpResponse`` for csv/excel/pdf, or ``None`` for the JSON path."""
    if export_format == "csv":
        return export_csv(rows, filename)
    if export_format == "excel":
        return export_excel(rows, filename)
    if export_format == "pdf":
        return export_pdf(title, rows, filename)
    return None
