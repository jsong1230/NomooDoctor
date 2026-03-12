"""법령 시드 데이터 삽입 스크립트

주요 근로기준법, 최저임금법 조항 10개를 law_vectors 테이블에 삽입한다.
embedding 컬럼은 null로 유지하며, 이후 별도 배치 작업으로 OpenAI API를 통해 생성한다.

실행 방법:
    # Docker 컨테이너 내부에서
    docker compose exec backend python scripts/seed_law_data.py

    # 로컬에서 (backend/ 디렉토리 기준)
    python scripts/seed_law_data.py
"""
import sys
import os
import uuid
from datetime import datetime, timezone

# backend/ 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.models.law_vector import LawVector

# 삽입할 법령 조항 시드 데이터
SEED_DATA = [
    {
        "law_name": "근로기준법",
        "article": "제2조",
        "content": (
            "근로자란 직업의 종류와 관계없이 임금을 목적으로 사업이나 사업장에 "
            "근로를 제공하는 사람을 말한다."
        ),
        "keywords": ["근로자", "정의", "임금"],
    },
    {
        "law_name": "근로기준법",
        "article": "제17조",
        "content": (
            "사용자는 근로계약을 체결할 때에 근로자에게 임금, 소정근로시간, 휴일, "
            "연차 유급휴가 등의 근로조건을 명시하여야 한다."
        ),
        "keywords": ["근로계약", "명시의무", "근로조건"],
    },
    {
        "law_name": "근로기준법",
        "article": "제23조",
        "content": (
            "사용자는 근로자에게 정당한 이유 없이 해고, 휴직, 정직, 전직, 감봉, "
            "그 밖의 징벌을 하지 못한다."
        ),
        "keywords": ["해고", "부당해고", "징벌"],
    },
    {
        "law_name": "근로기준법",
        "article": "제26조",
        "content": (
            "사용자는 근로자를 해고하려면 적어도 30일 전에 예고를 하여야 하고, "
            "30일 전에 예고를 하지 아니하였을 때에는 30일분 이상의 통상임금을 "
            "지급하여야 한다."
        ),
        "keywords": ["해고예고", "30일", "통상임금"],
    },
    {
        "law_name": "근로기준법",
        "article": "제36조",
        "content": (
            "사용자는 근로자가 사망 또는 퇴직한 경우에는 그 지급 사유가 발생한 "
            "때부터 14일 이내에 임금, 보상금, 그 밖에 일체의 금품을 지급하여야 한다."
        ),
        "keywords": ["퇴직금", "14일", "금품지급"],
    },
    {
        "law_name": "근로기준법",
        "article": "제48조",
        "content": (
            "사용자는 임금을 지급하는 때에는 근로자에게 임금의 구성항목·계산방법, "
            "공제내역 등 대통령령으로 정하는 사항을 적은 임금명세서를 "
            "서면(전자문서 포함)으로 교부하여야 한다."
        ),
        "keywords": ["임금명세서", "교부의무", "급여명세서"],
    },
    {
        "law_name": "근로기준법",
        "article": "제50조",
        "content": (
            "1주 간의 근로시간은 휴게시간을 제외하고 40시간을 초과할 수 없다. "
            "1일의 근로시간은 휴게시간을 제외하고 8시간을 초과할 수 없다."
        ),
        "keywords": ["근로시간", "40시간", "8시간", "주52시간"],
    },
    {
        "law_name": "근로기준법",
        "article": "제55조",
        "content": (
            "사용자는 근로자에게 1주에 평균 1회 이상의 유급휴일을 보장하여야 한다."
        ),
        "keywords": ["유급휴일", "주휴일", "주휴수당"],
    },
    {
        "law_name": "근로기준법",
        "article": "제60조",
        "content": (
            "사용자는 1년간 80퍼센트 이상 출근한 근로자에게 15일의 유급휴가를 "
            "주어야 한다."
        ),
        "keywords": ["연차", "유급휴가", "15일", "출근율"],
    },
    {
        "law_name": "최저임금법",
        "article": "제6조",
        "content": (
            "사용자는 최저임금의 적용을 받는 근로자에게 최저임금액 이상의 임금을 "
            "지급하여야 한다."
        ),
        "keywords": ["최저임금", "임금지급", "위반"],
    },
]


def seed_law_data() -> None:
    """law_vectors 테이블에 시드 데이터를 삽입한다."""
    engine = create_engine(str(settings.DATABASE_URL), echo=False)

    with Session(engine) as session:
        # 기존 데이터 중복 삽입 방지 — law_name + article 조합 기준
        existing_keys: set[tuple[str, str]] = set(
            session.execute(
                text("SELECT law_name, article FROM law_vectors")
            ).fetchall()
        )

        records_to_insert: list[LawVector] = []
        skipped = 0

        for item in SEED_DATA:
            key = (item["law_name"], item["article"])
            if key in existing_keys:
                skipped += 1
                continue

            records_to_insert.append(
                LawVector(
                    id=uuid.uuid4(),
                    law_name=item["law_name"],
                    article=item["article"],
                    content=item["content"],
                    embedding=None,  # OpenAI API 호출 후 별도 업데이트
                    keywords=item["keywords"],
                    created_at=datetime.now(tz=timezone.utc),
                )
            )

        if records_to_insert:
            session.add_all(records_to_insert)
            session.commit()
            print(
                f"[seed_law_data] {len(records_to_insert)}개 조항 삽입 완료. "
                f"(건너뜀: {skipped}개)"
            )
        else:
            print(f"[seed_law_data] 삽입할 신규 데이터 없음. (이미 존재: {skipped}개)")


if __name__ == "__main__":
    seed_law_data()
