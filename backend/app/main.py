from __future__ import annotations

import json
import os
from datetime import date, datetime, timedelta
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import Boolean, Column, Date, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Session, relationship

from .database import Base, SessionLocal, engine, get_db

app = FastAPI(title="RevOpsIQ", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "http://127.0.0.1:5173").split(",")
        if origin.strip()
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(200), unique=True, nullable=False)
    role = Column(String(60), default="Strategy / Business Ops")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class MarketSegment(Base):
    __tablename__ = "market_segments"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    industry = Column(String(120), default="Fintech")
    geography = Column(String(120), default="North America")
    company_size_band = Column(String(80), default="Enterprise")
    use_case = Column(String(200), default="Risk monitoring")
    target_org_count = Column(Integer, default=0)
    urgency = Column(String(80), default="High")
    buying_complexity = Column(String(80), default="Moderate")
    notes = Column(Text, default="")
    status = Column(String(60), default="active")
    score = Column(Float, default=0.0)
    market_attractiveness = Column(Float, default=0.0)
    urgency_score = Column(Float, default=0.0)
    product_fit = Column(Float, default=0.0)
    accessibility = Column(Float, default=0.0)
    competitive_intensity = Column(Float, default=0.0)
    tam = Column(Float, default=0.0)
    sam = Column(Float, default=0.0)
    som = Column(Float, default=0.0)
    currency = Column(String(10), default="USD")
    sizing_method = Column(String(50), default="bottom-up")
    assumptions_json = Column(Text, default="{}")
    source_url = Column(String(300), default="")
    confidence = Column(Float, default=0.7)
    reviewed_at = Column(DateTime, default=datetime.utcnow)


class Competitor(Base):
    __tablename__ = "competitors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    website = Column(String(250), default="")
    category = Column(String(120), default="Platform")
    notes = Column(Text, default="")
    source_url = Column(String(250), default="")
    observation_date = Column(DateTime, default=datetime.utcnow)
    confidence = Column(Float, default=0.7)
    strengths = Column(Text, default="")
    weaknesses = Column(Text, default="")
    pricing_notes = Column(Text, default="")
    differentiators = Column(Text, default="")


class SegmentCompetitor(Base):
    __tablename__ = "segment_competitors"
    id = Column(Integer, primary_key=True, index=True)
    segment_id = Column(Integer, ForeignKey("market_segments.id"), nullable=False)
    competitor_id = Column(Integer, ForeignKey("competitors.id"), nullable=False)
    comparison_notes = Column(Text, default="")
    position = Column(String(80), default="Mid-market")


class ResearchSource(Base):
    __tablename__ = "research_sources"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    url = Column(String(400), default="")
    publisher = Column(String(120), default="")
    source_type = Column(String(60), default="web")
    observed_at = Column(DateTime, default=datetime.utcnow)
    confidence = Column(Float, default=0.7)
    notes = Column(Text, default="")


class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    domain = Column(String(200), default="")
    industry = Column(String(120), default="Finance")
    geography = Column(String(120), default="NA")
    segment_id = Column(Integer, ForeignKey("market_segments.id"), nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    fit_score = Column(Float, default=0.0)
    status = Column(String(60), default="active")
    priority = Column(String(50), default="medium")
    pain_point = Column(Text, default="")
    fit_notes = Column(Text, default="")
    source = Column(String(200), default="")
    reviewed_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    segment = relationship("MarketSegment")
    owner = relationship("User")
    contacts = relationship("Contact", back_populates="account")
    opportunities = relationship("Opportunity", back_populates="account")


class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    name = Column(String(120), nullable=False)
    title = Column(String(100), default="")
    department = Column(String(100), default="")
    email = Column(String(200), default="")
    notes = Column(Text, default="")
    source = Column(String(120), default="")
    account = relationship("Account", back_populates="contacts")


class Opportunity(Base):
    __tablename__ = "opportunities"
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    name = Column(String(200), nullable=False)
    stage = Column(String(80), default="Qualified")
    value = Column(Float, default=0.0)
    currency = Column(String(10), default="USD")
    probability = Column(Float, default=0.0)
    close_date = Column(Date, default=date.today)
    next_step = Column(String(200), default="")
    activity_date = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default="open")
    loss_reason = Column(String(200), default="")
    account = relationship("Account", back_populates="opportunities")
    owner = relationship("User")


class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    opportunity_id = Column(Integer, ForeignKey("opportunities.id"), nullable=True)
    start_date = Column(Date, default=date.today)
    plan = Column(String(120), default="Growth")
    recurring_value = Column(Float, default=0.0)
    currency = Column(String(10), default="USD")
    renewal_date = Column(Date, default=date.today)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    lifecycle = Column(String(50), default="Active")
    status = Column(String(50), default="active")
    account = relationship("Account")
    owner = relationship("User")


class OnboardingPlan(Base):
    __tablename__ = "onboarding_plans"
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    template = Column(String(120), default="Standard")
    status = Column(String(60), default="in_progress")
    start_date = Column(Date, default=date.today)
    target_go_live = Column(Date, default=date.today)


class OnboardingMilestone(Base):
    __tablename__ = "onboarding_milestones"
    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("onboarding_plans.id"), nullable=False)
    name = Column(String(140), nullable=False)
    owner = Column(String(120), default="Owner")
    due_date = Column(Date, default=date.today)
    status = Column(String(60), default="pending")
    completion_date = Column(Date, nullable=True)
    blocker = Column(Text, default="")
    notes = Column(Text, default="")


class AdoptionObservation(Base):
    __tablename__ = "adoption_observations"
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    period = Column(String(40), default="monthly")
    active_users = Column(Integer, default=0)
    feature_usage = Column(Float, default=0.0)
    frequency = Column(String(40), default="weekly")
    source = Column(String(80), default="manual")
    created_at = Column(DateTime, default=datetime.utcnow)


class CustomerHealthSnapshot(Base):
    __tablename__ = "customer_health_snapshots"
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    score = Column(Float, default=0.0)
    band = Column(String(40), default="Monitoring")
    components_json = Column(Text, default="{}")
    calculated_at = Column(DateTime, default=datetime.utcnow)


class CustomerRisk(Base):
    __tablename__ = "customer_risks"
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    type = Column(String(80), default="Adoption")
    severity = Column(String(40), default="Medium")
    description = Column(Text, default="")
    owner = Column(String(120), default="CS")
    mitigation = Column(Text, default="")
    status = Column(String(50), default="open")


class CostRecord(Base):
    __tablename__ = "cost_records"
    id = Column(Integer, primary_key=True, index=True)
    period = Column(String(40), default="2026-Q1")
    category = Column(String(80), default="Customer acquisition")
    amount = Column(Float, default=0.0)
    currency = Column(String(10), default="USD")
    segment_id = Column(Integer, ForeignKey("market_segments.id"), nullable=True)
    notes = Column(Text, default="")


class BusinessTarget(Base):
    __tablename__ = "business_targets"
    id = Column(Integer, primary_key=True, index=True)
    metric_key = Column(String(120), default="revenue")
    period = Column(String(40), default="2026-Q1")
    target = Column(Float, default=0.0)
    currency = Column(String(10), default="USD")
    segment_id = Column(Integer, ForeignKey("market_segments.id"), nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)


class BusinessReview(Base):
    __tablename__ = "business_reviews"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    period = Column(String(40), default="2026-Q1")
    owner = Column(String(120), default="Ops")
    status = Column(String(60), default="draft")
    summary = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)


class ReviewKpiSnapshot(Base):
    __tablename__ = "review_kpi_snapshots"
    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, ForeignKey("business_reviews.id"), nullable=False)
    metric_key = Column(String(120), default="revenue")
    actual = Column(Float, default=0.0)
    target = Column(Float, default=0.0)
    variance = Column(Float, default=0.0)
    snapshot_at = Column(DateTime, default=datetime.utcnow)


class Decision(Base):
    __tablename__ = "decisions"
    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, ForeignKey("business_reviews.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, default="")
    owner = Column(String(120), default="Ops")
    date = Column(Date, default=date.today)
    status = Column(String(50), default="open")


class ActionItem(Base):
    __tablename__ = "action_items"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, default="")
    owner = Column(String(120), default="Ops")
    priority = Column(String(40), default="medium")
    due_date = Column(Date, default=date.today)
    status = Column(String(40), default="open")
    linked_entity_type = Column(String(80), default="segment")
    linked_entity_id = Column(Integer, default=0)
    completion_notes = Column(Text, default="")
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Recommendation(Base):
    __tablename__ = "recommendations"
    id = Column(Integer, primary_key=True, index=True)
    rule_key = Column(String(120), default="opportunity_health")
    entity_type = Column(String(60), default="account")
    entity_id = Column(Integer, default=0)
    title = Column(String(200), nullable=False)
    rationale = Column(Text, default="")
    evidence_json = Column(Text, default="{}")
    severity = Column(String(50), default="medium")
    status = Column(String(40), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    actor = Column(String(120), default="system")
    entity = Column(String(120), default="record")
    action = Column(String(120), default="create")
    before_json = Column(Text, default="{}")
    after_json = Column(Text, default="{}")
    timestamp = Column(DateTime, default=datetime.utcnow)


class SegmentCreate(BaseModel):
    name: str
    industry: str = "Fintech"
    geography: str = "North America"
    company_size_band: str = "Enterprise"
    use_case: str = "Risk monitoring"
    target_org_count: int = 0
    urgency: str = "High"
    buying_complexity: str = "Moderate"
    notes: str = ""
    status: str = "active"
    score: float = 0.0
    market_attractiveness: float = 0.0
    urgency_score: float = 0.0
    product_fit: float = 0.0
    accessibility: float = 0.0
    competitive_intensity: float = 0.0
    tam: float = 0.0
    sam: float = 0.0
    som: float = 0.0
    currency: str = "USD"
    sizing_method: str = "bottom-up"
    assumptions_json: str = "{}"
    source_url: str = ""
    confidence: float = 0.7


class AccountCreate(BaseModel):
    name: str
    domain: str = ""
    industry: str = "Finance"
    geography: str = "NA"
    segment_id: Optional[int] = None
    owner_id: Optional[int] = None
    fit_score: float = 0.0
    status: str = "active"
    priority: str = "medium"
    pain_point: str = ""
    fit_notes: str = ""
    source: str = ""


class OpportunityCreate(BaseModel):
    account_id: int
    owner_id: Optional[int] = None
    name: str
    stage: str = "Qualified"
    value: float = 0.0
    currency: str = "USD"
    probability: float = 0.0
    close_date: Optional[str] = None
    next_step: str = ""
    status: str = "open"


class CustomerCreate(BaseModel):
    account_id: int
    opportunity_id: Optional[int] = None
    plan: str = "Growth"
    recurring_value: float = 0.0
    currency: str = "USD"
    renewal_date: Optional[str] = None
    owner_id: Optional[int] = None
    lifecycle: str = "Active"


class ActionCreate(BaseModel):
    title: str
    description: str = ""
    owner: str = "Ops"
    priority: str = "medium"
    due_date: Optional[str] = None
    status: str = "open"
    linked_entity_type: str = "segment"
    linked_entity_id: int = 0


class ReviewCreate(BaseModel):
    title: str
    period: str = "2026-Q1"
    owner: str = "Ops"
    status: str = "draft"
    summary: str = ""


class RecommendationCreate(BaseModel):
    rule_key: str = "opportunity_health"
    entity_type: str = "account"
    entity_id: int = 0
    title: str
    rationale: str = ""
    evidence_json: str = "{}"
    severity: str = "medium"
    status: str = "active"


Base.metadata.create_all(bind=engine)


def seed_demo_data(db: Session) -> None:
    if db.query(User).count() > 0:
        return

    admin = User(name="Ava Admin", email="admin@revopsiq.demo", role="Admin")
    sales = User(name="Marcus Sales", email="sales@revopsiq.demo", role="Sales")
    cs = User(name="Nina Success", email="cs@revopsiq.demo", role="Customer Success")
    db.add_all([admin, sales, cs])
    db.flush()

    seg_1 = MarketSegment(
        name="Digital Banking Fraud Prevention",
        industry="Banking",
        geography="North America",
        company_size_band="Enterprise",
        use_case="Identity verification and fraud detection",
        target_org_count=420,
        urgency="High",
        buying_complexity="Moderate",
        notes="Strong demand for mobile channel and policy-based controls.",
        status="active",
        score=84,
        market_attractiveness=88,
        urgency_score=82,
        product_fit=89,
        accessibility=78,
        competitive_intensity=62,
        tam=120000000,
        sam=55000000,
        som=14000000,
        currency="USD",
        sizing_method="bottom-up",
        assumptions_json=json.dumps({"avg_contract": 180000, "org_count": 420}),
        source_url="https://example.com/market-research",
        confidence=0.82,
    )
    seg_2 = MarketSegment(
        name="Embedded Finance for Marketplaces",
        industry="Marketplace",
        geography="Europe",
        company_size_band="Mid-market",
        use_case="Payments and wallet risk controls",
        target_org_count=310,
        urgency="High",
        buying_complexity="High",
        notes="Marketplace operators increasingly require seamless compliance workflows.",
        status="active",
        score=76,
        market_attractiveness=80,
        urgency_score=75,
        product_fit=79,
        accessibility=68,
        competitive_intensity=70,
        tam=94000000,
        sam=36000000,
        som=11000000,
        currency="USD",
        sizing_method="top-down",
        assumptions_json=json.dumps({"market_size": 94000000, "share": 0.12}),
        source_url="https://example.com/embedded-finance",
        confidence=0.74,
    )
    db.add_all([seg_1, seg_2])
    db.flush()

    comp_a = Competitor(name="ShieldVerify", website="https://shieldverify.example", category="Identity", notes="Strong orchestration and policy controls.", source_url="https://example.com/shieldverify", confidence=0.8, strengths="Workflow automation", weaknesses="Capability depth in onboarding", pricing_notes="Custom enterprise pricing", differentiators="Deep policy orchestration")
    comp_b = Competitor(name="RiskPilot", website="https://riskpilot.example", category="Fraud prevention", notes="Prominent in risk scores and fraud ops.", source_url="https://example.com/riskpilot", confidence=0.76, strengths="High-accuracy rules engine", weaknesses="Less flexible onboarding", pricing_notes="Usage-based pricing", differentiators="Fast reporting")
    db.add_all([comp_a, comp_b])
    db.flush()

    db.add_all([
        SegmentCompetitor(segment_id=seg_1.id, competitor_id=comp_a.id, comparison_notes="Strong on orchestration", position="Leader"),
        SegmentCompetitor(segment_id=seg_1.id, competitor_id=comp_b.id, comparison_notes="More rule-oriented", position="Challenger"),
        SegmentCompetitor(segment_id=seg_2.id, competitor_id=comp_a.id, comparison_notes="Good fit for embedded workflows", position="Leader"),
    ])
    db.add_all([
        ResearchSource(title="Banking fraud stack survey", url="https://example.com/survey", publisher="Industry", source_type="report", confidence=0.8, notes="Demand is increasing across banking mobile portfolios."),
        ResearchSource(title="Marketplace compliance benchmark", url="https://example.com/compliance", publisher="Analyst", source_type="report", confidence=0.75, notes="Workflow upgrades remain a shared priority across sellers."),
    ])

    account_1 = Account(
        name="Northstar Credit Union",
        domain="northstarcu.com",
        industry="Banking",
        geography="United States",
        segment_id=seg_1.id,
        owner_id=sales.id,
        fit_score=88,
        status="active",
        priority="high",
        pain_point="Mobile channel fraud risk is growing across digital deposits.",
        fit_notes="Strong economics and well-defined security programme.",
        source="research",
        last_activity=datetime.utcnow() - timedelta(days=4),
    )
    account_2 = Account(
        name="HarborPay",
        domain="harborpay.io",
        industry="Marketplace",
        geography="United Kingdom",
        segment_id=seg_2.id,
        owner_id=sales.id,
        fit_score=81,
        status="active",
        priority="medium",
        pain_point="Need real-time verification for cross-border seller flows.",
        fit_notes="Promising expansion opportunity with API-first rollout.",
        source="inbound",
        last_activity=datetime.utcnow() - timedelta(days=9),
    )
    account_3 = Account(
        name="Crestline Insurance",
        domain="crestlineins.com",
        industry="Insurance",
        geography="Canada",
        segment_id=seg_1.id,
        owner_id=sales.id,
        fit_score=72,
        status="target",
        priority="medium",
        pain_point="Customer onboarding is fragmented and slow.",
        fit_notes="Need additional evidence on KYC and claim workflows.",
        source="market research",
        last_activity=datetime.utcnow() - timedelta(days=25),
    )
    db.add_all([account_1, account_2, account_3])
    db.flush()

    db.add_all([
        Contact(account_id=account_1.id, name="Maria Chen", title="VP Risk", department="Risk", email="maria@northstarcu.com", notes="Strong sponsor and product champion.", source="demo"),
        Contact(account_id=account_2.id, name="Samir Patel", title="Head of Payments", department="Finance", email="samir@harborpay.io", notes="Interested in API rollout.", source="demo"),
    ])

    opp_1 = Opportunity(account_id=account_1.id, owner_id=sales.id, name="Northstar onboarding expansion", stage="Proposal", value=220000, currency="USD", probability=62, close_date=date.today() + timedelta(days=35), next_step="Finalise security architecture review", activity_date=datetime.utcnow() - timedelta(days=2), last_activity=datetime.utcnow() - timedelta(days=2), status="open")
    opp_2 = Opportunity(account_id=account_2.id, owner_id=sales.id, name="HarborPay risk controls pilot", stage="Discovery", value=145000, currency="USD", probability=38, close_date=date.today() + timedelta(days=55), next_step="Run use-case workshop with product and compliance", activity_date=datetime.utcnow() - timedelta(days=12), last_activity=datetime.utcnow() - timedelta(days=12), status="open")
    opp_3 = Opportunity(account_id=account_3.id, owner_id=sales.id, name="Crestline insurance verification", stage="Target", value=95000, currency="USD", probability=12, close_date=date.today() + timedelta(days=80), next_step="Schedule discovery call with ops", activity_date=datetime.utcnow() - timedelta(days=30), last_activity=datetime.utcnow() - timedelta(days=30), status="open")
    db.add_all([opp_1, opp_2, opp_3])
    db.flush()

    customer_1 = Customer(account_id=account_1.id, opportunity_id=opp_1.id, start_date=date.today() - timedelta(days=120), plan="Enterprise Growth", recurring_value=320000, currency="USD", renewal_date=date.today() + timedelta(days=180), owner_id=cs.id, lifecycle="Active", status="active")
    customer_2 = Customer(account_id=account_2.id, opportunity_id=opp_2.id, start_date=date.today() - timedelta(days=60), plan="Professional", recurring_value=180000, currency="USD", renewal_date=date.today() + timedelta(days=120), owner_id=cs.id, lifecycle="Expansion", status="active")
    db.add_all([customer_1, customer_2])
    db.flush()

    plan_1 = OnboardingPlan(customer_id=customer_1.id, template="Enterprise Onboarding", status="in_progress", start_date=date.today() - timedelta(days=30), target_go_live=date.today() + timedelta(days=20))
    plan_2 = OnboardingPlan(customer_id=customer_2.id, template="Quick Start", status="at_risk", start_date=date.today() - timedelta(days=15), target_go_live=date.today() + timedelta(days=10))
    db.add_all([plan_1, plan_2])
    db.flush()

    db.add_all([
        OnboardingMilestone(plan_id=plan_1.id, name="Kickoff Scheduled", owner="Nina Success", due_date=date.today() - timedelta(days=10), status="completed", completion_date=date.today() - timedelta(days=8), blocker="", notes="Kickoff completed."),
        OnboardingMilestone(plan_id=plan_1.id, name="Requirements / Configuration", owner="Nina Success", due_date=date.today() - timedelta(days=2), status="in_progress", blocker="", notes="Integration checklist in progress."),
        OnboardingMilestone(plan_id=plan_2.id, name="Integration", owner="CS Team", due_date=date.today() - timedelta(days=1), status="blocked", blocker="Dependency on marketplace API partner", notes="Waiting for vendor credentials."),
        OnboardingMilestone(plan_id=plan_2.id, name="Training", owner="CS Team", due_date=date.today() + timedelta(days=7), status="pending", blocker="", notes="Planned route training."),
    ])

    db.add_all([
        AdoptionObservation(customer_id=customer_1.id, period="2026-W03", active_users=120, feature_usage=0.84, frequency="weekly", source="csv"),
        AdoptionObservation(customer_id=customer_1.id, period="2026-W04", active_users=138, feature_usage=0.92, frequency="weekly", source="csv"),
        AdoptionObservation(customer_id=customer_2.id, period="2026-W03", active_users=42, feature_usage=0.53, frequency="weekly", source="manual"),
    ])

    db.add_all([
        CustomerHealthSnapshot(customer_id=customer_1.id, score=82, band="Healthy", components_json=json.dumps({"adoption": 85, "onboarding": 78, "support": 74, "engagement": 90, "renewal": 82})),
        CustomerHealthSnapshot(customer_id=customer_2.id, score=61, band="Watch", components_json=json.dumps({"adoption": 58, "onboarding": 52, "support": 66, "engagement": 63, "renewal": 72})),
        CustomerRisk(customer_id=customer_2.id, type="Adoption", severity="Medium", description="Feature usage below target in first month.", owner="Nina Success", mitigation="Increase training cadence and monitor workflows.", status="open"),
    ])

    db.add_all([
        CostRecord(period="2026-Q1", category="Customer acquisition", amount=64000, currency="USD", segment_id=seg_1.id, notes="Digital banking acquisition spend"),
        CostRecord(period="2026-Q2", category="Customer acquisition", amount=72000, currency="USD", segment_id=seg_2.id, notes="Marketplace expansion spend"),
        BusinessTarget(metric_key="revenue", period="2026-Q1", target=500000, currency="USD", segment_id=seg_1.id, owner_id=admin.id),
        BusinessTarget(metric_key="pipeline", period="2026-Q1", target=850000, currency="USD", segment_id=seg_2.id, owner_id=admin.id),
    ])

    review = BusinessReview(title="Q1 Revenue Review", period="2026-Q1", owner="Ava Admin", status="published", summary="Review completed with risk follow-ups.")
    db.add(review)
    db.flush()
    db.add_all([
        ReviewKpiSnapshot(review_id=review.id, metric_key="revenue", actual=465000, target=500000, variance=-35000),
        ReviewKpiSnapshot(review_id=review.id, metric_key="pipeline", actual=820000, target=850000, variance=-30000),
        Decision(review_id=review.id, title="Expand field enablement", description="Fund onboarding enablement across two strategic segments.", owner="Ava Admin", date=date.today(), status="open"),
        ActionItem(title="Refresh onboarding templates", description="Update enterprise launch checklist for fintech teams.", owner="Nina Success", priority="high", due_date=date.today() + timedelta(days=7), status="open", linked_entity_type="segment", linked_entity_id=seg_1.id),
        ActionItem(title="Call HarborPay owner", description="Resolve API dependency and recommit to onboarding plan.", owner="Marcus Sales", priority="urgent", due_date=date.today() - timedelta(days=2), status="overdue", linked_entity_type="customer", linked_entity_id=customer_2.id),
    ])

    db.add_all([
        Recommendation(rule_key="overdue_next_step", entity_type="opportunity", entity_id=opp_2.id, title="Follow up on overdue discovery next step", rationale="Opportunity is stale and needs timely contact to avoid drift.", evidence_json=json.dumps({"days_since_activity": 12, "stage": "Discovery"}), severity="high", status="active"),
        Recommendation(rule_key="health_watch", entity_type="customer", entity_id=customer_2.id, title="Customer health review needed", rationale="Recent adoption and onboarding metrics indicate risk.", evidence_json=json.dumps({"score": 61, "risk_count": 1}), severity="medium", status="active"),
    ])
    db.add(AuditLog(actor="system", entity="seed", action="initialize", before_json="{}", after_json=json.dumps({"segments": 2, "accounts": 3, "opportunities": 3, "customers": 2})))
    db.commit()


def get_summary(db: Session):
    opportunities = db.query(Opportunity).all()
    customers = db.query(Customer).all()
    actions = db.query(ActionItem).all()
    open_pipeline = sum((op.value or 0) for op in opportunities if op.status == "open")
    weighted_pipeline = sum((op.value or 0) * ((op.probability or 0) / 100) for op in opportunities if op.status == "open")
    closed_won = sum((op.value or 0) for op in opportunities if op.stage == "Closed Won")
    onboarding_at_risk = db.query(CustomerRisk).count()
    overdue_actions = sum(1 for action in actions if action.status == "overdue")
    return {
        "kpis": {
            "open_pipeline": round(open_pipeline, 2),
            "weighted_pipeline": round(weighted_pipeline, 2),
            "closed_won_value": round(closed_won, 2),
            "active_customers": len(customers),
            "onboarding_at_risk": onboarding_at_risk,
            "overdue_actions": overdue_actions,
        },
        "segments": db.query(MarketSegment).count(),
        "accounts": db.query(Account).count(),
        "opportunities": len(opportunities),
        "customers": len(customers),
    }


@app.on_event("startup")
def startup_event() -> None:
    db = SessionLocal()
    try:
        Base.metadata.create_all(bind=engine)
        seed_demo_data(db)
    finally:
        db.close()


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "service": "RevOpsIQ backend"}


