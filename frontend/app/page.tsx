import Link from 'next/link'

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      {/* Header */}
      <header className="container mx-auto px-4 py-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-blue-900">노무닥터</h1>
          <div className="space-x-4">
            <Link href="/login" className="text-gray-600 hover:text-gray-900">
              로그인
            </Link>
            <Link
              href="/register"
              className="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
            >
              회원가입
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20">
        <div className="max-w-3xl">
          <h2 className="mb-6 text-5xl font-bold text-gray-900">
            AI 기반 노무/HR 자동화
          </h2>
          <p className="mb-8 text-xl text-gray-600">
            50인 미만 사업장 사장님을 위한 AI 노무 비서
            <br />
            노동법 Q&A, 근로계약서, 급여 계산을 자동으로
          </p>
          <Link
            href="/register"
            className="inline-block rounded-lg bg-blue-600 px-8 py-3 text-lg font-semibold text-white hover:bg-blue-700"
          >
            무료로 시작하기
          </Link>
        </div>
      </section>

      {/* Features Section */}
      <section className="container mx-auto px-4 py-16">
        <h3 className="mb-12 text-center text-3xl font-bold text-gray-900">
          핵심 기능
        </h3>
        <div className="grid gap-8 md:grid-cols-3">
          <FeatureCard
            title="AI 노동법 Q&A"
            description="자연어 질문으로 노동법 관련 즉각적인 답변 받기"
            icon="🤖"
          />
          <FeatureCard
            title="근로계약서 자동 생성"
            description="고용형태별 법적 유효한 계약서 자동 작성"
            icon="📄"
          />
          <FeatureCard
            title="급여 자동 계산기"
            description="주휴수당, 연장수당, 4대보험 완전 자동화"
            icon="💰"
          />
        </div>
      </section>

      {/* Pricing Section */}
      <section className="container mx-auto px-4 py-16">
        <h3 className="mb-12 text-center text-3xl font-bold text-gray-900">
          요금제
        </h3>
        <div className="grid gap-8 md:grid-cols-3">
          <PriceCard
            title="Free"
            price="0"
            features={[
              '월 10건 AI 상담',
              '최대 5명 직원 관리',
              '기본 템플릿',
            ]}
          />
          <PriceCard
            title="Standard"
            price="29,000"
            features={[
              '무제한 AI 상담',
              '최대 30명 직원 관리',
              '고급 템플릿',
              '노무사 연결',
            ]}
            highlighted
          />
          <PriceCard
            title="Premium"
            price="99,000"
            features={[
              '무제한 AI 상담',
              '최대 100명 직원 관리',
              '모든 템플릿',
              '노무사 1:1 상담',
              '전자서명',
            ]}
          />
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t bg-gray-50 py-8">
        <div className="container mx-auto px-4 text-center text-gray-600">
          <p>&copy; 2024 노무닥터. All rights reserved.</p>
        </div>
      </footer>
    </div>
  )
}

function FeatureCard({ title, description, icon }: { title: string; description: string; icon: string }) {
  return (
    <div className="rounded-lg border bg-white p-6 shadow-sm">
      <div className="mb-4 text-4xl">{icon}</div>
      <h4 className="mb-2 text-xl font-semibold text-gray-900">{title}</h4>
      <p className="text-gray-600">{description}</p>
    </div>
  )
}

function PriceCard({
  title,
  price,
  features,
  highlighted = false,
}: {
  title: string
  price: string
  features: string[]
  highlighted?: boolean
}) {
  return (
    <div
      className={`rounded-lg border p-6 shadow-sm ${
        highlighted ? 'border-blue-500 bg-blue-50' : 'bg-white'
      }`}
    >
      <h4 className="mb-2 text-xl font-semibold text-gray-900">{title}</h4>
      <p className="mb-6 text-3xl font-bold text-gray-900">
        ₩{price}
        <span className="text-lg font-normal text-gray-600">/월</span>
      </p>
      <ul className="mb-6 space-y-2">
        {features.map((feature) => (
          <li key={feature} className="flex items-center text-gray-600">
            <span className="mr-2 text-green-500">✓</span>
            {feature}
          </li>
        ))}
      </ul>
      <Link
        href="/register"
        className={`block rounded-lg px-4 py-2 text-center font-semibold ${
          highlighted
            ? 'bg-blue-600 text-white hover:bg-blue-700'
            : 'border border-gray-300 text-gray-900 hover:bg-gray-50'
        }`}
      >
        {price === '0' ? '무료로 시작' : '구독하기'}
      </Link>
    </div>
  )
}
