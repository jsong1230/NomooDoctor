# 급여명세서 PDF 생성 서비스 (근로기준법 제48조 법정 기재사항)
import io
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)


def _try_register_korean_font() -> str | None:
    """
    시스템에 설치된 한글 폰트를 등록하고 폰트 이름을 반환합니다.
    폰트 등록 실패 시 None을 반환합니다.
    """
    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        import os

        # 운영체제별 한글 폰트 후보 경로 목록
        candidate_fonts: list[tuple[str, str]] = [
            # macOS
            ("NanumGothic", "/Library/Fonts/NanumGothic.ttf"),
            ("AppleGothic", "/System/Library/Fonts/AppleGothic.ttf"),
            ("AppleSDGothicNeo", "/System/Library/Fonts/AppleSDGothicNeo.ttc"),
            # Linux (Ubuntu/Debian)
            ("NanumGothic", "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"),
            ("UnDotum", "/usr/share/fonts/truetype/unfonts-core/UnDotum.ttf"),
            ("NotoSansCJK", "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
            # Windows
            ("Malgun", "C:/Windows/Fonts/malgun.ttf"),
            ("Gulim", "C:/Windows/Fonts/gulim.ttc"),
        ]

        for font_name, font_path in candidate_fonts:
            if not os.path.exists(font_path):
                continue
            try:
                pdfmetrics.registerFont(TTFont(font_name, font_path))
                logger.info(f"한글 폰트 등록 성공: {font_name} ({font_path})")
                return font_name
            except Exception as font_exc:
                # PostScript 기반 TTC 등 지원되지 않는 포맷은 건너뜀
                logger.debug(f"폰트 로드 실패, 다음 후보 시도: {font_path} - {font_exc}")
                continue

        logger.warning("시스템에서 한글 폰트를 찾을 수 없습니다. 기본 폰트를 사용합니다.")
        return None

    except Exception as exc:
        logger.warning(f"한글 폰트 등록 실패, 기본 폰트 사용: {exc}")
        return None


def _fmt_amount(value: Decimal | int | float | None) -> str:
    """금액을 천 단위 구분 콤마 형식으로 포맷합니다."""
    if value is None:
        return "0"
    return f"{int(value):,}"


class PayslipPDFService:
    """급여명세서 PDF 생성 서비스"""

    @staticmethod
    def generate(payslip_data: dict) -> bytes:
        """
        급여명세서 PDF를 생성하여 bytes로 반환합니다.

        Args:
            payslip_data: _to_response 반환값과 동일한 구조의 dict

        Returns:
            생성된 PDF bytes
        """
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import mm
        from reportlab.platypus import (
            SimpleDocTemplate,
            Table,
            TableStyle,
            Paragraph,
            Spacer,
        )

        buffer = io.BytesIO()

        # 한글 폰트 등록 시도
        korean_font = _try_register_korean_font()
        # 한글 폰트가 없으면 기본 내장 폰트 사용 (한글 출력 불가이나 레이아웃 유지)
        font_name = korean_font if korean_font else "Helvetica"
        font_name_bold = (korean_font if korean_font else "Helvetica-Bold")

        # 문서 마진 설정 (A4)
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=15 * mm,
            leftMargin=15 * mm,
            topMargin=15 * mm,
            bottomMargin=15 * mm,
        )

        # 스타일 정의
        styles = getSampleStyleSheet()
        style_title = ParagraphStyle(
            "PayslipTitle",
            parent=styles["Title"],
            fontName=font_name_bold,
            fontSize=18,
            spaceAfter=6,
            alignment=1,  # 가운데 정렬
        )
        style_subtitle = ParagraphStyle(
            "PayslipSubtitle",
            parent=styles["Normal"],
            fontName=font_name,
            fontSize=10,
            spaceAfter=4,
            alignment=1,
        )
        style_section = ParagraphStyle(
            "SectionHeader",
            parent=styles["Normal"],
            fontName=font_name_bold,
            fontSize=10,
            spaceBefore=8,
            spaceAfter=3,
            textColor=colors.HexColor("#1a1a2e"),
        )
        style_footer = ParagraphStyle(
            "Footer",
            parent=styles["Normal"],
            fontName=font_name,
            fontSize=8,
            alignment=1,
            textColor=colors.grey,
        )

        # 공통 테이블 스타일 기반
        base_table_style = [
            ("FONTNAME", (0, 0), (-1, -1), font_name),
            ("FONTNAME", (0, 0), (-1, 0), font_name_bold),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2d6a4f")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("ALIGN", (1, 1), (1, -1), "RIGHT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f9f7")]),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (0, -1), 8),
            ("RIGHTPADDING", (-1, 0), (-1, -1), 8),
        ]

        # ── 급여 데이터 추출 ──
        employee_name: str = payslip_data.get("employee_name", "")
        company_name: str = payslip_data.get("company_name", "")
        year: int = payslip_data.get("year", 0)
        month: int = payslip_data.get("month", 0)

        # 지급 항목
        base_salary = payslip_data.get("base_salary", Decimal("0"))
        weekly_allowance = payslip_data.get("weekly_allowance", Decimal("0"))
        overtime_pay = payslip_data.get("overtime_pay", Decimal("0"))
        night_pay = payslip_data.get("night_pay", Decimal("0"))
        holiday_pay = payslip_data.get("holiday_pay", Decimal("0"))
        meal_allowance = payslip_data.get("meal_allowance", Decimal("0"))
        transport_allowance = payslip_data.get("transport_allowance", Decimal("0"))
        total_payment = payslip_data.get("total_payment", Decimal("0"))

        # 공제 항목
        national_pension = payslip_data.get("national_pension", Decimal("0"))
        health_insurance = payslip_data.get("health_insurance", Decimal("0"))
        long_term_care = payslip_data.get("long_term_care", Decimal("0"))
        employment_insurance = payslip_data.get("employment_insurance", Decimal("0"))
        income_tax = payslip_data.get("income_tax", Decimal("0"))
        local_income_tax = payslip_data.get("local_income_tax", Decimal("0"))
        total_deduction = payslip_data.get("total_deduction", Decimal("0"))

        # 실수령액
        net_salary = payslip_data.get("net_salary", Decimal("0"))

        # ── 문서 요소 조립 ──
        story: list = []

        # 1. 제목
        story.append(Paragraph("\uae09\uc5ec\uba85\uc138\uc11c", style_title))  # 급여명세서
        story.append(
            Paragraph(
                f"{year}\ub144 {month}\uc6d4 | {company_name}",  # {year}년 {month}월 | {company_name}
                style_subtitle,
            )
        )
        story.append(Spacer(1, 4 * mm))

        # 2. 기본 정보 테이블 (사업장명 / 근로자 / 급여기간)
        info_table_data = [
            [
                "\uc0ac\uc5c5\uc7a5\uba85",  # 사업장명
                "\uadfc\ub85c\uc790",         # 근로자
                "\uae09\uc5ec \uae30\uac04",  # 급여 기간
            ],
            [
                company_name,
                employee_name,
                f"{year}\ub144 {month:02d}\uc6d4",  # {year}년 {month:02d}월
            ],
        ]
        page_width = A4[0] - 30 * mm
        info_table = Table(
            info_table_data,
            colWidths=[page_width / 3] * 3,
        )
        info_table.setStyle(
            TableStyle(
                base_table_style
                + [
                    ("FONTNAME", (0, 1), (-1, 1), font_name),
                    ("FONTSIZE", (0, 1), (-1, 1), 10),
                    ("ALIGN", (0, 1), (-1, 1), "CENTER"),
                ]
            )
        )
        story.append(info_table)
        story.append(Spacer(1, 5 * mm))

        # 3. 지급 항목 테이블
        story.append(Paragraph("\u25a0 \uc9c0\uae09 \ud56d\ubaa9", style_section))  # ■ 지급 항목
        payment_col_w = page_width / 2
        payment_data = [
            ["\ud56d\ubaa9", "\uae08\uc561 (\uc6d0)"],  # 항목, 금액 (원)
            ["\uae30\ubcf8\uae09", _fmt_amount(base_salary)],                      # 기본급
            ["\uc8fc\ud734\uc218\ub2f9", _fmt_amount(weekly_allowance)],          # 주휴수당
            ["\uc5f0\uc7a5\uc218\ub2f9", _fmt_amount(overtime_pay)],              # 연장수당
            ["\uc57c\uac04\uc218\ub2f9", _fmt_amount(night_pay)],                 # 야간수당
            ["\ud734\uc77c\uc218\ub2f9", _fmt_amount(holiday_pay)],               # 휴일수당
            ["\uc2dd\ub300", _fmt_amount(meal_allowance)],                        # 식대
            ["\uad50\ud1b5\ube44", _fmt_amount(transport_allowance)],             # 교통비
            ["\uc9c0\uae09 \ud569\uacc4", _fmt_amount(total_payment)],            # 지급 합계
        ]
        payment_table = Table(
            payment_data,
            colWidths=[payment_col_w, payment_col_w],
        )
        payment_style = TableStyle(
            base_table_style
            + [
                # 지급 합계 행 강조
                ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#1b4332")),
                ("TEXTCOLOR", (0, -1), (-1, -1), colors.white),
                ("FONTNAME", (0, -1), (-1, -1), font_name_bold),
                ("FONTSIZE", (0, -1), (-1, -1), 10),
            ]
        )
        payment_table.setStyle(payment_style)
        story.append(payment_table)
        story.append(Spacer(1, 5 * mm))

        # 4. 공제 항목 테이블
        story.append(Paragraph("\u25a0 \uacf5\uc81c \ud56d\ubaa9", style_section))  # ■ 공제 항목
        deduction_col_w = page_width / 2
        deduction_data = [
            ["\ud56d\ubaa9", "\uae08\uc561 (\uc6d0)"],  # 항목, 금액 (원)
            ["\uad6d\ubbfc\uc5f0\uae08", _fmt_amount(national_pension)],          # 국민연금
            ["\uac74\uac15\ubcf4\ud5d8", _fmt_amount(health_insurance)],          # 건강보험
            ["\uc7a5\uae30\uc694\uc591\ubcf4\ud5d8", _fmt_amount(long_term_care)],  # 장기요양보험
            ["\uace0\uc6a9\ubcf4\ud5d8", _fmt_amount(employment_insurance)],      # 고용보험
            ["\uc18c\ub4dd\uc138", _fmt_amount(income_tax)],                      # 소득세
            ["\uc9c0\ubc29\uc18c\ub4dd\uc138", _fmt_amount(local_income_tax)],    # 지방소득세
            ["\uacf5\uc81c \ud569\uacc4", _fmt_amount(total_deduction)],          # 공제 합계
        ]
        deduction_table = Table(
            deduction_data,
            colWidths=[deduction_col_w, deduction_col_w],
        )
        deduction_style = TableStyle(
            base_table_style
            + [
                # 공제 합계 행 강조
                ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#7b2d00")),
                ("TEXTCOLOR", (0, -1), (-1, -1), colors.white),
                ("FONTNAME", (0, -1), (-1, -1), font_name_bold),
                ("FONTSIZE", (0, -1), (-1, -1), 10),
            ]
        )
        deduction_table.setStyle(deduction_style)
        story.append(deduction_table)
        story.append(Spacer(1, 5 * mm))

        # 5. 실수령액 테이블
        net_col_w = page_width / 2
        net_data = [
            ["\uc2e4\uc218\ub839\uc561 (\uc6d0)", _fmt_amount(net_salary)],  # 실수령액 (원)
        ]
        net_table = Table(
            net_data,
            colWidths=[net_col_w, net_col_w],
        )
        net_table.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (-1, -1), font_name_bold),
                    ("FONTSIZE", (0, 0), (-1, -1), 13),
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#0d3b2e")),
                    ("TEXTCOLOR", (0, 0), (-1, -1), colors.white),
                    ("ALIGN", (0, 0), (0, 0), "CENTER"),
                    ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                    ("LEFTPADDING", (0, 0), (0, 0), 8),
                    ("RIGHTPADDING", (-1, 0), (-1, 0), 8),
                ]
            )
        )
        story.append(net_table)
        story.append(Spacer(1, 8 * mm))

        # 6. 법적 고지 문구
        story.append(
            Paragraph(
                # 본 명세서는 근로기준법 제48조에 의거하여 발급되었습니다.
                "\ubcf8 \uba85\uc138\uc11c\ub294 \uadfc\ub85c\uae30\uc900\ubc95 \uc81c48\uc870\uc5d0 \uc758\uac70\ud558\uc5ec \ubc1c\uae09\ub418\uc5c8\uc2b5\ub2c8\ub2e4.",
                style_footer,
            )
        )

        doc.build(story)

        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes
