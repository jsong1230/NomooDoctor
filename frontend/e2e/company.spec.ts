/**
 * F-02 사업장 관리 — E2E 테스트 (RED)
 *
 * 이 파일은 구현 전 실패하는 테스트입니다.
 * 실제 구현은 frontend-dev 에이전트가 수행합니다.
 */

import { test, expect } from '@playwright/test';

test.describe('사업장 관리', () => {
  let authCookies: string[];

  test.beforeEach(async ({ page, context }) => {
    // 로그인
    await page.goto('/login');
    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="password"]', 'TestP@ss123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL('/dashboard');

    // 인증 쿠키 저장
    authCookies = (await context.cookies()).map(c => `${c.name}=${c.value}`);
  });

  test.describe('사업장 등록 플로우', () => {
    test('사업장 등록 플로우 전체', async ({ page }) => {
      // 1. 사업장 등록 페이지 접속
      await page.goto('/company/new');
      await expect(page.locator('h1')).toContainText('사업장 등록');

      // 2. 폼 필드 확인
      await expect(page.locator('[name="business_name"]')).toBeVisible();
      await expect(page.locator('[name="business_number"]')).toBeVisible();
      await expect(page.locator('[name="representative_name"]')).toBeVisible();
      await expect(page.locator('[name="industry_type"]')).toBeVisible();
      await expect(page.locator('[name="employee_count"]')).toBeVisible();

      // 3. 사업장 정보 입력
      await page.fill('[name="business_name"]', '테스트사업장');
      await page.fill('[name="business_number"]', '123-45-67890');
      await page.fill('[name="representative_name"]', '홍길동');
      await page.selectOption('[name="industry_type"]', 'it');
      await page.fill('[name="employee_count"]', '5');

      // 4. 제출
      await page.click('button[type="submit"]');

      // 5. 대시보드로 리다이렉트 확인
      await expect(page).toHaveURL('/dashboard');

      // 6. 등록한 사업장명 표시 확인
      await expect(page.locator('text=테스트사업장')).toBeVisible();
    });

    test('사업자등록번호 실시간 검증', async ({ page }) => {
      await page.goto('/company/new');

      // 잘못된 형식 입력 (하이픈 없음)
      await page.fill('[name="business_number"]', '1234567890');
      await page.blur('[name="business_number"]');

      // 에러 메시지 확인
      await expect(page.locator('text=사업자등록번호 형식')).toBeVisible();

      // 올바른 형식으로 수정
      await page.fill('[name="business_number"]', '123-45-67890');
      await page.blur('[name="business_number"]');

      // 에러 메시지 사라짐 확인
      await expect(page.locator('text=사업자등록번호 형식')).not.toBeVisible();
    });

    test('업종 선택', async ({ page }) => {
      await page.goto('/company/new');

      // 업종 드롭다운 확인
      const industrySelect = page.locator('[name="industry_type"]');
      await expect(industrySelect).toBeVisible();

      // 8개 업종 옵션 확인
      const options = await industrySelect.locator('option').allTextContents();
      expect(options).toContainEqual('제조업');
      expect(options).toContainEqual('요식업');
      expect(options).toContainEqual('소매업');
      expect(options).toContainEqual('서비스업');
      expect(options).toContainEqual('IT/정보통신');
      expect(options).toContainEqual('건설업');
      expect(options).toContainEqual('의료업');
      expect(options).toContainEqual('기타');
    });

    test('필수 필드 누락 시 제출 불가', async ({ page }) => {
      await page.goto('/company/new');

      // 사업장명만 입력
      await page.fill('[name="business_name"]', '테스트사업장');

      // 제출 버튼 확인
      const submitButton = page.locator('button[type="submit"]');
      await expect(submitButton).toBeVisible();

      // 필수 필드 누락 시 제출 버튼 비활성화 또는 에러
      await submitButton.click();

      // 에러 메시지 또는 제출 방지 확인
      await expect(page.locator('text=필수 항목')).toBeVisible();
    });
  });

  test.describe('10인 이상 사업장 등록 플로우', () => {
    test('10인 이상 사업장 등록 시 취업규칙 안내', async ({ page }) => {
      await page.goto('/company/new');

      // 15인 사업장 등록
      await page.fill('[name="business_name"]', '중견기업');
      await page.fill('[name="business_number"]', '987-65-43210');
      await page.fill('[name="representative_name"]', '김대표');
      await page.selectOption('[name="industry_type"]', 'manufacturing');
      await page.fill('[name="employee_count"]', '15');

      await page.click('button[type="submit"]');

      // 대시보드로 이동
      await expect(page).toHaveURL('/dashboard');

      // 취업규칙 작성 안내 배너 확인
      await expect(page.locator('text=취업규칙')).toBeVisible();
      await expect(page.locator('text=10인 이상 사업장은 취업규칙 작성이 의무입니다')).toBeVisible();

      // 취업규칙 작성 버튼 확인
      await expect(page.locator('text=취업규칙 작성하기')).toBeVisible();

      // 취업규칙 작성 버튼 클릭
      await page.click('text=취업규칙 작성하기');

      // 취업규칙 페이지로 리다이렉트 확인
      await expect(page).toHaveURL(/.*work-rules.*/);
    });

    test('9인 사업장 등록 시 취업규칙 안내 미표시', async ({ page }) => {
      await page.goto('/company/new');

      // 9인 사업장 등록
      await page.fill('[name="business_name"]', '소기업');
      await page.fill('[name="business_number"]', '123-45-67890');
      await page.fill('[name="representative_name"]', '홍길동');
      await page.selectOption('[name="industry_type"]', 'it');
      await page.fill('[name="employee_count"]', '9');

      await page.click('button[type="submit"]');

      // 대시보드로 이동
      await expect(page).toHaveURL('/dashboard');

      // 취업규칙 안내 배너 미표시
      await expect(page.locator('text=취업규칙')).not.toBeVisible();
    });
  });

  test.describe('다중 사업장 전환', () => {
    test.beforeEach(async ({ page }) => {
      // 첫 번째 사업장 등록
      await page.goto('/company/new');
      await page.fill('[name="business_name"]', '첫번째사업장');
      await page.fill('[name="business_number"]', '111-22-33333');
      await page.fill('[name="representative_name"]', '홍길동');
      await page.selectOption('[name="industry_type"]', 'it');
      await page.fill('[name="employee_count"]', '5');
      await page.click('button[type="submit"]');
      await expect(page).toHaveURL('/dashboard');

      // 두 번째 사업장 등록
      await page.goto('/company/new');
      await page.fill('[name="business_name"]', '두번째사업장');
      await page.fill('[name="business_number"]', '222-33-44444');
      await page.fill('[name="representative_name"]', '김철수');
      await page.selectOption('[name="industry_type"]', 'manufacturing');
      await page.fill('[name="employee_count"]', '15');
      await page.click('button[type="submit"]');
      await expect(page).toHaveURL('/dashboard');
    });

    test('사업장 선택 드롭다운 표시', async ({ page }) => {
      // 사업장 선택 드롭다운 확인
      const selector = page.locator('[data-testid="company-selector"]');
      await expect(selector).toBeVisible();
      await expect(selector).toContainText('첫번째사업장');

      // 드롭다운 클릭
      await selector.click();

      // 등록된 사업장 목록 표시
      await expect(page.locator('text=첫번째사업장')).toBeVisible();
      await expect(page.locator('text=두번째사업장')).toBeVisible();
    });

    test('다른 사업장 선택 시 토큰 재발급 및 UI 갱신', async ({ page }) => {
      // 현재 사업장명 확인
      await expect(page.locator('text=두번째사업장')).toBeVisible();

      // 사업장 선택 드롭다운 클릭
      await page.click('[data-testid="company-selector"]');

      // 다른 사업장 선택
      await page.click('text=첫번째사업장');

      // UI 갱신 확인
      await expect(page.locator('text=첫번째사업장')).toBeVisible();
      await expect(page.locator('text=두번째사업장')).not.toBeVisible();

      // 페이지 새로고침
      await page.reload();

      // 선택한 사업장 컨텍스트 유지 확인
      await expect(page.locator('text=첫번째사업장')).toBeVisible();
    });

    test('API 요청 시 선택한 사업장 데이터 조회', async ({ page }) => {
      // 사업장 선택
      await page.click('[data-testid="company-selector"]');
      await page.click('text=첫번째사업장');

      // 대시보드 데이터 로드 대기
      await page.waitForLoadState('networkidle');

      // 첫번째 사업장 데이터 표시 확인
      await expect(page.locator('text=첫번째사업장')).toBeVisible();
    });
  });

  test.describe('사업장 수정', () => {
    test.beforeEach(async ({ page }) => {
      // 9인 사업장 등록
      await page.goto('/company/new');
      await page.fill('[name="business_name"]', '성장기업');
      await page.fill('[name="business_number"]', '123-45-67890');
      await page.fill('[name="representative_name"]', '홍길동');
      await page.selectOption('[name="industry_type"]', 'it');
      await page.fill('[name="employee_count"]', '9');
      await page.click('button[type="submit"]');
      await expect(page).toHaveURL('/dashboard');
    });

    test('직원 수 증가로 취업규칙 의무화', async ({ page }) => {
      // 사업장 상세 페이지 접속
      await page.click('[data-testid="company-card"]:first-child');

      // 수정 버튼 클릭
      await page.click('text=수정');

      // 직원 수를 15로 수정
      await page.fill('[name="employee_count"]', '15');

      // 저장
      await page.click('button[type="submit"]');

      // 취업규칙 작성 안내 모달 표시
      await expect(page.locator('text=취업규칙 작성이 필요합니다')).toBeVisible();

      // work_rule_required 확인 (상세 페이지에서)
      await page.click('text=확인');

      // 상세 페이지에서 work_rule_required 확인
      await expect(page.locator('text=취업규칙 의무')).toBeVisible();
    });

    test('직원 수 감소로 취업규칙 의무 해제', async ({ page }) => {
      // 15인 사업장 등록
      await page.goto('/company/new');
      await page.fill('[name="business_name"]', '축소기업');
      await page.fill('[name="business_number"]', '987-65-43210');
      await page.fill('[name="representative_name"]', '김대표');
      await page.selectOption('[name="industry_type"]', 'manufacturing');
      await page.fill('[name="employee_count"]', '15');
      await page.click('button[type="submit"]');

      // 사업장 상세 페이지 접속
      await page.click('[data-testid="company-card"]:last-child');

      // 수정 버튼 클릭
      await page.click('text=수정');

      // 직원 수를 5로 수정
      await page.fill('[name="employee_count"]', '5');

      // 저장
      await page.click('button[type="submit"]');

      // 취업규칙 의무 해제 확인
      await expect(page.locator('text=취업규칙 의무')).not.toBeVisible();
    });

    test('사업자등록번호 수정 불가', async ({ page }) => {
      // 사업장 상세 페이지 접속
      await page.click('[data-testid="company-card"]:first-child');

      // 수정 버튼 클릭
      await page.click('text=수정');

      // 사업자등록번호 필드 확인 (비활성화되어야 함)
      const businessNumberField = page.locator('[name="business_number"]');
      await expect(businessNumberField).toBeDisabled();
    });

    test('사업장명 수정 성공', async ({ page }) => {
      // 사업장 상세 페이지 접속
      await page.click('[data-testid="company-card"]:first-child');

      // 수정 버튼 클릭
      await page.click('text=수정');

      // 사업장명 수정
      await page.fill('[name="business_name"]', '바뀐사업장명');

      // 저장
      await page.click('button[type="submit"]');

      // 수정된 사업장명 표시 확인
      await expect(page.locator('text=바뀐사업장명')).toBeVisible();
      await expect(page.locator('text=성장기업')).not.toBeVisible();
    });
  });

  test.describe('사업장 삭제', () => {
    test.beforeEach(async ({ page }) => {
      // 사업장 등록
      await page.goto('/company/new');
      await page.fill('[name="business_name"]', '삭제될사업장');
      await page.fill('[name="business_number"]', '999-99-99999');
      await page.fill('[name="representative_name"]', '홍길동');
      await page.selectOption('[name="industry_type"]', 'it');
      await page.fill('[name="employee_count"]', '5');
      await page.click('button[type="submit"]');
      await expect(page).toHaveURL('/dashboard');
    });

    test('사업장 삭제 플로우', async ({ page }) => {
      // 사업장 상세 페이지 접속
      await page.click('[data-testid="company-card"]:first-child');

      // 삭제 버튼 클릭
      await page.click('text=삭제');

      // 확인 모달 표시
      await expect(page.locator('[data-testid="delete-confirm-modal"]')).toBeVisible();
      await expect(page.locator('text=정말로 이 사업장을 삭제하시겠습니까?')).toBeVisible();

      // 확인 문구 입력 요구
      await expect(page.locator('[placeholder="사업장명을 입력하세요"]')).toBeVisible();

      // 잘못된 문구 입력
      await page.fill('[placeholder="사업장명을 입력하세요"]', '잘못된문구');

      // 삭제 버튼 비활성화 확인
      const deleteButton = page.locator('button:has-text("삭제")');
      await expect(deleteButton).toBeDisabled();

      // 올바른 문구 입력
      await page.fill('[placeholder="사업장명을 입력하세요"]', '삭제될사업장');

      // 삭제 버튼 활성화 확인
      await expect(deleteButton).toBeEnabled();

      // 삭제 실행
      await deleteButton.click();

      // 30일 복구 가능 안내 토스트 표시
      await expect(page.locator('text=30일 이내에 복구 가능합니다')).toBeVisible();

      // 대시보드로 리다이렉트
      await expect(page).toHaveURL('/dashboard');

      // 삭제된 사업장 목록에서 제외
      await expect(page.locator('text=삭제될사업장')).not.toBeVisible();
    });

    test('삭제 확인 문구 불일치 시 삭제 불가', async ({ page }) => {
      // 사업장 상세 페이지 접속
      await page.click('[data-testid="company-card"]:first-child');

      // 삭제 버튼 클릭
      await page.click('text=삭제');

      // 잘못된 문구 입력
      await page.fill('[placeholder="사업장명을 입력하세요"]', '틀린사업장명');

      // 삭제 버튼 클릭 (비활성화 상태이므로 클릭 불가)
      const deleteButton = page.locator('button:has-text("삭제")');
      await expect(deleteButton).toBeDisabled();
    });

    test('취소 버튼 클릭 시 모달 닫기', async ({ page }) => {
      // 사업장 상세 페이지 접속
      await page.click('[data-testid="company-card"]:first-child');

      // 삭제 버튼 클릭
      await page.click('text=삭제');

      // 모달 표시 확인
      await expect(page.locator('[data-testid="delete-confirm-modal"]')).toBeVisible();

      // 취소 버튼 클릭
      await page.click('button:has-text("취소")');

      // 모달 닫힘 확인
      await expect(page.locator('[data-testid="delete-confirm-modal"]')).not.toBeVisible();
    });
  });

  test.describe('사업장 목록', () => {
    test.beforeEach(async ({ page }) => {
      // 여러 사업장 등록
      const companies = [
        { name: '제조업체', number: '111-22-33333', type: 'manufacturing', count: 20 },
        { name: '식당', number: '222-33-44444', type: 'food_service', count: 3 },
        { name: '편의점', number: '333-44-55555', type: 'retail', count: 2 },
      ];

      for (const company of companies) {
        await page.goto('/company/new');
        await page.fill('[name="business_name"]', company.name);
        await page.fill('[name="business_number"]', company.number);
        await page.fill('[name="representative_name"]', '홍길동');
        await page.selectOption('[name="industry_type"]', company.type);
        await page.fill('[name="employee_count"]', company.count.toString());
        await page.click('button[type="submit"]');
        await expect(page).toHaveURL('/dashboard');
      }
    });

    test('사업장 목록 표시', async ({ page }) => {
      // 대시보드에서 사업장 목록 확인
      await expect(page.locator('[data-testid="company-card"]')).toHaveCount(3);
      await expect(page.locator('text=제조업체')).toBeVisible();
      await expect(page.locator('text=식당')).toBeVisible();
      await expect(page.locator('text=편의점')).toBeVisible();
    });

    test('취업규칙 의무 사업장 표시', async ({ page }) => {
      // 10인 이상 사업장에 취업규칙 의무 표시
      const manufacturingCard = page.locator('[data-testid="company-card"]').filter({ hasText: '제조업체' });
      await expect(manufacturingCard.locator('text=취업규칙 의무')).toBeVisible();

      // 10인 미만 사업장에는 취업규칙 의무 미표시
      const restaurantCard = page.locator('[data-testid="company-card"]').filter({ hasText: '식당' });
      await expect(restaurantCard.locator('text=취업규칙 의무')).not.toBeVisible();
    });

    test('사업장 카드 클릭 시 상세 페이지 이동', async ({ page }) => {
      // 사업장 카드 클릭
      await page.click('[data-testid="company-card"]:first-child');

      // 상세 페이지로 이동 확인
      await expect(page).toHaveURL(/\/company\/.+/);
      await expect(page.locator('h1')).toContainText('사업장 상세');
    });
  });

  test.describe('보안 테스트', () => {
    test('인증 없이 사업장 등록 페이지 접근 불가', async ({ page }) => {
      // 로그아웃
      await page.click('[data-testid="logout-button"]');

      // 사업장 등록 페이지 접근 시도
      await page.goto('/company/new');

      // 로그인 페이지로 리다이렉트
      await expect(page).toHaveURL('/login');
    });

    test('인증 없이 사업장 상세 페이지 접근 불가', async ({ page }) => {
      // 로그아웃
      await page.click('[data-testid="logout-button"]');

      // 사업장 상세 페이지 접근 시도
      await page.goto('/company/123e4567-e89b-12d3-a456-426614174000');

      // 로그인 페이지로 리다이렉트
      await expect(page).toHaveURL('/login');
    });
  });

  test.describe('반응형 디자인', () => {
    test('모바일 화면에서 사업장 등록', async ({ page }) => {
      // 모바일 화면 크기 설정
      await page.setViewportSize({ width: 375, height: 667 });

      await page.goto('/company/new');

      // 모바일용 레이아웃 확인
      await expect(page.locator('h1')).toContainText('사업장 등록');
      await expect(page.locator('[name="business_name"]')).toBeVisible();

      // 폼 입력 및 제출
      await page.fill('[name="business_name"]', '모바일사업장');
      await page.fill('[name="business_number"]', '123-45-67890');
      await page.fill('[name="representative_name"]', '홍길동');
      await page.selectOption('[name="industry_type"]', 'it');
      await page.fill('[name="employee_count"]', '5');

      await page.click('button[type="submit"]');

      // 대시보드로 리다이렉트
      await expect(page).toHaveURL('/dashboard');
    });
  });
});
