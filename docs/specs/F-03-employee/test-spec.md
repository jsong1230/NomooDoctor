# F-03 직원 관리 테스트 명세

## 1. API 통합 테스트

### TestCreateEmployeeAPI
- test_정상_직원_등록_성공
- test_인증_없이_등록_실패
- test_타인_사업장에_직원_등록_실패
- test_주민등록번호_형식_오류

### TestListEmployeesAPI
- test_정상_목록_조회_성공
- test_상태_필터_동작
- test_페이지네이션_동작

### TestGetEmployeeAPI
- test_정상_상세_조회_성공
- test_존재하지_않는_ID_조회_실패

### TestUpdateEmployeeAPI
- test_정상_수정_성공
- test_타인_직원_수정_실패

### TestResignEmployeeAPI
- test_정상_퇴직_처리
- test_이미_퇴직한_직원
