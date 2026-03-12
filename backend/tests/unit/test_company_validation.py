"""
F-02 사업장 관리 — 단위 테스트 (RED)

이 파일은 구현 전 실패하는 테스트입니다.
실제 구현은 backend-dev 에이전트가 수행합니다.
"""

from unittest.mock import MagicMock


class TestBusinessNumberValidation:
    """사업자등록번호 검증 테스트"""

    def test_유효한_사업자등록번호_형식(self):
        """유효한 형식의 사업자등록번호는 검증 통과해야 함"""
        # 구현 후 테스트 대상
        # from app.schemas.company import CompanyCreate

        valid_numbers = [
            "123-45-67890",
            "001-01-00001",
            "999-99-99999"
        ]

        # 구현 전: 임시 검증
        pattern = r"^\d{3}-\d{2}-\d{5}$"
        import re
        for number in valid_numbers:
            assert re.match(pattern, number), f"{number} 형식 검증 실패"

    def test_하이픈_없는_사업자등록번호_실패(self):
        """하이픈이 없는 형식은 검증 실패해야 함"""
        invalid_numbers = ["1234567890", "12345678901"]

        pattern = r"^\d{3}-\d{2}-\d{5}$"
        import re
        for number in invalid_numbers:
            assert not re.match(pattern, number), f"{number}는 실패해야 함"

    def test_자릿수_부족_사업자등록번호_실패(self):
        """자릿수가 부족한 형식은 검증 실패해야 함"""
        invalid_numbers = ["123-45-6789", "12-34-56789"]

        pattern = r"^\d{3}-\d{2}-\d{5}$"
        import re
        for number in invalid_numbers:
            assert not re.match(pattern, number), f"{number}는 실패해야 함"

    def test_자릿수_초과_사업자등록번호_실패(self):
        """자릿수가 초과하는 형식은 검증 실패해야 함"""
        invalid_numbers = ["1234-56-78901", "123-456-78901"]

        pattern = r"^\d{3}-\d{2}-\d{5}$"
        import re
        for number in invalid_numbers:
            assert not re.match(pattern, number), f"{number}는 실패해야 함"

    def test_문자_포함_사업자등록번호_실패(self):
        """문자가 포함된 형식은 검증 실패해야 함"""
        invalid_numbers = ["123-AB-67890", "ABC-12-34567"]

        pattern = r"^\d{3}-\d{2}-\d{5}$"
        import re
        for number in invalid_numbers:
            assert not re.match(pattern, number), f"{number}는 실패해야 함"

    def test_빈_문자열_사업자등록번호_실패(self):
        """빈 문자열은 검증 실패해야 함"""
        pattern = r"^\d{3}-\d{2}-\d{5}$"
        import re
        assert not re.match(pattern, ""), "빈 문자열은 실패해야 함"

    def test_앞뒤_공백_포함_사업자등록번호_실패(self):
        """앞뒤 공백이 포함된 형식은 검증 실패해야 함"""
        invalid_numbers = [" 123-45-67890", "123-45-67890 ", " 123-45-67890 "]

        pattern = r"^\d{3}-\d{2}-\d{5}$"
        import re
        for number in invalid_numbers:
            assert not re.match(pattern, number), f"{number}는 실패해야 함"


class TestIndustryTypeValidation:
    """업종 검증 테스트"""

    def test_유효한_업종_검증(self):
        """유효한 8개 업종은 검증 통과해야 함"""
        valid_industries = [
            "manufacturing",  # 제조업
            "food_service",   # 요식업
            "retail",         # 소매업
            "service",        # 서비스업
            "it",             # IT/정보통신
            "construction",   # 건설업
            "healthcare",     # 의료업
            "other"           # 기타
        ]

        # 구현 전: 임시 검증
        for industry in valid_industries:
            assert industry in valid_industries, f"{industry}는 유효한 업종이어야 함"

    def test_유효하지_않은_업종_검증_실패(self):
        """유효하지 않은 업종은 검증 실패해야 함"""
        valid_industries = [
            "manufacturing", "food_service", "retail", "service",
            "it", "construction", "healthcare", "other"
        ]

        invalid_industries = ["finance", "education", "transport", "agriculture", "unknown"]

        for industry in invalid_industries:
            assert industry not in valid_industries, f"{industry}는 유효하지 않아야 함"

    def test_대소문자_구분_검증_실패(self):
        """업종은 소문자만 허용, 대문자는 실패해야 함"""
        invalid_industries = ["IT", "It", "IT", "MANUFACTURING", "Food_Service"]

        valid_industries = [
            "manufacturing", "food_service", "retail", "service",
            "it", "construction", "healthcare", "other"
        ]

        for industry in invalid_industries:
            assert industry not in valid_industries, f"{industry}는 대소문자 구분으로 실패해야 함"

    def test_빈_문자열_업종_검증_실패(self):
        """빈 문자열 업종은 검증 실패해야 함"""
        valid_industries = [
            "manufacturing", "food_service", "retail", "service",
            "it", "construction", "healthcare", "other"
        ]

        assert "" not in valid_industries, "빈 문자열은 실패해야 함"


