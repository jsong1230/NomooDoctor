# 취업규칙 업종별 템플릿

WORK_RULE_TEMPLATES = {
    "manufacturing": {
        "industry_name": "제조업",
        "description": "제조업 사업장 표준 취업규칙",
        "sections": [
            {
                "section_number": 1,
                "title": "업무의 시작과 종료 시각, 휴게시간, 휴일, 휴가 및 교대근로에 관한 사항",
                "description": "근로기준법 제93조 제1호",
                "content_template": "<h2>제1조 (근로시간)</h2><p>근로자의 근로시간은 월~금 09:00~18:00(점심시간 12:00~13:00)으로 합니다.</p><p>야간 근로 및 교대근로의 경우 별도의 근로시간표에 따릅니다.</p><h2>제2조 (휴게시간)</h2><p>근로자에게 4시간마다 10분, 8시간 근로 시 1시간의 휴게시간을 제공합니다.</p>"
            },
            {
                "section_number": 2,
                "title": "임금의 결정, 계산, 지급 방법, 임금의 산정기간, 지급시기 및 승급에 관한 사항",
                "description": "근로기준법 제93조 제2호",
                "content_template": "<h2>제1조 (임금의 구성)</h2><p>임금은 기본급 및 각종 수당으로 구성합니다.</p><h2>제2조 (임금 지급)</h2><p>임금은 매월 25일 계좌이체로 지급합니다.</p><p>산정기간은 당월 1일~말일입니다.</p>"
            },
            {
                "section_number": 3,
                "title": "가족수당의 계산, 지급 방법에 관한 사항",
                "description": "근로기준법 제93조 제3호",
                "content_template": "<h2>제1조 (가족수당)</h2><p>가족수당은 다음과 같이 지급합니다.</p><ul><li>배우자: 월 50,000원</li><li>자녀(1인당): 월 30,000원</li></ul>"
            },
            {
                "section_number": 4,
                "title": "퇴직에 관한 사항",
                "description": "근로기준법 제93조 제4호",
                "content_template": "<h2>제1조 (퇴직의 종류)</h2><p>퇴직은 정년퇴직, 자의퇴직, 강제퇴직으로 구분합니다.</p><h2>제2조 (퇴직금)</h2><p>퇴직금은 근로기준법 제34조에 따라 계산하여 퇴직 후 14일 이내에 지급합니다.</p>"
            },
            {
                "section_number": 5,
                "title": "퇴직급여, 상여 및 최저임금에 관한 사항",
                "description": "근로기준법 제93조 제5호",
                "content_template": "<h2>제1조 (상여금)</h2><p>상여금은 회사의 실적에 따라 결정되며, 별도로 지급합니다.</p><h2>제2조 (최저임금 준수)</h2><p>회사는 법정 최저임금을 보장합니다.</p>"
            },
            {
                "section_number": 6,
                "title": "근로자의 식비, 작업용품 등의 부담에 관한 사항",
                "description": "근로기준법 제93조 제6호",
                "content_template": "<h2>제1조 (작업용품)</h2><p>회사가 제공하는 보호구 및 작업용품은 회사가 부담합니다.</p><p>근로자의 개인용품으로 인한 손실은 책임지지 않습니다.</p>"
            },
            {
                "section_number": 7,
                "title": "근로자를 위한 교육시설에 관한 사항",
                "description": "근로기준법 제93조 제7호",
                "content_template": "<h2>제1조 (교육)</h2><p>회사는 근로자의 직무 능력 향상을 위해 필요한 교육을 실시합니다.</p>"
            },
            {
                "section_number": 8,
                "title": "출산전후휴가, 육아휴직 등 근로자의 모성 보호 및 일-가정 양립 지원에 관한 사항",
                "description": "근로기준법 제93조 제8호",
                "content_template": "<h2>제1조 (출산전후휴가)</h2><p>여성 근로자는 출산전후 90일의 휴가를 가질 수 있습니다.</p><h2>제2조 (육아휴직)</h2><p>근로자는 만 8세 이하의 자녀에 대해 육아휴직을 신청할 수 있습니다.</p>"
            },
            {
                "section_number": 9,
                "title": "안전과 보건에 관한 사항",
                "description": "근로기준법 제93조 제9호",
                "content_template": "<h2>제1조 (안전보건 관리)</h2><p>회사는 산업안전보건법에 따라 안전 및 보건 관련 조치를 취합니다.</p><p>근로자는 안전 교육에 참여하여야 합니다.</p>"
            },
            {
                "section_number": 10,
                "title": "근로자의 성별, 연령 또는 신체적 조건 등의 특성에 따른 사업장 환경의 개선에 관한 사항",
                "description": "근로기준법 제93조 제10호",
                "content_template": "<h2>제1조 (차별금지)</h2><p>회사는 성별, 연령, 신체적 조건 등을 이유로 부당한 차별을 하지 않습니다.</p>"
            },
            {
                "section_number": 11,
                "title": "업무상과 업무 외의 재해부조에 관한 사항",
                "description": "근로기준법 제93조 제11호",
                "content_template": "<h2>제1조 (산업재해 보상)</h2><p>업무상 재해는 산업재해보상보험법에 따라 처리합니다.</p>"
            },
            {
                "section_number": 12,
                "title": "직장 내 괴롭힘의 예방 및 발생 시 조치 등에 관한 사항",
                "description": "근로기준법 제93조 제11의2호",
                "content_template": "<h2>제1조 (직장 내 괴롭힘 금지)</h2><p>직장 내 괴롭힘을 금지합니다.</p><p>피해 신고 시 성실하게 조사하고 필요한 조치를 취합니다.</p>"
            },
            {
                "section_number": 13,
                "title": "표창과 제재에 관한 사항",
                "description": "근로기준법 제93조 제12호",
                "content_template": "<h2>제1조 (표창)</h2><p>우수한 근로실적을 거둔 근로자는 표창합니다.</p><h2>제2조 (징계)</h2><p>징계 사유 및 징계 기준은 별도로 정합니다.</p>"
            },
            {
                "section_number": 14,
                "title": "기타 해당 사업 또는 사업장의 근로자 전체에 적용될 사항",
                "description": "근로기준법 제93조 제13호",
                "content_template": "<h2>제1조 (근무규칙)</h2><p>근로자는 사업장의 규칙을 준수하여야 합니다.</p>"
            }
        ]
    },
    "food_service": {
        "industry_name": "요식업",
        "description": "요식업 사업장 표준 취업규칙",
        "sections": [
            {
                "section_number": 1,
                "title": "업무의 시작과 종료 시각, 휴게시간, 휴일, 휴가 및 교대근로에 관한 사항",
                "description": "근로기준법 제93조 제1호",
                "content_template": "<h2>제1조 (근로시간)</h2><p>근로자의 근로시간은 일일 8시간, 주 40시간을 원칙으로 합니다.</p><p>점심 및 저녁 시간대 영업 특성상 교대근로를 실시합니다.</p><h2>제2조 (휴게시간)</h2><p>4시간 근로 시마다 최소 10분의 휴게시간을 제공합니다.</p>"
            },
            {
                "section_number": 2,
                "title": "임금의 결정, 계산, 지급 방법, 임금의 산정기간, 지급시기 및 승급에 관한 사항",
                "description": "근로기준법 제93조 제2호",
                "content_template": "<h2>제1조 (임금)</h2><p>임금은 기본급 및 매출액 연동 수당으로 구성합니다.</p><h2>제2조 (지급)</h2><p>임금은 매월 말일에 계좌이체로 지급합니다.</p>"
            },
            {
                "section_number": 3,
                "title": "가족수당의 계산, 지급 방법에 관한 사항",
                "description": "근로기준법 제93조 제3호",
                "content_template": "<h2>제1조 (가족수당)</h2><p>가족수당은 회사 정책에 따라 지급합니다.</p>"
            },
            {
                "section_number": 4,
                "title": "퇴직에 관한 사항",
                "description": "근로기준법 제93조 제4호",
                "content_template": "<h2>제1조 (퇴직금)</h2><p>퇴직금은 근로기준법 제34조에 따라 계산합니다.</p>"
            },
            {
                "section_number": 5,
                "title": "퇴직급여, 상여 및 최저임금에 관한 사항",
                "description": "근로기준법 제93조 제5호",
                "content_template": "<h2>제1조 (상여금)</h2><p>상여금은 분기별로 지급합니다.</p>"
            },
            {
                "section_number": 6,
                "title": "근로자의 식비, 작업용품 등의 부담에 관한 사항",
                "description": "근로기준법 제93조 제6호",
                "content_template": "<h2>제1조 (식사)</h2><p>근로자는 근무 중 식사를 제공받습니다.</p>"
            },
            {
                "section_number": 7,
                "title": "근로자를 위한 교육시설에 관한 사항",
                "description": "근로기준법 제93조 제7호",
                "content_template": "<h2>제1조 (교육)</h2><p>조리 및 서빙 교육을 정기적으로 실시합니다.</p>"
            },
            {
                "section_number": 8,
                "title": "출산전후휴가, 육아휴직 등 근로자의 모성 보호 및 일-가정 양립 지원에 관한 사항",
                "description": "근로기준법 제93조 제8호",
                "content_template": "<h2>제1조 (모성보호)</h2><p>법정 출산전후휴가 및 육아휴직을 보장합니다.</p>"
            },
            {
                "section_number": 9,
                "title": "안전과 보건에 관한 사항",
                "description": "근로기준법 제93조 제9호",
                "content_template": "<h2>제1조 (위생관리)</h2><p>식품 위생 및 안전 관리를 철저히 합니다.</p>"
            },
            {
                "section_number": 10,
                "title": "근로자의 성별, 연령 또는 신체적 조건 등의 특성에 따른 사업장 환경의 개선에 관한 사항",
                "description": "근로기준법 제93조 제10호",
                "content_template": "<h2>제1조 (차별금지)</h2><p>모든 근로자에게 평등한 기회를 제공합니다.</p>"
            },
            {
                "section_number": 11,
                "title": "업무상과 업무 외의 재해부조에 관한 사항",
                "description": "근로기준법 제93조 제11호",
                "content_template": "<h2>제1조 (상해 대응)</h2><p>업무 중 상해는 산업재해보험으로 처리합니다.</p>"
            },
            {
                "section_number": 12,
                "title": "직장 내 괴롭힘의 예방 및 발생 시 조치 등에 관한 사항",
                "description": "근로기준법 제93조 제11의2호",
                "content_template": "<h2>제1조 (괴롭힘 금지)</h2><p>직장 내 괴롭힘을 엄격하게 금지합니다.</p>"
            },
            {
                "section_number": 13,
                "title": "표창과 제재에 관한 사항",
                "description": "근로기준법 제93조 제12호",
                "content_template": "<h2>제1조 (포상)</h2><p>우수 근로자에게 보너스를 지급합니다.</p><h2>제2조 (징계)</h2><p>징계 규정을 별도로 운영합니다.</p>"
            },
            {
                "section_number": 14,
                "title": "기타 해당 사업 또는 사업장의 근로자 전체에 적용될 사항",
                "description": "근로기준법 제93조 제13호",
                "content_template": "<h2>제1조 (기타)</h2><p>본 규칙에 명시되지 않은 사항은 법령을 따릅니다.</p>"
            }
        ]
    },
    "service": {
        "industry_name": "서비스업",
        "description": "서비스업 사업장 표준 취업규칙",
        "sections": [
            {
                "section_number": 1,
                "title": "업무의 시작과 종료 시각, 휴게시간, 휴일, 휴가 및 교대근로에 관한 사항",
                "description": "근로기준법 제93조 제1호",
                "content_template": "<h2>제1조 (근로시간)</h2><p>근로자의 근로시간은 월~금 10:00~19:00입니다.</p><p>주말 근무 시 별도 협의합니다.</p>"
            },
            {
                "section_number": 2,
                "title": "임금의 결정, 계산, 지급 방법, 임금의 산정기간, 지급시기 및 승급에 관한 사항",
                "description": "근로기준법 제93조 제2호",
                "content_template": "<h2>제1조 (임금 체계)</h2><p>월급제 및 시급제 근로자를 구분하여 관리합니다.</p>"
            },
            {
                "section_number": 3,
                "title": "가족수당의 계산, 지급 방법에 관한 사항",
                "description": "근로기준법 제93조 제3호",
                "content_template": "<h2>제1조 (수당)</h2><p>성과급 및 인센티브를 지급합니다.</p>"
            },
            {
                "section_number": 4,
                "title": "퇴직에 관한 사항",
                "description": "근로기준법 제93조 제4호",
                "content_template": "<h2>제1조 (퇴직 처리)</h2><p>퇴직금을 근로기준법에 따라 지급합니다.</p>"
            },
            {
                "section_number": 5,
                "title": "퇴직급여, 상여 및 최저임금에 관한 사항",
                "description": "근로기준법 제93조 제5호",
                "content_template": "<h2>제1조 (최저임금)</h2><p>법정 최저임금을 준수합니다.</p>"
            },
            {
                "section_number": 6,
                "title": "근로자의 식비, 작업용품 등의 부담에 관한 사항",
                "description": "근로기준법 제93조 제6호",
                "content_template": "<h2>제1조 (부담금)</h2><p>개인용품은 근로자가 부담합니다.</p>"
            },
            {
                "section_number": 7,
                "title": "근로자를 위한 교육시설에 관한 사항",
                "description": "근로기준법 제93조 제7호",
                "content_template": "<h2>제1조 (교육)</h2><p>정기적인 직무 교육을 실시합니다.</p>"
            },
            {
                "section_number": 8,
                "title": "출산전후휴가, 육아휴직 등 근로자의 모성 보호 및 일-가정 양립 지원에 관한 사항",
                "description": "근로기준법 제93조 제8호",
                "content_template": "<h2>제1조 (보호)</h2><p>모성 보호 관련 휴가를 지원합니다.</p>"
            },
            {
                "section_number": 9,
                "title": "안전과 보건에 관한 사항",
                "description": "근로기준법 제93조 제9호",
                "content_template": "<h2>제1조 (안전)</h2><p>작업 환경의 안전을 유지합니다.</p>"
            },
            {
                "section_number": 10,
                "title": "근로자의 성별, 연령 또는 신체적 조건 등의 특성에 따른 사업장 환경의 개선에 관한 사항",
                "description": "근로기준법 제93조 제10호",
                "content_template": "<h2>제1조 (평등)</h2><p>차별 없는 근무 환경을 조성합니다.</p>"
            },
            {
                "section_number": 11,
                "title": "업무상과 업무 외의 재해부조에 관한 사항",
                "description": "근로기준법 제93조 제11호",
                "content_template": "<h2>제1조 (보상)</h2><p>산업재해 시 보험으로 처리합니다.</p>"
            },
            {
                "section_number": 12,
                "title": "직장 내 괴롭힘의 예방 및 발생 시 조치 등에 관한 사항",
                "description": "근로기준법 제93조 제11의2호",
                "content_template": "<h2>제1조 (예방)</h2><p>괴롭힘을 금지하고 신고를 받습니다.</p>"
            },
            {
                "section_number": 13,
                "title": "표창과 제재에 관한 사항",
                "description": "근로기준법 제93조 제12호",
                "content_template": "<h2>제1조 (상벌)</h2><p>상벌 기준을 명확히 합니다.</p>"
            },
            {
                "section_number": 14,
                "title": "기타 해당 사업 또는 사업장의 근로자 전체에 적용될 사항",
                "description": "근로기준법 제93조 제13호",
                "content_template": "<h2>제1조 (기타)</h2><p>추가 사항은 별도 규정으로 정합니다.</p>"
            }
        ]
    },
    "it": {
        "industry_name": "IT업",
        "description": "IT업 사업장 표준 취업규칙",
        "sections": [
            {
                "section_number": 1,
                "title": "업무의 시작과 종료 시각, 휴게시간, 휴일, 휴가 및 교대근로에 관한 사항",
                "description": "근로기준법 제93조 제1호",
                "content_template": "<h2>제1조 (근로시간)</h2><p>근로자의 근로시간은 월~금 09:00~18:00입니다.</p><p>탄력근로시간제를 적용할 수 있습니다.</p>"
            },
            {
                "section_number": 2,
                "title": "임금의 결정, 계산, 지급 방법, 임금의 산정기간, 지급시기 및 승급에 관한 사항",
                "description": "근로기준법 제93조 제2호",
                "content_template": "<h2>제1조 (임금)</h2><p>임금은 기본급 및 성과급으로 구성합니다.</p><h2>제2조 (지급)</h2><p>매월 25일에 지급합니다.</p>"
            },
            {
                "section_number": 3,
                "title": "가족수당의 계산, 지급 방법에 관한 사항",
                "description": "근로기준법 제93조 제3호",
                "content_template": "<h2>제1조 (복리후생)</h2><p>복리후생비를 지급합니다.</p>"
            },
            {
                "section_number": 4,
                "title": "퇴직에 관한 사항",
                "description": "근로기준법 제93조 제4호",
                "content_template": "<h2>제1조 (퇴직금)</h2><p>퇴직금을 근로기준법에 따라 지급합니다.</p>"
            },
            {
                "section_number": 5,
                "title": "퇴직급여, 상여 및 최저임금에 관한 사항",
                "description": "근로기준법 제93조 제5호",
                "content_template": "<h2>제1조 (상여금)</h2><p>분기별 성과급을 지급합니다.</p>"
            },
            {
                "section_number": 6,
                "title": "근로자의 식비, 작업용품 등의 부담에 관한 사항",
                "description": "근로기준법 제93조 제6호",
                "content_template": "<h2>제1조 (장비)</h2><p>회사가 업무용 장비를 제공합니다.</p>"
            },
            {
                "section_number": 7,
                "title": "근로자를 위한 교육시설에 관한 사항",
                "description": "근로기준법 제93조 제7호",
                "content_template": "<h2>제1조 (교육)</h2><p>기술 교육 및 자격증 취득을 지원합니다.</p>"
            },
            {
                "section_number": 8,
                "title": "출산전후휴가, 육아휴직 등 근로자의 모성 보호 및 일-가정 양립 지원에 관한 사항",
                "description": "근로기준법 제93조 제8호",
                "content_template": "<h2>제1조 (일-가정 양립)</h2><p>모성 보호 및 유연 근무를 지원합니다.</p>"
            },
            {
                "section_number": 9,
                "title": "안전과 보건에 관한 사항",
                "description": "근로기준법 제93조 제9호",
                "content_template": "<h2>제1조 (건강)</h2><p>정기 건강검진을 실시합니다.</p>"
            },
            {
                "section_number": 10,
                "title": "근로자의 성별, 연령 또는 신체적 조건 등의 특성에 따른 사업장 환경의 개선에 관한 사항",
                "description": "근로기준법 제93조 제10호",
                "content_template": "<h2>제1조 (환경 개선)</h2><p>모두를 위한 업무 환경을 조성합니다.</p>"
            },
            {
                "section_number": 11,
                "title": "업무상과 업무 외의 재해부조에 관한 사항",
                "description": "근로기준법 제93조 제11호",
                "content_template": "<h2>제1조 (보험)</h2><p>산업재해보험을 가입합니다.</p>"
            },
            {
                "section_number": 12,
                "title": "직장 내 괴롭힘의 예방 및 발생 시 조치 등에 관한 사항",
                "description": "근로기준법 제93조 제11의2호",
                "content_template": "<h2>제1조 (괴롭힘 금지)</h2><p>직장 문화를 건강하게 유지합니다.</p>"
            },
            {
                "section_number": 13,
                "title": "표창과 제재에 관한 사항",
                "description": "근로기준법 제93조 제12호",
                "content_template": "<h2>제1조 (포상)</h2><p>우수 성과에 보상을 합니다.</p><h2>제2조 (징계)</h2><p>부정행위에 대해 징계합니다.</p>"
            },
            {
                "section_number": 14,
                "title": "기타 해당 사업 또는 사업장의 근로자 전체에 적용될 사항",
                "description": "근로기준법 제93조 제13호",
                "content_template": "<h2>제1조 (지적재산)</h2><p>업무 중 창출한 저작물은 회사에 귀속됩니다.</p>"
            }
        ]
    }
}


def get_template(industry_type: str) -> dict | None:
    """업종별 템플릿 조회"""
    return WORK_RULE_TEMPLATES.get(industry_type)


def get_all_templates() -> list[dict]:
    """모든 템플릿 목록 반환"""
    templates = []
    for industry_type, template_data in WORK_RULE_TEMPLATES.items():
        templates.append({
            "industry_type": industry_type,
            "industry_name": template_data["industry_name"],
            "description": template_data["description"],
            "sections": template_data["sections"]
        })
    return templates
