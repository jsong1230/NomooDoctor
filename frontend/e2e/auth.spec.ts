/**
 * F-01 사용자 인증 — E2E 테스트 (RED)
 *
 * 이 파일은 구현 전 실패하는 테스트입니다.
 * 실제 구현은 frontend-dev 에이전트가 수행합니다.
 */

import { expect, test } from '@playwright/test';

/**
 * 회원가입 플로우 테스트
 */
test.describe('회원가입 플로우', () => {
  test('사용자가 정상적으로 회원가입하면 사업장 등록 페이지로 이동한다', async ({ page }) => {
    // Arrange: 회원가입 페이지 접속
    await page.goto('/register');

    // Act: 유효한 정보 입력 후 제출
    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="password"]', 'TestP@ss123');
    await page.fill('[name="name"]', '테스트사용자');
    await page.fill('[name="phone"]', '010-1234-5678');
    await page.click('button[type="submit"]');

    // Assert: 사업장 등록 페이지로 리다이렉트
    await expect(page).toHaveURL('/company/new');
    await expect(page.locator('h1')).toContainText('사업장 등록');
  });

  test('이미 등록된 이메일로 회원가입하면 에러 메시지가 표시된다', async ({ page }) => {
    // Arrange: 첫 번째 회원가입
    await page.goto('/register');
    await page.fill('[name="email"]', 'duplicate@example.com');
    await page.fill('[name="password"]', 'TestP@ss123');
    await page.fill('[name="name"]', '첫번째사용자');
    await page.fill('[name="phone"]', '010-1234-5678');
    await page.click('button[type="submit"]');

    // 동일 이메일로 두 번째 시도
    await page.goto('/register');
    await page.fill('[name="email"]', 'duplicate@example.com');
    await page.fill('[name="password"]', 'NewP@ss456');
    await page.fill('[name="name"]', '두번째사용자');
    await page.fill('[name="phone"]', '010-9876-5432');
    await page.click('button[type="submit"]');

    // Assert: 에러 메시지 표시
    await expect(page.locator('[data-testid="error-message"]')).toBeVisible();
    await expect(page.locator('[data-testid="error-message"]')).toContainText('E-3001');
  });

  test('비밀번호 정책을 위반하면 검증 에러가 표시된다', async ({ page }) => {
    await page.goto('/register');
    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="password"]', 'weak'); // 8자 미만
    await page.fill('[name="name"]', '테스트사용자');
    await page.fill('[name="phone"]', '010-1234-5678');
    await page.click('button[type="submit"]');

    // Assert: 비밀번호 검증 에러 표시
    await expect(page.locator('[data-testid="password-error"]')).toBeVisible();
    await expect(page.locator('[data-testid="password-error"]')).toContainText('8자 이상');
  });

  test('이메일 형식이 잘못되면 즉시 검증 에러가 표시된다', async ({ page }) => {
    await page.goto('/register');
    await page.fill('[name="email"]', 'invalid-email');
    await page.blur('[name="email"]');

    // Assert: 이메일 검증 에러 즉시 표시
    await expect(page.locator('[data-testid="email-error"]')).toBeVisible();
    await expect(page.locator('[data-testid="email-error"]')).toContainText('유효한 이메일');
  });
});

/**
 * 로그인 플로우 테스트
 */
