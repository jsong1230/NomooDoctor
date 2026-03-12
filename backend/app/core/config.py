# 환경변수 설정
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, Field
from typing import Literal
from functools import lru_cache
from dotenv import load_dotenv

# .env 파일 로드
BACKEND_ROOT = Path(__file__).parent.parent.parent
load_dotenv(BACKEND_ROOT / ".env")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BACKEND_ROOT / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # 애플리케이션 설정
    PROJECT_NAME: str = "NomooDoctor"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = True

    # 데이터베이스 설정
    DATABASE_URL: str = "postgresql://nomoodoc:nomoodoc@localhost:5432/nomoodoc"

    # Redis 설정
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT 설정
    JWT_SECRET_KEY: str = "dev-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # 암호화 설정
    ENCRYPTION_KEY: str = "encryption-key-32-chars-long!!"

    # AI 설정
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-sonnet-4-6"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"

    # CORS 설정 (쉼표로 구분된 문자열을 리스트로 변환)
    CORS_ORIGINS_STR: str = Field(default="http://localhost:3000", alias="CORS_ORIGINS")

    @property
    def CORS_ORIGINS(self) -> list[str]:
        if isinstance(self.CORS_ORIGINS_STR, str):
            return [origin.strip() for origin in self.CORS_ORIGINS_STR.split(",")]
        return ["http://localhost:3000"]

    # 외부 서비스
    TOSS_API_KEY: str = ""
    KAKAO_CLIENT_ID: str = ""
    KAKAO_CLIENT_SECRET: str = ""
    MODUSIGN_API_KEY: str = ""

    # AWS S3
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_S3_BUCKET: str = ""
    AWS_REGION: str = "ap-northeast-2"

    # 이메일 (SendGrid)
    SENDGRID_API_KEY: str = ""
    SENDGRID_FROM_EMAIL: str = "noreply@nomoodoc.com"

    # SMTP 설정 (선택 - 미설정 시 mock 모드)
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "noreply@nomoodoctor.com"
    SMTP_USE_TLS: bool = True

    # 카카오 알림톡 (선택 - 미설정 시 mock 모드)
    KAKAO_API_KEY: str = ""
    KAKAO_SENDER_KEY: str = ""


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