@app.get("/api/overview")
def overview(db: Session = Depends(get_db)) -> dict:
    return get_summary(db)


@app.get("/api/segments")
def list_segments(db: Session = Depends(get_db)):
    rows = db.query(MarketSegment).all()
    return [
        {
            "id": row.id,
            "name": row.name,
            "industry": row.industry,
            "geography": row.geography,
            "company_size_band": row.company_size_band,
            "use_case": row.use_case,
            "target_org_count": row.target_org_count,
            "score": row.score,
            "status": row.status,
            "confidence": row.confidence,
            "tam": row.tam,
            "sam": row.sam,
            "som": row.som,
            "currency": row.currency,
        }
        for row in rows
    ]


@app.post("/api/segments")
def create_segment(payload: SegmentCreate, db: Session = Depends(get_db)) -> dict:
    identity = (
        func.lower(func.trim(MarketSegment.name)) == payload.name.strip().lower(),
        func.lower(func.trim(MarketSegment.industry)) == payload.industry.strip().lower(),
        func.lower(func.trim(MarketSegment.geography)) == payload.geography.strip().lower(),
    )
    existing = db.query(MarketSegment.id).filter(*identity).first()
    if existing:
        raise HTTPException(
            status_code=409,
            detail="A market segment with this name, industry, and geography already exists.",
        )

    segment = MarketSegment(**payload.model_dump())
    db.add(segment)
    db.commit()
    db.refresh(segment)
    return {"id": segment.id, "status": "created"}


