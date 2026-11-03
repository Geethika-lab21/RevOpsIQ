import { useEffect, useState } from 'react'

const API = 'http://127.0.0.1:8001/api'

async function fetchJson(path: string) {
  const response = await fetch(`${API}${path}`)
  if (!response.ok) throw new Error(`HTTP ${response.status} fetching ${path}`)
  return await response.json()
}

async function postJson(path: string, payload: Record<string, unknown>) {
  const response = await fetch(`${API}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  const result = await response.json()
  if (!response.ok) {
    throw new Error(typeof result.detail === 'string' ? result.detail : `HTTP ${response.status} posting ${path}`)
  }
  return result
}

const tabs = [
  'Overview',
  'Market Intelligence',
  'Accounts',
  'Sales Pipeline',
  'Customers & Adoption',
  'Business Reviews',
  'Actions',
  'Recommendations',
]

function formatCurrency(value: number) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0,
  }).format(value ?? 0)
}

function App() {
  const [activeTab, setActiveTab] = useState('Overview')
  const [overview, setOverview] = useState<any>({ kpis: {} })
  const [segments, setSegments] = useState<any[]>([])
  const [accounts, setAccounts] = useState<any[]>([])
  const [opportunities, setOpportunities] = useState<any[]>([])
  const [customers, setCustomers] = useState<any[]>([])
  const [reviews, setReviews] = useState<any[]>([])
  const [actions, setActions] = useState<any[]>([])
  const [recommendations, setRecommendations] = useState<any[]>([])
  const [healthScores, setHealthScores] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [segmentError, setSegmentError] = useState('')

  const refresh = async () => {
    setLoading(true)
    const [overviewData, segmentsData, accountsData, oppData, customerData, reviewData, actionsData, recData, healthData] = await Promise.all([
      fetchJson('/overview'),
      fetchJson('/segments'),
      fetchJson('/accounts'),
      fetchJson('/opportunities'),
      fetchJson('/customers'),
      fetchJson('/reviews'),
      fetchJson('/actions'),
      fetchJson('/recommendations'),
      fetchJson('/health-scores'),
    ])

    setOverview(overviewData)
    setSegments(segmentsData)
    setAccounts(accountsData)
    setOpportunities(oppData)
    setCustomers(customerData)
    setReviews(reviewData)
    setActions(actionsData)
    setRecommendations(recData)
    setHealthScores(healthData)
    setLoading(false)
  }

  useEffect(() => {
    refresh()
  }, [])

  const createSegment = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setSegmentError('')
    const formElement = event.currentTarget
    const form = new FormData(formElement)
    const payload = {
      name: form.get('name') ?? 'New segment',
      industry: form.get('industry') ?? 'Fintech',
      geography: form.get('geography') ?? 'North America',
      company_size_band: form.get('company_size_band') ?? 'Enterprise',
      use_case: form.get('use_case') ?? 'Risk monitoring',
      target_org_count: Number(form.get('target_org_count') ?? 0),
      score: Number(form.get('score') ?? 0),
      tam: Number(form.get('tam') ?? 0),
      sam: Number(form.get('sam') ?? 0),
      som: Number(form.get('som') ?? 0),
    }
    try {
      await postJson('/segments', payload)
    } catch (error) {
      setSegmentError(error instanceof Error ? error.message : 'Unable to create the market segment.')
      return
    }
    formElement.reset()
    await refresh()
  }

  const createAccount = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    const payload = {
      name: form.get('name') ?? 'New account',
      domain: form.get('domain') ?? '',
      industry: form.get('industry') ?? 'Finance',
      geography: form.get('geography') ?? 'NA',
      fit_score: Number(form.get('fit_score') ?? 0),
      status: form.get('status') ?? 'active',
      priority: form.get('priority') ?? 'medium',
    }
    await postJson('/accounts', payload)
    event.currentTarget.reset()
    refresh()
  }

  const createOpportunity = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    const payload = {
      account_id: Number(form.get('account_id') ?? 1),
      name: form.get('name') ?? 'New opportunity',
      stage: form.get('stage') ?? 'Qualified',
      value: Number(form.get('value') ?? 0),
      probability: Number(form.get('probability') ?? 0),
      next_step: form.get('next_step') ?? '',
    }
    await postJson('/opportunities', payload)
    event.currentTarget.reset()
    refresh()
  }

  const createAction = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    const payload = {
      title: form.get('title') ?? 'New action',
      description: form.get('description') ?? '',
      owner: form.get('owner') ?? 'Ops',
      priority: form.get('priority') ?? 'medium',
      due_date: form.get('due_date') ?? new Date().toISOString().slice(0,10),
    }
    await postJson('/actions', payload)
    event.currentTarget.reset()
    refresh()
  }

  const createCustomer = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    const payload = {
      account_id: Number(form.get('account_id') ?? 1),
      opportunity_id: Number(form.get('opportunity_id') || 0) || null,
      plan: form.get('plan') ?? 'Growth',
      recurring_value: Number(form.get('recurring_value') ?? 0),
      currency: form.get('currency') ?? 'USD',
      renewal_date: form.get('renewal_date') ?? new Date().toISOString().slice(0, 10),
      owner_id: Number(form.get('owner_id') || 0) || null,
      lifecycle: form.get('lifecycle') ?? 'Active',
    }
    await postJson('/customers', payload)
    event.currentTarget.reset()
    refresh()
  }

  const createReview = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    const payload = {
      title: form.get('title') ?? 'Quarterly review',
      period: form.get('period') ?? '2026-Q1',
      owner: form.get('owner') ?? 'Ops',
      status: form.get('status') ?? 'draft',
      summary: form.get('summary') ?? 'Review summary pending.',
    }
    await postJson('/reviews', payload)
    event.currentTarget.reset()
    refresh()
  }

  const createRecommendation = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    const payload = {
      rule_key: form.get('rule_key') ?? 'opportunity_health',
      entity_type: form.get('entity_type') ?? 'account',
      entity_id: Number(form.get('entity_id') ?? 0),
      title: form.get('title') ?? 'Recommendation',
      rationale: form.get('rationale') ?? 'Action recommended based on current signals.',
      evidence_json: JSON.stringify({ source: 'dashboard' }),
      severity: form.get('severity') ?? 'medium',
      status: form.get('status') ?? 'active',
    }
    await postJson('/recommendations', payload)
    event.currentTarget.reset()
    refresh()
  }

  const renderOverview = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-4">
        {[
          ['Open pipeline', overview?.kpis?.open_pipeline ?? 0, 'USD'],
          ['Weighted pipeline', overview?.kpis?.weighted_pipeline ?? 0, 'USD'],
          ['Closed-won value', overview?.kpis?.closed_won_value ?? 0, 'USD'],
          ['Active customers', overview?.kpis?.active_customers ?? 0, 'count'],
          ['Onboarding at risk', overview?.kpis?.onboarding_at_risk ?? 0, 'count'],
          ['Overdue actions', overview?.kpis?.overdue_actions ?? 0, 'count'],
        ].map(([label, value, unit]) => (
          <div key={label} className="card p-4">
            <div className="text-xs uppercase text-slate-400">{label}</div>
            <div className="mt-2 text-2xl font-semibold text-slate-900">
              {unit === 'count' ? value : formatCurrency(Number(value))}
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
        <div className="card p-4">
          <h3 className="text-lg font-semibold mb-4">Priority segments</h3>
          <div className="space-y-3">
            {segments.slice(0, 4).map((segment) => (
              <div key={segment.id} className="flex justify-between border-b pb-2 text-sm">
                <span>{segment.name}</span>
                <span className="font-medium">{segment.score}</span>
              </div>
            ))}
          </div>
        </div>
        <div className="card p-4">
          <h3 className="text-lg font-semibold mb-4">Top recommendations</h3>
          <div className="space-y-3">
            {recommendations.slice(0, 4).map((item) => (
              <div key={item.id} className="border-b pb-2 text-sm">
                <div className="font-medium">{item.title}</div>
                <div className="text-slate-500">{item.rationale}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
        <div className="card p-4">
          <h3 className="text-lg font-semibold mb-4">Pipeline by stage</h3>
          <div className="space-y-2">
            {['Target','Qualified','Discovery','Proposal','Negotiation'].map((stage) => {
              const total = opportunities.filter((op) => op.stage === stage).reduce((sum, op) => sum + Number(op.value || 0), 0)
              return (
                <div key={stage} className="flex items-center gap-3 text-sm">
                  <span className="w-28 text-slate-500">{stage}</span>
                  <div className="flex-1 h-2.5 rounded-full bg-slate-200">
                    <div className="h-full rounded-full bg-sky-500" style={{ width: `${Math.min(total / 300000 * 100, 100)}%` }} />
                  </div>
                  <span className="w-20 text-right font-medium">{formatCurrency(total)}</span>
                </div>
              )
            })}
          </div>
        </div>
        <div className="card p-4">
          <h3 className="text-lg font-semibold mb-4">Health distribution</h3>
          <div className="space-y-2">
            {healthScores.map((score) => (
              <div key={score.customer_id} className="flex justify-between text-sm border-b pb-2">
                <span>Customer {score.customer_id}</span>
                <span className="font-medium">{score.score}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )

  const renderSegments = () => (
    <div className="space-y-6">
      <div className="card p-4">
        <h3 className="text-lg font-semibold mb-4">Create market segment</h3>
        <form className="grid grid-cols-2 gap-3" onSubmit={createSegment} onChange={() => setSegmentError('')}>
          <input name="name" placeholder="Segment name" className="input" />
          <input name="industry" placeholder="Industry" className="input" />
          <input name="geography" placeholder="Geography" className="input" />
          <input name="company_size_band" placeholder="Company size" className="input" />
          <input name="use_case" placeholder="Use case" className="input" />
          <input name="target_org_count" type="number" placeholder="Target orgs" className="input" />
          <input name="score" type="number" placeholder="Score" className="input" />
          <input name="tam" type="number" placeholder="TAM" className="input" />
          <input name="sam" type="number" placeholder="SAM" className="input" />
          <input name="som" type="number" placeholder="SOM" className="input" />
          {segmentError && <p className="col-span-2 text-sm text-red-600" role="alert">{segmentError}</p>}
          <button type="submit" className="btn col-span-2">Save segment</button>
        </form>
      </div>

      <div className="card overflow-hidden">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-100">
            <tr>
              <th className="p-3">Segment</th>
              <th className="p-3">Industry</th>
              <th className="p-3">Geography</th>
              <th className="p-3">Score</th>
              <th className="p-3">TAM</th>
            </tr>
          </thead>
          <tbody>
            {segments.map((segment) => (
              <tr key={segment.id} className="border-b">
                <td className="p-3">{segment.name}</td>
                <td className="p-3">{segment.industry}</td>
                <td className="p-3">{segment.geography}</td>
                <td className="p-3">{segment.score}</td>
                <td className="p-3">{formatCurrency(segment.tam || 0)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )

  const renderAccounts = () => (
    <div className="space-y-6">
      <div className="card p-4">
        <h3 className="text-lg font-semibold mb-4">Create account</h3>
        <form className="grid grid-cols-2 gap-3" onSubmit={createAccount}>
          <input name="name" placeholder="Account name" className="input" />
          <input name="domain" placeholder="Domain" className="input" />
          <input name="industry" placeholder="Industry" className="input" />
          <input name="geography" placeholder="Geography" className="input" />
          <input name="fit_score" type="number" placeholder="Fit score" className="input" />
          <input name="status" placeholder="Status" className="input" />
          <input name="priority" placeholder="Priority" className="input" />
          <button type="submit" className="btn col-span-2">Save account</button>
        </form>
      </div>

      <div className="card overflow-hidden">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-100">
            <tr>
              <th className="p-3">Account</th>
              <th className="p-3">Segment</th>
              <th className="p-3">Owner</th>
              <th className="p-3">Fit score</th>
              <th className="p-3">Status</th>
            </tr>
          </thead>
          <tbody>
            {accounts.map((account) => (
              <tr key={account.id} className="border-b">
                <td className="p-3">{account.name}</td>
                <td className="p-3">{account.segment}</td>
                <td className="p-3">{account.owner}</td>
                <td className="p-3">{account.fit_score}</td>
                <td className="p-3">{account.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )

  const renderPipeline = () => (
    <div className="space-y-6">
      <div className="card p-4">
        <h3 className="text-lg font-semibold mb-4">Create opportunity</h3>
        <form className="grid grid-cols-2 gap-3" onSubmit={createOpportunity}>
          <input name="account_id" type="number" placeholder="Account ID" className="input" />
          <input name="name" placeholder="Opportunity name" className="input" />
          <input name="stage" placeholder="Stage" className="input" />
          <input name="value" type="number" placeholder="Value" className="input" />
          <input name="probability" type="number" placeholder="Probability" className="input" />
          <input name="next_step" placeholder="Next step" className="input" />
          <button type="submit" className="btn col-span-2">Save opportunity</button>
        </form>
      </div>

      <div className="card overflow-hidden">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-100">
            <tr>
              <th className="p-3">Account</th>
              <th className="p-3">Stage</th>
              <th className="p-3">Value</th>
              <th className="p-3">Probability</th>
              <th className="p-3">Weighted</th>
            </tr>
          </thead>
          <tbody>
            {opportunities.map((opp) => (
              <tr key={opp.id} className="border-b">
                <td className="p-3">{opp.account}</td>
                <td className="p-3">{opp.stage}</td>
                <td className="p-3">{formatCurrency(opp.value || 0)}</td>
                <td className="p-3">{opp.probability}%</td>
                <td className="p-3">{formatCurrency(opp.weighted_value || 0)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )

  const renderCustomers = () => (
    <div className="space-y-6">
      <div className="card p-4">
        <h3 className="text-lg font-semibold mb-4">Add customer</h3>
        <form className="grid grid-cols-2 gap-3" onSubmit={createCustomer}>
          <input name="account_id" type="number" placeholder="Account ID" className="input" />
          <input name="opportunity_id" type="number" placeholder="Opportunity ID" className="input" />
          <input name="plan" placeholder="Plan" className="input" />
          <input name="recurring_value" type="number" placeholder="Recurring value" className="input" />
          <input name="renewal_date" type="date" className="input" />
          <input name="lifecycle" placeholder="Lifecycle" className="input" />
          <button type="submit" className="btn col-span-2">Save customer</button>
        </form>
      </div>

      <div className="card p-4">
        <h3 className="text-lg font-semibold mb-4">Customer health snapshot</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {healthScores.map((customer) => (
            <div key={customer.customer_id} className="border rounded-lg p-3">
              <div className="flex justify-between font-medium"><span>Customer {customer.customer_id}</span><span>{customer.score}</span></div>
              <div className="mt-2 text-xs text-slate-500">{customer.band}</div>
              <div className="mt-3 text-sm">{JSON.stringify(customer.components)}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="card overflow-hidden">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-100">
            <tr>
              <th className="p-3">Customer</th>
              <th className="p-3">Plan</th>
              <th className="p-3">Lifecycle</th>
              <th className="p-3">Renewal</th>
              <th className="p-3">Revenue</th>
            </tr>
          </thead>
          <tbody>
            {customers.map((customer) => (
              <tr key={customer.id} className="border-b">
                <td className="p-3">{customer.name}</td>
                <td className="p-3">{customer.plan}</td>
                <td className="p-3">{customer.lifecycle}</td>
                <td className="p-3">{customer.renewal_date}</td>
                <td className="p-3">{formatCurrency(customer.recurring_value || 0)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )

  const renderReviews = () => (
    <div className="space-y-6">
      <div className="card p-4">
        <h3 className="text-lg font-semibold mb-4">Create business review</h3>
        <form className="grid grid-cols-2 gap-3" onSubmit={createReview}>
          <input name="title" placeholder="Review title" className="input" />
          <input name="period" placeholder="Period" className="input" />
          <input name="owner" placeholder="Owner" className="input" />
          <input name="status" placeholder="Status" className="input" />
          <textarea name="summary" placeholder="Summary" className="input col-span-2 min-h-24" />
          <button type="submit" className="btn col-span-2">Save review</button>
        </form>
      </div>

      <div className="card p-4">
        <h3 className="text-lg font-semibold mb-4">Business reviews</h3>
        <div className="space-y-3">
          {reviews.map((review) => (
            <div key={review.id} className="border rounded-lg p-3">
              <div className="font-medium">{review.title}</div>
              <div className="text-xs text-slate-500">{review.period} • {review.owner}</div>
              <div className="mt-2 text-sm">{review.summary}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )

  const renderActions = () => (
    <div className="space-y-6">
      <div className="card p-4">
        <h3 className="text-lg font-semibold mb-4">Create action</h3>
        <form className="grid grid-cols-2 gap-3" onSubmit={createAction}>
          <input name="title" placeholder="Action title" className="input" />
          <input name="owner" placeholder="Owner" className="input" />
          <input name="priority" placeholder="Priority" className="input" />
          <input name="due_date" type="date" className="input" />
          <textarea name="description" placeholder="Description" className="input col-span-2 min-h-24" />
          <button type="submit" className="btn col-span-2">Save action</button>
        </form>
      </div>

      <div className="card overflow-hidden">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-100">
            <tr>
              <th className="p-3">Action</th>
              <th className="p-3">Owner</th>
              <th className="p-3">Priority</th>
              <th className="p-3">Status</th>
            </tr>
          </thead>
          <tbody>
            {actions.map((action) => (
              <tr key={action.id} className="border-b">
                <td className="p-3">{action.title}</td>
                <td className="p-3">{action.owner}</td>
                <td className="p-3">{action.priority}</td>
                <td className="p-3">{action.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )

  const renderRecommendations = () => (
    <div className="space-y-6">
      <div className="card p-4">
        <h3 className="text-lg font-semibold mb-4">Create recommendation</h3>
        <form className="grid grid-cols-2 gap-3" onSubmit={createRecommendation}>
          <input name="rule_key" placeholder="Rule key" className="input" />
          <input name="entity_type" placeholder="Entity type" className="input" />
          <input name="entity_id" type="number" placeholder="Entity ID" className="input" />
          <input name="severity" placeholder="Severity" className="input" />
          <input name="title" placeholder="Title" className="input col-span-2" />
          <textarea name="rationale" placeholder="Rationale" className="input col-span-2 min-h-24" />
          <button type="submit" className="btn col-span-2">Save recommendation</button>
        </form>
      </div>

      <div className="card overflow-hidden">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-100">
            <tr>
              <th className="p-3">Title</th>
              <th className="p-3">Rule</th>
              <th className="p-3">Severity</th>
              <th className="p-3">Status</th>
            </tr>
          </thead>
          <tbody>
            {recommendations.map((rec) => (
              <tr key={rec.id} className="border-b">
                <td className="p-3">{rec.title}</td>
                <td className="p-3">{rec.rule_key}</td>
                <td className="p-3">{rec.severity}</td>
                <td className="p-3">{rec.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )

  const renderTab = () => {
    switch (activeTab) {
      case 'Overview': return renderOverview()
      case 'Market Intelligence': return renderSegments()
      case 'Accounts': return renderAccounts()
      case 'Sales Pipeline': return renderPipeline()
      case 'Customers & Adoption': return renderCustomers()
      case 'Business Reviews': return renderReviews()
      case 'Actions': return renderActions()
      case 'Recommendations': return renderRecommendations()
      default: return renderOverview()
    }
  }

  return (
    <div className="min-h-screen bg-slate-100 text-slate-800">
      <aside className="w-full border-b bg-slate-900 text-white">
        <div className="mx-auto max-w-7xl px-6 py-4 flex items-center justify-between">
          <div>
            <div className="text-2xl font-bold">RevOpsIQ</div>
            <div className="text-xs text-slate-300">Strategy & Revenue Operations Intelligence</div>
          </div>
          <button className="btn" onClick={refresh}>Refresh data</button>
        </div>
        <nav className="mx-auto max-w-7xl px-6 pb-3 flex flex-wrap gap-2">
          {tabs.map((tab) => (
            <button
              key={tab}
              className={`px-3 py-2 rounded-md text-sm ${activeTab === tab ? 'bg-sky-600 text-white' : 'bg-slate-800 text-slate-200'}`}
              onClick={() => setActiveTab(tab)}
            >
              {tab}
            </button>
          ))}
        </nav>
      </aside>

      <main className="mx-auto max-w-7xl px-6 py-8">
        {loading ? <div className="text-slate-500">Loading demo data…</div> : renderTab()}
      </main>
    </div>
  )
}

export default App
