"""Overtime table export service."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from io import BytesIO
import logging
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfgen import canvas
from sqlalchemy.orm import Session

from ..models import OvertimeWeek, Staff, Department, DepartmentOperation

logger = logging.getLogger(__name__)

STATUS_INTERNAL = "bg-2"
STATUS_TRIP = "bg-3"
DEFAULT_FONT_NAME = "STSong-Light"
NAME_FONT_SIZES = (14, 13, 12, 11, 10)
REMARK_FONT_SIZE = 12
TITLE_FONT_SIZE = 20
TITLE_TEXT_CENTER_X = 350
TITLE_TEXT_BASELINE_Y = 33
PAGE_BORDER_LEFT = 2
PAGE_BORDER_RIGHT = 702
PAGE_TOP = 57
PAGE_BOTTOM = 1089
NAME_COLUMN_LEFT = 76
NAME_COLUMN_RIGHT = 457
REMARK_COLUMN_LEFT = 635
ROW_PADDING_X = 6
ROW_PADDING_Y = 6
TITLE_CLEAR_BOX = (100, 8, 600, 54)
FOOTER_VALUE_CLEAR_BOX = (2, 1051, 702, 1088)

DAY_TOKEN_BY_WEEKDAY = {
    0: "mon",
    1: "tue",
    2: "wed",
    3: "thu",
    4: "fri",
    5: "sat",
    6: "sun",
}


@dataclass(frozen=True)
class NameRun:
    """A rendered staff name unit and its style."""

    text: str
    underlined: bool


@dataclass(frozen=True)
class TemplateRow:
    """Template row coordinates (image-space, top-left origin)."""

    template_name: str
    department_id: Optional[int]
    row_top: int
    row_bottom: int


@dataclass(frozen=True)
class DepartmentExportRow:
    """Per-department export model used by the renderer."""

    template_name: str
    department_id: Optional[int]
    row_top: int
    row_bottom: int
    name_runs: List[NameRun]
    remark_count: Optional[int]


TEMPLATE_ROWS: Tuple[TemplateRow, ...] = (
    TemplateRow("制造部", 1, 96, 236),
    TemplateRow("仓库", None, 236, 311),
    TemplateRow("装配部", 4, 311, 425),
    TemplateRow("品质部", 2, 425, 501),
    TemplateRow("采购部", None, 501, 577),
    TemplateRow("技术部", 6, 577, 653),
    TemplateRow("电气部", 5, 653, 729),
    TemplateRow("工艺部", 3, 729, 797),
    TemplateRow("管理部", None, 797, 865),
    TemplateRow("业务部", 8, 865, 933),
    TemplateRow("机加技术部", 7, 933, 1013),
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_IMAGE_PATH = PROJECT_ROOT / "format.jpg"


class OvertimeTableExportService:
    """Build overtime export model and render template-based PDF output."""

    def __init__(self, db: Session):
        self.db = db

    def build_department_rows(self, export_date: date) -> List[DepartmentExportRow]:
        """Assemble per-row export data for the requested date."""
        weekday_token = DAY_TOKEN_BY_WEEKDAY[export_date.weekday()]
        status_column = getattr(OvertimeWeek, weekday_token)
        
        # 1. 获取当天有操作记录的部门
        active_department_names = {
            row.department_name
            for row in self.db.query(DepartmentOperation.department_name)
            .filter(DepartmentOperation.date == export_date)
            .all()
        }
        
        # 获取所有部门 ID 到名称的映射
        dept_id_to_name = {
            d.id: d.name 
            for d in self.db.query(Department.id, Department.name).all()
        }

        raw_rows = (
            self.db.query(
                Staff.id.label("staff_id"),
                Staff.name.label("staff_name"),
                Staff.department_id.label("department_id"),
                status_column.label("status"),
            )
            .outerjoin(OvertimeWeek, OvertimeWeek.staff_id == Staff.id)
            .order_by(Staff.department_id.asc(), Staff.name.asc(), Staff.id.asc())
            .all()
        )

        grouped: Dict[int, Dict[str, List[str]]] = {
            row.department_id: {STATUS_INTERNAL: [], STATUS_TRIP: []}
            for row in TEMPLATE_ROWS
            if row.department_id is not None
        }

        for raw in raw_rows:
            department_id = raw.department_id
            if department_id not in grouped:
                continue
            
            # 过滤逻辑：如果该部门今天没有操作记录，则不采集其加班人员
            dept_name = dept_id_to_name.get(department_id)
            if dept_name not in active_department_names:
                continue

            status = raw.status or "bg-1"
            if status in (STATUS_INTERNAL, STATUS_TRIP):
                grouped[department_id][status].append(raw.staff_name)

        rows: List[DepartmentExportRow] = []
        for template_row in TEMPLATE_ROWS:
            if template_row.department_id is None:
                rows.append(
                    DepartmentExportRow(
                        template_name=template_row.template_name,
                        department_id=None,
                        row_top=template_row.row_top,
                        row_bottom=template_row.row_bottom,
                        name_runs=[],
                        remark_count=None,
                    )
                )
                continue

            names_by_status = grouped[template_row.department_id]
            name_runs = [NameRun(name, underlined=False) for name in names_by_status[STATUS_INTERNAL]] + [
                NameRun(name, underlined=True) for name in names_by_status[STATUS_TRIP]
            ]
            
            # 只有当活跃部门名单不为空时，才更新 remark_count
            rows.append(
                DepartmentExportRow(
                    template_name=template_row.template_name,
                    department_id=template_row.department_id,
                    row_top=template_row.row_top,
                    row_bottom=template_row.row_bottom,
                    name_runs=name_runs,
                    remark_count=len(names_by_status[STATUS_INTERNAL]) if name_runs else 0,
                )
            )

        return rows

    def render_pdf(self, export_date: date, rows: Sequence[DepartmentExportRow]) -> bytes:
        """Render a PDF document from the template image and export rows."""
        page_width, page_height = self._load_template_size()
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=(page_width, page_height))
        self._register_font()

        image = ImageReader(str(TEMPLATE_IMAGE_PATH))
        pdf.drawImage(image, 0, 0, width=page_width, height=page_height)

        self._clear_rect(pdf, page_height, *TITLE_CLEAR_BOX)
        self._clear_rect(pdf, page_height, *FOOTER_VALUE_CLEAR_BOX)

        for row in rows:
            self._clear_rect(
                pdf,
                page_height,
                NAME_COLUMN_LEFT + 1,
                row.row_top + 1,
                NAME_COLUMN_RIGHT - 1,
                row.row_bottom - 1,
            )
            self._clear_rect(
                pdf,
                page_height,
                REMARK_COLUMN_LEFT + 1,
                row.row_top + 1,
                PAGE_BORDER_RIGHT - 1,
                row.row_bottom - 1,
            )

        self._draw_title(pdf, page_height, export_date)

        for row in rows:
            if row.department_id is None:
                continue
            self._draw_department_names(pdf, page_height, export_date, row)
            self._draw_remark_count(pdf, page_height, row)

        pdf.showPage()
        pdf.save()
        return buffer.getvalue()

    def build_pdf(self, export_date: date) -> bytes:
        """Build and render export PDF for the requested date."""
        rows = self.build_department_rows(export_date)
        return self.render_pdf(export_date, rows)

    def _load_template_size(self) -> Tuple[int, int]:
        if not TEMPLATE_IMAGE_PATH.exists():
            raise FileNotFoundError(f"Template image not found: {TEMPLATE_IMAGE_PATH}")
        image = ImageReader(str(TEMPLATE_IMAGE_PATH))
        width, height = image.getSize()
        return int(width), int(height)

    def _register_font(self) -> None:
        if DEFAULT_FONT_NAME in pdfmetrics.getRegisteredFontNames():
            return
        pdfmetrics.registerFont(UnicodeCIDFont(DEFAULT_FONT_NAME))

    def _draw_title(self, pdf: canvas.Canvas, page_height: int, export_date: date) -> None:
        title = f"{self._to_cn_date(export_date)}  上班人员统计表"
        pdf.setFillColor(colors.black)
        pdf.setFont(DEFAULT_FONT_NAME, TITLE_FONT_SIZE)
        pdf.drawCentredString(
            TITLE_TEXT_CENTER_X,
            self._to_pdf_y(page_height, TITLE_TEXT_BASELINE_Y),
            title,
        )

    def _draw_department_names(
        self,
        pdf: canvas.Canvas,
        page_height: int,
        export_date: date,
        row: DepartmentExportRow,
    ) -> None:
        if not row.name_runs:
            return

        box_left = NAME_COLUMN_LEFT + ROW_PADDING_X
        box_right = NAME_COLUMN_RIGHT - ROW_PADDING_X
        box_top = row.row_top + ROW_PADDING_Y
        box_bottom = row.row_bottom - ROW_PADDING_Y
        box_width = max(1.0, float(box_right - box_left))
        box_height = max(1.0, float(box_bottom - box_top))

        selected_font_size = NAME_FONT_SIZES[-1]
        selected_lines: List[List[Tuple[str, bool, float]]] = []
        overflowed = False

        for font_size in NAME_FONT_SIZES:
            lines, overflow = self._layout_name_runs(
                row.name_runs,
                font_size,
                box_width,
                box_height,
                truncate=False,
            )
            if not overflow:
                selected_font_size = font_size
                selected_lines = lines
                overflowed = False
                break
            selected_font_size = font_size
            selected_lines = lines
            overflowed = True

        if overflowed:
            selected_lines, _ = self._layout_name_runs(
                row.name_runs,
                selected_font_size,
                box_width,
                box_height,
                truncate=True,
            )
            logger.warning(
                "Export names overflow for department '%s' (%s) on %s",
                row.template_name,
                row.department_id,
                export_date.isoformat(),
            )

        line_height = selected_font_size + 3
        baseline_y = self._to_pdf_y(page_height, box_top + selected_font_size)
        pdf.setFillColor(colors.black)
        pdf.setStrokeColor(colors.black)
        pdf.setFont(DEFAULT_FONT_NAME, selected_font_size)

        for line in selected_lines:
            cursor_x = float(box_left)
            for text, underlined, text_width in line:
                pdf.drawString(cursor_x, baseline_y, text)
                if underlined and text.strip():
                    underline_y = baseline_y - 1.5
                    pdf.line(cursor_x, underline_y, cursor_x + text_width, underline_y)
                cursor_x += text_width
            baseline_y -= line_height

    def _draw_remark_count(
        self,
        pdf: canvas.Canvas,
        page_height: int,
        row: DepartmentExportRow,
    ) -> None:
        if row.remark_count is None:
            return
        center_x = (REMARK_COLUMN_LEFT + PAGE_BORDER_RIGHT) / 2
        center_y = (row.row_top + row.row_bottom) / 2
        pdf.setFillColor(colors.black)
        pdf.setFont(DEFAULT_FONT_NAME, REMARK_FONT_SIZE)
        pdf.drawCentredString(
            center_x,
            self._to_pdf_y(page_height, center_y) - 5,
            str(row.remark_count),
        )

    def _layout_name_runs(
        self,
        name_runs: Sequence[NameRun],
        font_size: int,
        box_width: float,
        box_height: float,
        truncate: bool,
    ) -> Tuple[List[List[Tuple[str, bool, float]]], bool]:
        line_height = font_size + 3
        max_lines = max(1, int(box_height // line_height))
        segments = self._split_runs(name_runs, font_size, box_width)

        lines: List[List[Tuple[str, bool, float]]] = []
        current_line: List[Tuple[str, bool, float]] = []
        current_width = 0.0

        for text, underlined, width in segments:
            if current_line and current_width + width > box_width:
                lines.append(current_line)
                current_line = []
                current_width = 0.0
            current_line.append((text, underlined, width))
            current_width += width

        if current_line:
            lines.append(current_line)

        overflow = len(lines) > max_lines
        if not overflow:
            return lines, False

        if not truncate:
            return lines[:max_lines], True

        truncated = lines[:max_lines]
        if not truncated:
            return [], True

        ellipsis_width = pdfmetrics.stringWidth("...", DEFAULT_FONT_NAME, font_size)
        last_line = truncated[-1]
        line_width = sum(width for _, _, width in last_line)

        while last_line and line_width + ellipsis_width > box_width:
            text, underlined, width = last_line[-1]
            if len(text) <= 1:
                last_line.pop()
                line_width -= width
                continue
            trimmed_text = text[:-1]
            trimmed_width = pdfmetrics.stringWidth(
                trimmed_text,
                DEFAULT_FONT_NAME,
                font_size,
            )
            last_line[-1] = (trimmed_text, underlined, trimmed_width)
            line_width = line_width - width + trimmed_width

        last_line.append(("...", False, ellipsis_width))
        return truncated, True

    def _split_runs(
        self,
        name_runs: Sequence[NameRun],
        font_size: int,
        box_width: float,
    ) -> List[Tuple[str, bool, float]]:
        split_segments: List[Tuple[str, bool, float]] = []
        for index, run in enumerate(name_runs):
            text = run.text
            if index < len(name_runs) - 1:
                text = f"{text}、"

            split_segments.extend(
                self._split_text_segment(text, run.underlined, font_size, box_width)
            )
        return split_segments

    def _split_text_segment(
        self,
        text: str,
        underlined: bool,
        font_size: int,
        box_width: float,
    ) -> List[Tuple[str, bool, float]]:
        width = pdfmetrics.stringWidth(text, DEFAULT_FONT_NAME, font_size)
        if width <= box_width:
            return [(text, underlined, width)]

        segments: List[Tuple[str, bool, float]] = []
        cursor = ""
        for char in text:
            candidate = f"{cursor}{char}"
            candidate_width = pdfmetrics.stringWidth(
                candidate,
                DEFAULT_FONT_NAME,
                font_size,
            )
            if candidate_width <= box_width:
                cursor = candidate
                continue

            if cursor:
                cursor_width = pdfmetrics.stringWidth(
                    cursor,
                    DEFAULT_FONT_NAME,
                    font_size,
                )
                segments.append((cursor, underlined, cursor_width))
            cursor = char

        if cursor:
            cursor_width = pdfmetrics.stringWidth(cursor, DEFAULT_FONT_NAME, font_size)
            segments.append((cursor, underlined, cursor_width))

        return segments

    def _clear_rect(
        self,
        pdf: canvas.Canvas,
        page_height: int,
        left: int,
        top: int,
        right: int,
        bottom: int,
    ) -> None:
        width = max(0, right - left)
        height = max(0, bottom - top)
        if width == 0 or height == 0:
            return
        pdf.setFillColor(colors.white)
        pdf.rect(
            left,
            self._to_pdf_y(page_height, bottom),
            width,
            height,
            fill=1,
            stroke=0,
        )

    def _to_pdf_y(self, page_height: int, image_y: float) -> float:
        return float(page_height) - float(image_y)

    def _to_cn_date(self, export_date: date) -> str:
        return f"{export_date.year}年{export_date.month}月{export_date.day}日"
