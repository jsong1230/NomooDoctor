# F-13 근태 관리 -- 테스트 명세

## 참조
- 설계서: docs/specs/F-13-attendance/design.md
- 인수조건: docs/project/features.md #F-13

---

## 단위 테스트

### AttendanceService.calculate_work_times()

| # | 시나리오 | 입력 | 예상 결과 |
|---|----------|------|-----------|
| U-01 | 정상 근무 (9~18, 휴게 60분) | actual_start=09:00, actual_end=18:00, scheduled=09:00~18:00, break=60, is_holiday=false | total=480, overtime=0, night=0, holiday=0 |
| U-02 | 연장근무 2시간 | actual_start=09:00, actual_end=20:00, scheduled=09:00~18:00, break=60, is_holiday=false | total=600, overtime=120, night=0, holiday=0 |
| U-03 | 야간근무 포함 (18~23시) | actual_start=18:00, actual_end=23:00, scheduled=18:00~22:00, break=30, is_holiday=false | total=270, overtime=30, night=60, holiday=0 |
| U-04 | 야간 자정 경계 (22~02시) | actual_start=22:00, actual_end=02:00, scheduled=22:00~02:00, break=0, is_holiday=false | total=240, overtime=0, night=240, holiday=0 |
| U-05 | 휴일근무 | actual_start=09:00, actual_end=18:00, scheduled=09:00~18:00, break=60, is_holiday=true | total=480, overtime=0, night=0, holiday=480 |
| U-06 | 휴일 + 연장 + 야간 | actual_start=09:00, actual_end=23:00, scheduled=09:00~18:00, break=60, is_holiday=true | total=780, overtime=300, night=60, holiday=780 |
| U-07 | 출근만 기록 (actual_end=None) | actual_start=09:00, actual_end=None | total=0, overtime=0, night=0, holiday=0 (미확정) |
| U-08 | 실제근무 없음 (both None) | actual_start=None, actual_end=None | total=0, overtime=0, night=0, holiday=0 |
| U-09 | 휴게시간 0분 | actual_start=09:00, actual_end=18:00, break=0 | total=540, overtime=60, night=0 |
| U-10 | 야간 전체 (22~06시 근무) | actual_start=22:00, actual_end=06:00, break=60, is_holiday=false | total=420, night=420 |
| U-11 | 짧은 근무 (4시간) | actual_start=09:00, actual_end=13:00, scheduled=09:00~18:00, break=0 | total=240, overtime=0 |
| U-12 | 새벽 출근 (05:00~14:00) | actual_start=05:00, actual_end=14:00, scheduled=06:00~15:00, break=60 | total=480, night=60 (05:00~06:00) |

### ExcelImportService.parse_file()

| # | 시나리오 | 입력 | 예상 결과 |
|---|----------|------|-----------|
| U-20 | 정상 xlsx 파싱 | 10행 정상 데이터 xlsx | 10개 ParsedRow, 에러 0 |
| U-21 | 정상 csv 파싱 | 10행 정상 데이터 csv | 10개 ParsedRow, 에러 0 |
| U-22 | 시간 형식 오류 | 3행: actual_start="abc" | 에러 1건: row=3, column="actual_start" |
| U-23 | 날짜 형식 오류 | 5행: work_date="2026/13/45" | 에러 1건: row=5, column="work_date" |
| U-24 | 필수 필드 누락 | 7행: work_date 빈칸 | 에러 1건: row=7, reason="필수 필드(work_date) 누락" |
| U-25 | 빈 파일 (헤더만) | 헤더만 있는 xlsx | total_rows=0, 에러 0 |
| U-26 | 혼합 오류 | 3행, 7행, 12행 오류 | 에러 3건, 각각 행 번호 명시 |
| U-27 | break_minutes 음수 | 4행: break_minutes=-10 | 에러 1건: row=4, reason="음수 불가" |
| U-28 | is_holiday 비표준 값 | "예" -> true, "Y" -> true, "1" -> true 변환 | 정상 파싱 |

### ExcelImportService.validate_rows()

| # | 시나리오 | 입력 | 예상 결과 |
|---|----------|------|-----------|
| U-30 | 존재하지 않는 직원 이름 | employee_name="김없음" | 에러: "직원을 찾을 수 없습니다." |
| U-31 | 동명이인 | employee_name="김철수" (2명 존재) | 에러: "동일 이름의 직원이 여러 명입니다." |
| U-32 | 파일 내 날짜 중복 | 같은 직원 같은 날짜 2행 | 에러: "파일 내 중복 데이터" |
| U-33 | DB 기존 데이터와 중복 | DB에 이미 존재하는 날짜 | 에러: "이미 근무 기록이 존재합니다." |

---

