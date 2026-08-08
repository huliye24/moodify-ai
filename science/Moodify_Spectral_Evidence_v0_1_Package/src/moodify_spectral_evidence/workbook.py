"""Dependency-free, deterministic XLSX research view for spectral evidence."""
from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Sequence
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from .analyzer import AnalysisParams, BandMetrics, CaseSpec, TrackMetrics


def _column_name(index: int) -> str:
    result = ""
    while index:
        index, remainder = divmod(index - 1, 26)
        result = chr(65 + remainder) + result
    return result


def _cell(ref: str, value: object, style: int = 0) -> str:
    style_attr = f' s="{style}"' if style else ""
    if value is None:
        return f'<c r="{ref}"{style_attr}/>'
    if isinstance(value, bool):
        return f'<c r="{ref}" t="b"{style_attr}><v>{1 if value else 0}</v></c>'
    if isinstance(value, (int, float)):
        return f'<c r="{ref}"{style_attr}><v>{value}</v></c>'
    text = escape(str(value))
    return f'<c r="{ref}" t="inlineStr"{style_attr}><is><t xml:space="preserve">{text}</t></is></c>'


def _sheet_xml(rows: list[list[object]], widths: Sequence[float] | None = None) -> str:
    max_cols = max((len(row) for row in rows), default=1)
    max_rows = max(len(rows), 1)
    cols = widths or [18.0] * max_cols
    cols_xml = "".join(
        f'<col min="{i}" max="{i}" width="{width}" customWidth="1"/>'
        for i, width in enumerate(cols, 1)
    )
    row_xml = []
    for row_index, row in enumerate(rows, 1):
        cells = []
        for column_index, value in enumerate(row, 1):
            style = 2 if row_index == 1 else (1 if row_index == 2 else (3 if isinstance(value, float) else 0))
            cells.append(_cell(f"{_column_name(column_index)}{row_index}", value, style))
        row_xml.append(f'<row r="{row_index}">{"".join(cells)}</row>')
    dimension = f"A1:{_column_name(max_cols)}{max_rows}"
    auto_filter = f'<autoFilter ref="A2:{_column_name(max_cols)}{max_rows}"/>' if max_rows >= 2 else ""
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f'<dimension ref="{dimension}"/><sheetViews><sheetView workbookViewId="0" showGridLines="0">'
        '<pane ySplit="2" topLeftCell="A3" activePane="bottomLeft" state="frozen"/>'
        '</sheetView></sheetViews><sheetFormatPr defaultRowHeight="18"/>'
        f'<cols>{cols_xml}</cols><sheetData>{"".join(row_xml)}</sheetData>{auto_filter}</worksheet>'
    )


def _zip_write(archive: ZipFile, name: str, content: str) -> None:
    info = ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = ZIP_DEFLATED
    archive.writestr(info, content.encode("utf-8"))