test.describe('로그인 플로우', () => {
  test('사용자가 정상적으로 로그인하면 대시보드로 이동한다', async ({ page }) => {
    // Arrange: 로그인 페이지 접속
    await page.goto('/login');

    // Act: 이메일/비밀번호 입력 후 제출
    await page.fill('[name="email"]', 'login@example.com');
    await page.fill('[name="password"]', 'TestP@ss123');
    await page.click('button[type="submit"]');

    // Assert: 대시보드로 리다이렉트
    await expect(page).toHaveURL('/dashboard');
    await expect(page.locator('h1')).toContainText('대시보드');
  });

  test('잘못된 비밀번호로 로그인하면 에러 메시지가 표시된다', async ({ page }) => {
    await page.goto('/login');
    await page.fill('[name="email"]', 'login@example.com');
    await page.fill('[name="password"]', 'WrongP@ss456');
    await page.click('button[type="submit"]');

    // Assert: 에러 메시지 표시
    await expect(page.locator('[data-testid="error-message"]')).toBeVisible();
    await expect(page.locator('[data-testid="error-message"]')).toContainText('E-3003');
  });

  test('로그인 후 페이지 새로고침하면 로그인 상태가 유지된다', async ({ page }) => {
    // 로그인
    await page.goto('/login');
    await page.fill('[name="email"]', 'persist@example.com');
    await page.fill('[name="password"]', 'TestP@ss123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL('/dashboard');

    // 페이지 새로고침
    await page.reload();

    // Assert: 여전히 대시보드에 있음
    await expect(page).toHaveURL('/dashboard');
  });

  test('로그인 후 브라우저 종료 및 재시작 시 토큰 갱신으로 로그인 유지', async ({ page, context }) => {
    // 로그인
    await page.goto('/login');
    await page.fill('[name="email"]', 'refresh@example.com');
    await page.fill('[name="password"]', 'TestP@ss123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL('/dashboard');

    // 브라우저 세션 저장
    const storage = await context.storageState();

    // 새 컨텍스트로 세션 복원
    const newContext = await page.browser()?.newContext({ storageState });
    const newPage = await newContext?.newPage();
    if (!newPage) throw new Error('Failed to create new page');

    await newPage.goto('/');
    await expect(newPage).toHaveURL('/dashboard');

    await newContext?.close();
  });
});

/**
 * 카카오 OAuth 로그인 테스트
 */
test.describe('카카오 OAuth 로그인', () => {
  test('카카오 로그인 버튼 클릭 시 카카오 인증 페이지로 리다이렉트된다', async ({ page }) => {
    await page.goto('/login');

    // 카카오 로그인 버튼 클릭
    await page.click('[data-testid="kakao-login-button"]');

    // Assert: 카카오 인증 페이지 URL로 리다이렉트
    await expect(page).toHaveURL(/kauth\.kakao\.com/);
  });

  test('카카오 신규 회원 로그인 시 사업장 등록 페이지로 이동한다', async ({ page }) => {
    // 카카오 콜백 시뮬레이션
    await page.goto('/callback/kakao?code=test_code&state=test_state');

    // Assert: 신규 회원 시 사업장 등록 페이지로
    await expect(page).toHaveURL(/company\/new/);
  });

  test('카카오 기존 회원 로그인 시 대시보드로 이동한다', async ({ page }) => {
    // 기존 카카오 회원으로 설정
    // (테스트 데이터베이스에 미리 카카오 사용자 생성 필요)

    // 카카오 콜백 시뮬레이션
    await page.goto('/callback/kakao?code=existing_code&state=test_state');

    // Assert: 대시보드로 이동
    await expect(page).toHaveURL('/dashboard');
  });

  test('카카오 state 불일치 시 로그인 페이지로 에러와 함께 리다이렉트된다', async ({ page }) => {
    await page.goto('/callback/kakao?code=test_code&state=invalid_state');

    // Assert: 로그인 페이지로 에러와 함께 리다이렉트
    await expect(page).toHaveURL(/login\?error=E-2001/);
    await expect(page.locator('[data-testid="error-message"]')).toBeVisible();
  });
});

/**
 * 로그아웃 플로우 테스트
 */
test.describe('로그아웃 플로우', () => {
  test('로그아웃 시 로그인 페이지로 이동하고 토큰이 삭제된다', async ({ page }) => {
    // 로그인
    await page.goto('/login');
    await page.fill('[name="email"]', 'logout@example.com');
    await page.fill('[name="password"]', 'TestP@ss123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL('/dashboard');

    // 로그아웃
    await page.click('[data-testid="logout-button"]');

    // Assert: 로그인 페이지로 이동
    await expect(page).toHaveURL('/login');

    // 토큰이 localStorage에서 삭제되었는지 확인
    const accessToken = await page.evaluate(() => localStorage.getItem('access_token'));
    expect(accessToken).toBeNull();
  });

  test('로그아웃 후 뒤로가기 시도 시 로그인 페이지에 머문다', async ({ page }) => {
    // 로그인
    await page.goto('/login');
    await page.fill('[name="email"]', 'back@example.com');
    await page.fill('[name="password"]', 'TestP@ss123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL('/dashboard');

    // 로그아웃
    await page.click('[data-testid="logout-button"]');
    await expect(page).toHaveURL('/login');

    // 뒤로가기 시도
    await page.goBack();

    // Assert: 여전히 로그인 페이지에 있음
    await expect(page).toHaveURL('/login');
  });

  test('로그아웃된 토큰으로 API 요청 시 401 에러가 반환된다', async ({ page }) => {
    // 로그인
    await page.goto('/login');
    await page.fill('[name="email"]', 'api@example.com');
    await page.fill('[name="password"]', 'TestP@ss123');
    await page.click('button[type="submit"]');

    // 토큰 저장
    const token = await page.evaluate(() => localStorage.getItem('access_token'));

    // 로그아웃
    await page.click('[data-testid="logout-button"]');

    // 로그아웃된 토큰으로 API 요청 시도
    const response = await page.request.get('/api/v1/users/me', {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    // Assert: 401 에러
    expect(response.status()).toBe(401);
  });
});

/**
 * 토큰 자동 갱신 테스트
 */
test.describe('토큰 자동 갱신', () => {
  test('Access Token 만료 시 Refresh Token으로 자동 갱신된다', async ({ page }) => {
    // 로그인
    await page.goto('/login');
    await page.fill('[name="email"]', 'refresh@example.com');
    await page.fill('[name="password"]', 'TestP@ss123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL('/dashboard');

    // Access Token 만료 시뮬레이션 (만료된 토큰으로 교체)
    await page.evaluate(() => {
      localStorage.setItem('access_token', 'expired_token_here');
    });

    // API 요청 (자동 갱신 트리거)
    await page.reload();

    // Assert: 여전히 대시보드에 있음 (자동 갱신 성공)
    await expect(page).toHaveURL('/dashboard');

    // 토큰이 갱신되었는지 확인
    const newToken = await page.evaluate(() => localStorage.getItem('access_token'));
    expect(newToken).not.toBe('expired_token_here');
  });
});

/**
 * 비밀번호 재설정 테스트
 */
test.describe('비밀번호 재설정', () => {
  test('비밀번호 찾기 페이지에서 이메일 입력 후 재설정 링크 발송 메시지가 표시된다', async ({ page }) => {
    await page.goto('/forgot-password');
    await page.fill('[name="email"]', 'reset@example.com');
    await page.click('button[type="submit"]');

    // Assert: 성공 메시지 표시
    await expect(page.locator('[data-testid="success-message"]')).toBeVisible();
    await expect(page.locator('[data-testid="success-message"]')).toContainText('비밀번호 재설정 링크');
  });

  test('유효한 재설정 토큰으로 비밀번호 변경이 성공한다', async ({ page }) => {
    await page.goto('/reset-password?token=valid_token_here');
    await page.fill('[name="new_password"]', 'NewP@ss456');
    await page.fill('[name="confirm_password"]', 'NewP@ss456');
    await page.click('button[type="submit"]');

    // Assert: 로그인 페이지로 리다이렉트
    await expect(page).toHaveURL('/login');
    await expect(page.locator('[data-testid="success-message"]')).toBeVisible();
  });

  test('만료된 재설정 토큰으로 비밀번호 변경이 실패한다', async ({ page }) => {
    await page.goto('/reset-password?token=expired_token_here');
    await page.fill('[name="new_password"]', 'NewP@ss456');
    await page.fill('[name="confirm_password"]', 'NewP@ss456');
    await page.click('button[type="submit"]');

    // Assert: 에러 메시지 표시
    await expect(page.locator('[data-testid="error-message"]')).toBeVisible();
    await expect(page.locator('[data-testid="error-message"]')).toContainText('E-2002');
  });
});

/**
 * Rate Limiting 테스트
 */
test.describe('Rate Limiting', () => {
  test('로그인 5회 실패 후 6회째 시도 시 429 에러가 반환된다', async ({ page }) => {
    await page.goto('/login');

    // 5회 연속 로그인 실패
    for (let i = 0; i < 5; i++) {
      await page.fill('[name="email"]', 'ratelimit@example.com');
      await page.fill('[name="password"]', 'WrongP@ss456');
      await page.click('button[type="submit"]');
      await page.waitForTimeout(100); // 각 요청 사이 짧은 지연
    }

    // 6번째 시도
    await page.fill('[name="email"]', 'ratelimit@example.com');
    await page.fill('[name="password"]', 'WrongP@ss456');
    await page.click('button[type="submit"]');

    // Assert: Rate Limit 에러 표시
    await expect(page.locator('[data-testid="error-message"]')).toBeVisible();
    await expect(page.locator('[data-testid="error-message"]')).toContainText('E-2006');
    await expect(page.locator('[data-testid="error-message"]')).toContainText('요청 횟수를 초과했습니다');
  });

  test('Rate Limit 후 1분 대기 후 재시도 시 정상적으로 로그인된다', async ({ page }) => {
    // (실제 테스트에서는 타임머니풀레이션 사용 또는 TTL 축소 필요)
    await page.goto('/login');

    // 테스트를 위해 빠른 TTL 설정 필요
    // 이 테스트는 실제 구현 후 시간 조절 필요
  });
});

/**
 * 전체 사용자 온보딩 플로우
 */
test.describe('사용자 온보딩 플로우', () => {
  test('회원가입 → 사업장 등록 → 대시보드 전체 플로우', async ({ page }) => {
    // 1. 회원가입
    await page.goto('/register');
    await page.fill('[name="email"]', 'onboard@example.com');
    await page.fill('[name="password"]', 'TestP@ss123');
    await page.fill('[name="name"]', '온보딩사용자');
    await page.fill('[name="phone"]', '010-1234-5678');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL('/company/new');

    // 2. 사업장 등록
    await page.fill('[name="company_name"]', '테스트사업장');
    await page.fill('[name="business_number"]', '123-45-67890');
    await page.selectOption('[name="business_type"]', '서비스');
    await page.fill('[name="employee_count"]', '5');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL('/dashboard');

    // 3. 대시보드 확인
    await expect(page.locator('h1')).toContainText('대시보드');
    await expect(page.locator('[data-testid="user-name"]')).toContainText('온보딩사용자');
    await expect(page.locator('[data-testid="company-name"]')).toContainText('테스트사업장');
  });
});