## 통합 테스트 (API)

### POST /api/v1/attendance/records

| # | 시나리오 | 입력 | 예상 결과 |
|---|----------|------|-----------|
| I-01 | 정상 근무 기록 생성 | 유효한 WorkRecordCreate | 201, 자동 계산된 overtime/night/holiday_minutes |
| I-02 | 인증 없이 요청 | Authorization 헤더 없음 | 401, E-2001 |
| I-03 | 다른 사업장 직원 | employee_id가 다른 company 소속 | 404, E-4004 |
| I-04 | 중복 날짜 기록 | 이미 존재하는 employee_id+work_date | 409, E-4010 |
| I-05 | actual_end < actual_start (야간 아님) | actual_start=18:00, actual_end=09:00, is_holiday=false | 정상 (다음날로 처리) 또는 422 (설계 결정 필요시) |
| I-06 | 필수 필드 누락 (work_date) | work_date 없음 | 400, E-1003 |
| I-07 | 퇴직 직원 기록 | is_active=false 직원 | 404, E-4004 |
| I-08 | break_minutes 범위 초과 (481분) | break_minutes=481 | 400, E-1001 |
| I-09 | 연장+야간 복합 계산 | actual=09:00~23:00, scheduled=09:00~18:00, break=60 | overtime=240, night=60 |

### POST /api/v1/attendance/records/batch

| # | 시나리오 | 입력 | 예상 결과 |
|---|----------|------|-----------|
| I-10 | 일괄 생성 (10건 정상) | 10건 유효 데이터 | 201, created=10, errors=[] |
| I-11 | 부분 성공 | 8건 정상, 2건 중복 | 201, created=8, skipped=2, errors 2건 |
| I-12 | 빈 배열 | records=[] | 400, E-1001 |
| I-13 | 최대 초과 (501건) | 501건 | 400, E-1001 |

### GET /api/v1/attendance/records

| # | 시나리오 | 입력 | 예상 결과 |
|---|----------|------|-----------|
| I-20 | 사업장 전체 조회 | company_id (JWT) | 200, 해당 사업장 전체 기록 |
| I-21 | 직원별 필터 | ?employee_id=xxx | 200, 해당 직원 기록만 |
| I-22 | 날짜 범위 필터 | ?from_date=2026-03-01&to_date=2026-03-31 | 200, 해당 범위 기록 |
| I-23 | 페이지네이션 | ?limit=10 | 200, 10건 + cursor |
| I-24 | year/month 필터 | ?year=2026&month=3 | 200, 2026년 3월 기록 |

### PUT /api/v1/attendance/records/{id}

| # | 시나리오 | 입력 | 예상 결과 |
|---|----------|------|-----------|
| I-30 | 정상 수정 | actual_end 변경 | 200, 시간 재계산 |
| I-31 | 다른 사업장 기록 수정 | 타 사업장 record_id | 404 |
| I-32 | 존재하지 않는 ID | 랜덤 UUID | 404 |
| I-33 | 부분 업데이트 | memo만 변경 | 200, 나머지 필드 유지 |

### DELETE /api/v1/attendance/records/{id}

| # | 시나리오 | 입력 | 예상 결과 |
|---|----------|------|-----------|
| I-40 | 정상 삭제 | 유효한 record_id | 204 |
| I-41 | 존재하지 않는 ID | 랜덤 UUID | 404 |
| I-42 | 타 사업장 기록 삭제 | 타 사업장 record_id | 404 |

### POST /api/v1/attendance/import

| # | 시나리오 | 입력 | 예상 결과 |
|---|----------|------|-----------|
| I-50 | 정상 xlsx 업로드 | 50행 정상 xlsx | 200, created=50, errors=[] |
| I-51 | 정상 csv 업로드 | 30행 정상 csv | 200, created=30, errors=[] |
| I-52 | 파싱 에러 포함 xlsx | 행 12, 25에 형식 오류 | 200, errors에 row 12, 25 명시 |
| I-53 | 지원하지 않는 형식 | .txt 파일 | 400, E-1001 |
| I-54 | 10MB 초과 파일 | 11MB xlsx | 413, E-1004 |
| I-55 | 빈 파일 | 헤더만 있는 xlsx | 200, total_rows=0 |
| I-56 | 동명이인 포함 | "김철수" 2명 존재 | errors에 해당 행 오류 명시 |

### GET /api/v1/attendance/import/template

| # | 시나리오 | 입력 | 예상 결과 |
|---|----------|------|-----------|
| I-60 | 템플릿 다운로드 | 인증된 요청 | 200, xlsx 파일 |

### GET /api/v1/attendance/summary