def write_research_workbook(
    output_path: Path,
    spec: CaseSpec,
    params: AnalysisParams,
    metrics: list[TrackMetrics],
    bands: list[BandMetrics],
) -> None:
    """Write an auditable human research view; JSON/CSV remain the fact layer."""
    readme: list[list[object]] = [
        ["Moodify Spectral Evidence", "Value"],
        ["Case ID", spec.case_id],
        ["Title", spec.title],
        ["Generator", "moodify_spectral_evidence v0.1"],
        ["Difference", "after - before; positive means measured energy increased, not better"],
        ["Fact layer", "case_summary.json, track_summary.csv, band_comparison.csv"],
        ["Human authority", "Human_Review is intentionally blank until an authorized person enters it"],
        ["Analysis parameters", str(asdict(params))],
        ["Parquet", "NOT_AVAILABLE: pyarrow is not installed; no dependency was added"],
    ]
    track_headers: list[object] = [
        "Track summary", "role", "before_hash", "after_hash", "before_sr", "after_sr",
        "channels", "duration_s", "before_peak_db", "after_peak_db", "before_rms_db",
        "after_rms_db", "rms_delta_db", "warnings", "errors", "asset_directory",
    ]
    track_rows: list[list[object]] = [["Track Summary"], track_headers]
    for item in metrics:
        track_rows.append([
            item.track_id, item.role, item.before_hash, item.after_hash,
            item.before_original_sample_rate, item.after_original_sample_rate,
            item.before_channels, item.before_duration_s, item.before_peak_db,
            item.after_peak_db, item.before_rms_db, item.after_rms_db, item.rms_delta_db,
            "; ".join(item.warnings), "; ".join(item.errors), f"assets/{item.track_id}/",
        ])
    band_headers: list[object] = [
        "Band comparison", "band", "frequency_hz", "before_energy_db",
        "after_energy_db", "delta_db",
    ]
    band_rows: list[list[object]] = [["Band Comparison"], band_headers]
    band_rows.extend([
        [item.track_id, item.band, item.freq_range_hz, item.before_energy_db,
         item.after_energy_db, item.delta_db]
        for item in bands
    ])
    empty_sheets: dict[str, list[list[object]]] = {
        "Time_Sections": [["Time Sections"], ["track_id", "start_s", "end_s", "status", "reason"],
                          ["full_mix", None, None, "NOT_PROVIDED", "No section contract in case spec"]],
        "Decision_Log": [["Decision Log"], ["track_id", "action", "parameter_reference", "operator", "status"],
                         ["full_mix", None, None, None, "NOT_PROVIDED"]],
        "Human_Review": [["Human Review"], ["track_id", "reviewer", "decision", "reason", "reviewed_at"],
                         ["full_mix", None, None, None, None]],
    }
    quality_rows: list[list[object]] = [["Data Quality"], ["track_id", "severity", "message", "actions"]]
    for item in metrics:
        if not item.warnings and not item.errors:
            quality_rows.append([item.track_id, "PASS", "No findings", "; ".join(item.analysis_actions)])
        for message in item.warnings:
            quality_rows.append([item.track_id, "WARNING", message, "; ".join(item.analysis_actions)])
        for message in item.errors:
            quality_rows.append([item.track_id, "ERROR", message, "; ".join(item.analysis_actions)])

    sheets: list[tuple[str, list[list[object]], list[float]]] = [
        ("README", readme, [28, 100]),
        ("Track_Summary", track_rows, [22, 14, 68, 68, 12, 12, 10, 12, 14, 14, 14, 14, 14, 30, 30, 30]),
        ("Band_Comparison", band_rows, [22, 16, 18, 20, 20, 16]),
        ("Time_Sections", empty_sheets["Time_Sections"], [22, 12, 12, 18, 45]),
        ("Decision_Log", empty_sheets["Decision_Log"], [22, 25, 30, 20, 18]),
        ("Human_Review", empty_sheets["Human_Review"], [22, 22, 20, 50, 22]),
        ("Data_Quality", quality_rows, [22, 16, 60, 60]),
    ]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    content_types = ''.join(
        f'<Override PartName="/xl/worksheets/sheet{i}.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        for i in range(1, len(sheets) + 1)
    )
    workbook_sheets = ''.join(
        f'<sheet name="{escape(name)}" sheetId="{i}" r:id="rId{i}"/>'
        for i, (name, _, _) in enumerate(sheets, 1)
    )
    workbook_rels = ''.join(
        f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{i}.xml"/>'
        for i in range(1, len(sheets) + 1)
    )
    workbook_rels += (
        f'<Relationship Id="rId{len(sheets) + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
    )
    styles = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        '<fonts count="3"><font><sz val="10"/><name val="Aptos"/></font>'
        '<font><b/><color rgb="FFFFFFFF"/><sz val="10"/><name val="Aptos"/></font>'
        '<font><b/><sz val="14"/><color rgb="FF17365D"/><name val="Aptos Display"/></font></fonts>'
        '<fills count="3"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill>'
        '<fill><patternFill patternType="solid"><fgColor rgb="FF1F4E78"/><bgColor indexed="64"/></patternFill></fill></fills>'
        '<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>'
        '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
        '<cellXfs count="4"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>'
        '<xf numFmtId="0" fontId="1" fillId="2" borderId="0" xfId="0" applyFont="1" applyFill="1"/>'
        '<xf numFmtId="0" fontId="2" fillId="0" borderId="0" xfId="0" applyFont="1"/>'
        '<xf numFmtId="2" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1"/></cellXfs>'
        '<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles></styleSheet>'
    )
    with ZipFile(output_path, "w") as archive:
        _zip_write(archive, "[Content_Types].xml", '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                   '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                   '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                   '<Default Extension="xml" ContentType="application/xml"/>'
                   '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
                   '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
                   f'{content_types}</Types>')
        _zip_write(archive, "_rels/.rels", '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                   '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
                   '</Relationships>')
        _zip_write(archive, "xl/workbook.xml", '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                   '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
                   f'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>{workbook_sheets}</sheets></workbook>')
        _zip_write(archive, "xl/_rels/workbook.xml.rels", '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                   f'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">{workbook_rels}</Relationships>')
        _zip_write(archive, "xl/styles.xml", styles)
        for index, (_, rows, widths) in enumerate(sheets, 1):
            _zip_write(archive, f"xl/worksheets/sheet{index}.xml", _sheet_xml(rows, widths))