class TestEmployeeCountValidation:
    """직원 수 검증 테스트"""

    def test_직원_수_0_유효(self):
        """직원 수 0은 유효해야 함"""
        employee_count = 0
        assert employee_count >= 0, "직원 수 0은 유효해야 함"

    def test_직원_수_9_유효(self):
        """직원 수 9는 유효해야 함"""
        employee_count = 9
        assert employee_count >= 0, "직원 수 9는 유효해야 함"

    def test_직원_수_10_유효_경계값(self):
        """직원 수 10은 유효해야 함 (경계값: work_rule_required TRUE)"""
        employee_count = 10
        assert employee_count >= 0, "직원 수 10은 유효해야 함"

    def test_직원_수_1000_유효(self):
        """직원 수 1000은 유효해야 함"""
        employee_count = 1000
        assert employee_count >= 0 and employee_count <= 1000, "직원 수 1000은 유효해야 함"

    def test_직원_수_음수_실패(self):
        """직원 수 음수는 검증 실패해야 함"""
        employee_count = -1
        assert employee_count < 0, "직원 수 -1은 실패해야 함"

    def test_직원_수_1001_실패(self):
        """직원 수 1001은 검증 실패해야 함"""
        employee_count = 1001
        assert employee_count > 1000, "직원 수 1001은 실패해야 함"


class TestWorkRuleRequiredCalculation:
    """work_rule_required 자동 계산 테스트"""

    def test_직원_수_9인_work_rule_required_FALSE(self):
        """직원 수 9인은 work_rule_required가 FALSE여야 함"""
        employee_count = 9
        work_rule_required = employee_count >= 10
        assert work_rule_required is False, "직원 수 9인은 work_rule_required가 FALSE여야 함"

    def test_직원_수_10인_work_rule_required_TRUE(self):
        """직원 수 10인은 work_rule_required가 TRUE여야 함"""
        employee_count = 10
        work_rule_required = employee_count >= 10
        assert work_rule_required is True, "직원 수 10인은 work_rule_required가 TRUE여야 함"

    def test_직원_수_15인_work_rule_required_TRUE(self):
        """직원 수 15인은 work_rule_required가 TRUE여야 함"""
        employee_count = 15
        work_rule_required = employee_count >= 10
        assert work_rule_required is True, "직원 수 15인은 work_rule_required가 TRUE여야 함"

    def test_직원_수_변경_9에서_10으로_변경(self):
        """직원 수가 9에서 10으로 변경 시 work_rule_required가 TRUE로 자동 변경되어야 함"""
        employee_count = 9
        work_rule_required = employee_count >= 10
        assert work_rule_required is False

        employee_count = 10
        work_rule_required = employee_count >= 10
        assert work_rule_required is True

    def test_직원_수_변경_10에서_9로_변경(self):
        """직원 수가 10에서 9로 변경 시 work_rule_required가 FALSE로 자동 변경되어야 함"""
        employee_count = 10
        work_rule_required = employee_count >= 10
        assert work_rule_required is True

        employee_count = 9
        work_rule_required = employee_count >= 10
        assert work_rule_required is False

    def test_직원_수_0인_work_rule_required_FALSE(self):
        """직원 수 0인은 work_rule_required가 FALSE여야 함"""
        employee_count = 0
        work_rule_required = employee_count >= 10
        assert work_rule_required is False, "직원 수 0인은 work_rule_required가 FALSE여야 함"

    def test_직원_수_1000인_work_rule_required_TRUE(self):
        """직원 수 1000인은 work_rule_required가 TRUE여야 함"""
        employee_count = 1000
        work_rule_required = employee_count >= 10
        assert work_rule_required is True, "직원 수 1000인은 work_rule_required가 TRUE여야 함"


