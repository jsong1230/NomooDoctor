# 알림 발송 서비스 (이메일, 카카오 알림톡)
import asyncio
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """SMTP 이메일 발송 서비스"""

    @staticmethod
    def _is_smtp_configured() -> bool:
        """SMTP 설정이 완료되었는지 확인"""
        return bool(settings.SMTP_HOST and settings.SMTP_USER and settings.SMTP_PASSWORD)

    @staticmethod
    def _build_payslip_email(
        to_email: str,
        employee_name: str,
        company_name: str,
        year: int,
        month: int,
        pdf_content: bytes,
    ) -> MIMEMultipart:
        """급여명세서 이메일 메시지 구성"""
        msg = MIMEMultipart()
        msg["From"] = settings.SMTP_FROM
        msg["To"] = to_email
        msg["Subject"] = f"[{company_name}] {year}년 {month}월 급여명세서"

        # HTML 본문
        body_html = f"""
<html>
<body>
  <p>안녕하세요, {employee_name}님.</p>
  <p>{company_name}에서 {year}년 {month}월 급여명세서를 발송합니다.</p>
  <p>첨부된 PDF 파일을 확인해 주세요.</p>
  <br>
  <p>문의사항은 담당 관리자에게 연락해 주세요.</p>
</body>
</html>
"""
        msg.attach(MIMEText(body_html, "html", "utf-8"))

        # PDF 첨부
        attachment = MIMEBase("application", "pdf")
        attachment.set_payload(pdf_content)
        encoders.encode_base64(attachment)
        attachment.add_header(
            "Content-Disposition",
            f'attachment; filename="payslip_{year}_{month:02d}.pdf"',
        )
        msg.attach(attachment)

        return msg

    @staticmethod
    def _send_via_smtp(msg: MIMEMultipart, to_email: str) -> None:
        """SMTP를 통한 동기 이메일 발송 (asyncio.to_thread에서 호출)"""
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            if settings.SMTP_USE_TLS:
                server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_FROM, to_email, msg.as_string())

    @staticmethod
    async def send_payslip_email(
        to_email: str,
        employee_name: str,
        company_name: str,
        year: int,
        month: int,
        pdf_content: bytes,
    ) -> bool:
        """급여명세서 이메일 발송

        SMTP 설정이 없으면 mock 모드로 동작하여 True 반환.
        SMTP 설정이 있으면 실제 발송을 시도하고 실패 시 False 반환.

        Returns:
            True if sent (or mock mode), False on send failure
        """
        if not EmailService._is_smtp_configured():
            # mock 모드: 설정 미완료 시 로깅만 처리
            logger.info(
                "[MOCK] 이메일 발송: to=%s, employee=%s, company=%s, %d/%02d",
                to_email, employee_name, company_name, year, month,
            )
            return True

        try:
            msg = EmailService._build_payslip_email(
                to_email=to_email,
                employee_name=employee_name,
                company_name=company_name,
                year=year,
                month=month,
                pdf_content=pdf_content,
            )
            # 동기 SMTP 호출을 별도 스레드에서 실행 (이벤트 루프 차단 방지)
            await asyncio.to_thread(EmailService._send_via_smtp, msg, to_email)
            logger.info(
                "이메일 발송 완료: to=%s, employee=%s, %d/%02d",
                to_email, employee_name, year, month,
            )
            return True
        except smtplib.SMTPException as exc:
            logger.error(
                "이메일 발송 실패 (SMTP 오류): to=%s, error=%s", to_email, str(exc)
            )
            return False
        except OSError as exc:
            logger.error(
                "이메일 발송 실패 (네트워크 오류): to=%s, error=%s", to_email, str(exc)
            )
            return False


class KakaoAlimtalkService:
    """카카오 알림톡 발송 서비스 (인터페이스)"""

    @staticmethod
    def _is_kakao_configured() -> bool:
        """카카오 API 설정이 완료되었는지 확인"""
        return bool(settings.KAKAO_API_KEY and settings.KAKAO_SENDER_KEY)

    @staticmethod
    async def send_payslip_notification(
        phone_number: str,
        employee_name: str,
        company_name: str,
        year: int,
        month: int,
        net_salary: str,
    ) -> bool:
        """급여명세서 카카오 알림톡 발송

        Note: 카카오 비즈니스 API 키가 필요합니다.
        현재는 mock 구현이며, 실제 발송을 위해서는
        KAKAO_API_KEY, KAKAO_SENDER_KEY 환경변수 설정이 필요합니다.

        Returns:
            True if sent successfully, False otherwise
        """
        if not KakaoAlimtalkService._is_kakao_configured():
            # TODO: 카카오 비즈니스 API 연동 (외부 API 키 필요)
            logger.info(
                "[MOCK] 카카오 알림톡 발송: phone=%s, employee=%s, company=%s, %d/%02d, net=%s",
                phone_number, employee_name, company_name, year, month, net_salary,
            )
            return True

        # 실제 카카오 비즈니스 API 연동 시 아래 로직 구현 필요
        # 현재는 API 키가 있어도 실제 발송 로직 미구현 → False 반환
        logger.warning(
            "카카오 알림톡 API 키가 설정되었지만 실제 연동이 구현되지 않았습니다. "
            "phone=%s", phone_number,
        )
        return False