@app.get("/api/accounts")
def list_accounts(db: Session = Depends(get_db)):
    rows = db.query(Account).all()
    return [
        {
            "id": row.id,
            "name": row.name,
            "industry": row.industry,
            "geography": row.geography,
            "segment": row.segment.name if row.segment else None,
            "owner": row.owner.name if row.owner else None,
            "fit_score": row.fit_score,
            "status": row.status,
            "priority": row.priority,
            "source": row.source,
        }
        for row in rows
    ]


@app.post("/api/accounts")
def create_account(payload: AccountCreate, db: Session = Depends(get_db)) -> dict:
    account = Account(**payload.model_dump())
    db.add(account)
    db.commit()
    db.refresh(account)
    return {"id": account.id, "status": "created"}


@app.get("/api/opportunities")
def list_opportunities(db: Session = Depends(get_db)):
    rows = db.query(Opportunity).all()
    return [
        {
            "id": row.id,
            "account": row.account.name if row.account else "",
            "name": row.name,
            "stage": row.stage,
            "value": row.value,
            "currency": row.currency,
            "probability": row.probability,
            "close_date": row.close_date.isoformat() if row.close_date else None,
            "next_step": row.next_step,
            "status": row.status,
            "owner": row.owner.name if row.owner else None,
            "weighted_value": round((row.value or 0) * ((row.probability or 0) / 100), 2),
        }
        for row in rows
    ]