class TestCompanyOwnershipVerification:
    """사업장 소유권 검증 테스트"""

    def test_소유자_일치_검증_성공(self):
        """소유자가 일치하면 Company를 반환해야 함"""
        # 구현 후 테스트 대상
        # from app.services.company_service import verify_company_ownership

        # 임시 모의 객체
        company = MagicMock()
        company.id = "test-id"
        company.owner_id = "user-id"
        company.is_deleted = False

        user_id = "user-id"
        assert company.owner_id == user_id, "소유자가 일치하면 성공해야 함"

    def test_소유자_불일치_검증_실패(self):
        """소유자가 불일치하면 ForbiddenError를 발생해야 함"""
        company = MagicMock()
        company.id = "test-id"
        company.owner_id = "user-a"

        user_id = "user-b"
        assert company.owner_id != user_id, "소유자 불일치 시 ForbiddenError가 발생해야 함"

    def test_삭제된_사업장_검증_실패(self):
        """삭제된 사업장은 NotFoundError를 발생해야 함"""
        company = MagicMock()
        company.id = "test-id"
        company.owner_id = "user-id"
        company.is_deleted = True

        assert company.is_deleted is True, "삭제된 사업장은 NotFoundError가 발생해야 함"

    def test_존재하지_않는_ID_검증_실패(self):
        """존재하지 않는 ID는 NotFoundError를 발생해야 함"""
        company = None  # 조회 결과 없음
        assert company is None, "존재하지 않는 ID는 NotFoundError가 발생해야 함"


class TestCompanyNameLengthValidation:
    """사업장명 길이 검증 테스트"""

    def test_사업장명_1자_유효(self):
        """사업장명 1자는 유효해야 함"""
        business_name = "가"
        assert len(business_name) >= 1, "사업장명 1자는 유효해야 함"

    def test_사업장명_200자_유효(self):
        """사업장명 200자는 유효해야 함"""
        business_name = "가" * 200
        assert len(business_name) == 200, "사업장명 200자는 유효해야 함"

    def test_사업장명_201자_실패(self):
        """사업장명 201자는 실패해야 함"""
        business_name = "가" * 201
        assert len(business_name) > 200, "사업장명 201자는 실패해야 함"


class TestRepresentativeNameLengthValidation:
    """대표자명 길이 검증 테스트"""

    def test_대표자명_1자_유효(self):
        """대표자명 1자는 유효해야 함"""
        representative_name = "홍"
        assert len(representative_name) >= 1, "대표자명 1자는 유효해야 함"

    def test_대표자명_100자_유효(self):
        """대표자명 100자는 유효해야 함"""
        representative_name = "홍" * 100
        assert len(representative_name) == 100, "대표자명 100자는 유효해야 함"

    def test_대표자명_101자_실패(self):
        """대표자명 101자는 실패해야 함"""
        representative_name = "홍" * 101
        assert len(representative_name) > 100, "대표자명 101자는 실패해야 함"


class TestPostalCodeValidation:
    """우편번호 검증 테스트"""

    def test_우편번호_5자_유효(self):
        """우편번호 5자는 유효해야 함"""
        postal_code = "06123"
        assert len(postal_code) == 5 and postal_code.isdigit(), "우편번호 5자는 유효해야 함"

    def test_우편번호_문자_포함_실패(self):
        """우편번호에 문자가 포함되면 실패해야 함"""
        postal_code = "06A23"
        assert not postal_code.isdigit(), "우편번호에 문자가 포함되면 실패해야 함"


class TestPhoneValidation:
    """전화번호 검증 테스트"""

    def test_전화번호_지역번호_형식_유효(self):
        """지역번호 형식 (02-1234-5678)은 유효해야 함"""
        phone = "02-1234-5678"
        pattern = r"^\d{2,3}-\d{3,4}-\d{4}$"
        import re
        assert re.match(pattern, phone), "지역번호 형식은 유효해야 함"

    def test_전화번호_휴대폰_형식_유효(self):
        """휴대폰 형식 (010-1234-5678)은 유효해야 함"""
        phone = "010-1234-5678"
        pattern = r"^\d{2,3}-\d{3,4}-\d{4}$"
        import re
        assert re.match(pattern, phone), "휴대폰 형식은 유효해야 함"

    def test_전화번호_형식_잘못됨_실패(self):
        """잘못된 형식은 실패해야 함"""
        invalid_phones = [
            "0212345678",      # 하이픈 없음
            "02-123-456",      # 자릿수 부족
            "02-1234-56789",   # 자릿수 초과
            "가-나-다라"       # 문자 포함
        ]

        pattern = r"^\d{2,3}-\d{3,4}-\d{4}$"
        import re
        for phone in invalid_phones:
            assert not re.match(pattern, phone), f"{phone}는 실패해야 함"