| # | 시나리오 | 입력 | 예상 결과 |
|---|----------|------|-----------|
| I-70 | 사업장 전체 월별 요약 | year=2026, month=3 | 200, employees[], company_total |
| I-71 | 직원별 요약 | year=2026, month=3, employee_id=xxx | 200, employees 1건 |
| I-72 | 데이터 없는 월 | year=2025, month=1 (기록 없음) | 200, employees=[], 0값 통계 |
| I-73 | 지각/조퇴/결근 카운트 | 지각 2일, 조퇴 1일 기록 | late_count=2, early_leave_count=1 |

### GET /api/v1/attendance/analysis

| # | 시나리오 | 입력 | 예상 결과 |
|---|----------|------|-----------|
| I-80 | 3개월 패턴 분석 | employee_id, 기본 기간 | 200, pattern + overtime_trend 3건 |
| I-81 | 연장근무 경고 | 월 연장 60시간 이상 직원 | alerts에 overtime_high 포함 |
| I-82 | 주 52시간 초과 경고 | 주 평균 53시간 | weekly_hours_warning=true |
| I-83 | 데이터 부족 | 1건만 있는 직원 | 200, 정상 응답 (평균=단일 값) |
| I-84 | 존재하지 않는 직원 | 랜덤 employee_id | 404, E-4004 |

---

## 경계 조건 / 에러 케이스

### 시간 계산 경계

- 자정 경계: actual_start=23:30, actual_end=00:30 → 다음날 처리, night_minutes=60
- 야간 전체 근무: 22:00~06:00 → night_minutes = 420 (480 - break 60)
- 소정근로시간 0분: scheduled_start == scheduled_end → overtime = total_work_minutes
- break_minutes > 실제 근무시간: break=300, 근무 4시간 → total=0 (음수 방지)
- 최대 근무시간: 24시간 근무 (actual_start=00:00, actual_end=23:59) → total=1379

### 엑셀 관련 경계

- 빈 행 건너뛰기: 중간에 빈 행 → 무시하고 다음 행 처리
- 헤더 순서 변경: 컬럼 순서 다름 → 헤더 이름 기반 매칭
- 셀 서식: 날짜가 Excel 시리얼 넘버로 저장 → 자동 변환
- 특수문자 이름: 직원명에 특수문자 포함 → 정상 처리
- 대용량: 5,000행 → 메모리 제한 내 처리 (스트리밍)
- BOM 있는 CSV: UTF-8 BOM → 자동 제거

### 데이터 무결성

- 동일 직원 같은 날짜 2건 동시 요청 (race condition): UNIQUE 제약으로 한 건만 성공
- 엑셀 업로드 중 직원 퇴직 처리: validate 시점 직원 상태 체크
- 급여 계산에 반영된 근태 데이터 수정: 경고만 (차단하지 않음)

---

## 회귀 테스트

| 기존 기능 | 영향 여부 | 검증 방법 |
|-----------|-----------|-----------|
| F-03 직원 관리 | 낮음 — work_records FK 참조 | 직원 삭제 시 CASCADE 동작 확인, 직원 목록 API 정상 |
| F-05 급여 계산 | 없음 — 읽기 전용 연동 | 급여 계산 API 기존 테스트 49건 전체 통과 |
| F-07 급여명세서 | 없음 — 직접 연동 없음 | payslips API 기존 테스트 통과 |
| F-10 컴플라이언스 | 낮음 — 근태 미등록 감점 가능 | 컴플라이언스 스코어 계산 기존 테스트 통과 |

---

## 테스트 파일 구조

```
backend/tests/
  ├── unit/
  │   ├── test_attendance_calculation.py    # U-01 ~ U-12
  │   └── test_excel_import.py             # U-20 ~ U-33
  └── api/
      └── test_attendance_api.py           # I-01 ~ I-84
```

---

## 테스트 데이터 요구사항

### Fixtures

- `company_with_employees`: 사업장 1개 + 직원 5명 (정규직 3, 파트타임 1, 계약직 1)
- `work_records_march_2026`: 직원 5명의 2026년 3월 근무 기록 (22일치)
  - 정상 근무, 연장근무, 야간근무, 휴일근무, 지각, 조퇴 케이스 포함
- `sample_xlsx_file`: 테스트용 엑셀 파일 (정상 데이터)
- `sample_csv_file`: 테스트용 CSV 파일 (정상 데이터)
- `error_xlsx_file`: 에러 포함 엑셀 파일 (행 12, 25에 오류)
- `duplicate_name_company`: 동명이인(김철수 2명) 포함 사업장

### 환경

- 테스트 DB에 work_records UNIQUE 인덱스 적용 확인
- openpyxl 설치 확인 (requirements.txt)
- 파일 업로드 테스트 시 TestClient multipart 지원