@app.post("/api/opportunities")
def create_opportunity(payload: OpportunityCreate, db: Session = Depends(get_db)) -> dict:
    obj = Opportunity(**payload.model_dump())
    if payload.close_date:
        obj.close_date = date.fromisoformat(payload.close_date)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return {"id": obj.id, "status": "created"}


@app.get("/api/customers")
def list_customers(db: Session = Depends(get_db)):
    rows = db.query(Customer).all()
    return [
        {
            "id": row.id,
            "name": row.account.name if row.account else "",
            "plan": row.plan,
            "renewal_date": row.renewal_date.isoformat() if row.renewal_date else None,
            "lifecycle": row.lifecycle,
            "status": row.status,
            "owner": row.owner.name if row.owner else None,
            "recurring_value": row.recurring_value,
        }
        for row in rows
    ]


@app.post("/api/customers")
def create_customer(payload: CustomerCreate, db: Session = Depends(get_db)) -> dict:
    obj = Customer(**payload.model_dump())
    if payload.renewal_date:
        obj.renewal_date = date.fromisoformat(payload.renewal_date)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return {"id": obj.id, "status": "created"}


@app.get("/api/actions")
def list_actions(db: Session = Depends(get_db)):
    rows = db.query(ActionItem).all()
    return [
        {
            "id": row.id,
            "title": row.title,
            "description": row.description,
            "owner": row.owner,
            "priority": row.priority,
            "due_date": row.due_date.isoformat() if row.due_date else None,
            "status": row.status,
            "linked_entity_type": row.linked_entity_type,
            "linked_entity_id": row.linked_entity_id,
        }
        for row in rows
    ]


@app.post("/api/actions")
def create_action(payload: ActionCreate, db: Session = Depends(get_db)) -> dict:
    obj = ActionItem(**payload.model_dump())
    if payload.due_date:
        obj.due_date = date.fromisoformat(payload.due_date)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return {"id": obj.id, "status": "created"}


@app.get("/api/recommendations")
def list_recommendations(db: Session = Depends(get_db)):
    rows = db.query(Recommendation).all()
    return [
        {
            "id": row.id,
            "rule_key": row.rule_key,
            "entity_type": row.entity_type,
            "entity_id": row.entity_id,
            "title": row.title,
            "rationale": row.rationale,
            "severity": row.severity,
            "status": row.status,
        }
        for row in rows
    ]


@app.post("/api/recommendations")
def create_recommendation(payload: RecommendationCreate, db: Session = Depends(get_db)) -> dict:
    obj = Recommendation(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return {"id": obj.id, "status": "created"}


@app.get("/api/reviews")
def list_reviews(db: Session = Depends(get_db)):
    rows = db.query(BusinessReview).all()
    return [
        {
            "id": row.id,
            "title": row.title,
            "period": row.period,
            "owner": row.owner,
            "status": row.status,
            "summary": row.summary,
        }
        for row in rows
    ]


@app.post("/api/reviews")
def create_review(payload: ReviewCreate, db: Session = Depends(get_db)) -> dict:
    obj = BusinessReview(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return {"id": obj.id, "status": "created"}


@app.get("/api/metrics")
def metric_overview(db: Session = Depends(get_db)) -> dict:
    segments = db.query(MarketSegment).all()
    return {
        "total_tam": sum((s.tam or 0) for s in segments),
        "total_sam": sum((s.sam or 0) for s in segments),
        "total_som": sum((s.som or 0) for s in segments),
        "segment_count": len(segments),
        "average_segment_score": round(sum((s.score or 0) for s in segments) / max(len(segments), 1), 2),
    }


@app.get("/api/health-scores")
def health_scores(db: Session = Depends(get_db)):
    rows = db.query(CustomerHealthSnapshot).all()
    return [
        {
            "customer_id": row.customer_id,
            "score": row.score,
            "band": row.band,
            "components": json.loads(row.components_json or "{}"),
        }
        for row in rows
    ]


@app.get("/api/audit")
def audit(db: Session = Depends(get_db)):
    rows = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(10).all()
    return [
        {
            "actor": row.actor,
            "entity": row.entity,
            "action": row.action,
            "timestamp": row.timestamp.isoformat() if row.timestamp else None,
        }
        for row in rows
    ]
