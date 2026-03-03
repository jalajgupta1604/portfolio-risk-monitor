# Product Requirement Document (PRD)

## Stock Portfolio "Risk Collapse" Early Warning System

------------------------------------------------------------------------

## 1. Product Overview

### Product Name

Portfolio Health Monitor (Working Title)

### Vision

Build a risk intelligence platform that helps retail investors detect
rising portfolio fragility before major drawdowns occur.

### Core Value Proposition

Instead of giving buy/sell tips, the platform provides: - Portfolio Risk
Score - Correlation & sector concentration insights - Stress test
simulation - Early warning alerts when risk accelerates

------------------------------------------------------------------------

## 2. Problem Statement

Retail investors focus primarily on returns and price movement but lack
tools to: - Detect overexposure to one sector - Understand correlation
risk - Measure downside beta - Predict portfolio drawdown probability -
Monitor rising volatility in real time

Existing broker apps show portfolio value but do not measure systemic
risk.

------------------------------------------------------------------------

## 3. Target Users

### Primary Segment

-   Serious retail investors (age 25--45)
-   Monthly portfolio size ₹2L -- ₹50L
-   Active equity investors

### Secondary Segment

-   HNI individuals
-   Financial advisors (future phase)

------------------------------------------------------------------------

## 4. Key Features (MVP)

### 4.1 Portfolio Input

-   Manual stock entry
-   CSV upload (broker export)
-   Automatic weight calculation

### 4.2 Risk Engine Calculations

-   Rolling 30-day volatility
-   Correlation matrix
-   Portfolio beta vs index
-   Downside beta
-   95% Value at Risk (VaR)
-   Stress testing (-3%, -5%, -8% index simulation)

### 4.3 Risk Score (0--100)

Composite score based on: - Volatility - Correlation concentration -
Sector exposure - Beta exposure

### 4.4 Risk Acceleration Indicator

Formula: Risk Acceleration = Current Risk Score -- 7-Day Average Risk
Score

Triggers alert if risk increases rapidly.

### 4.5 Dashboard

-   Overall Risk Score
-   Sector allocation chart
-   Correlation heatmap
-   Stress test results
-   Risk trend graph (30-day view)

### 4.6 Alert System

Triggers when: - Risk Score \> 70 - Sector concentration \> 40% -
Correlation spike above threshold - Volatility index spike

Delivery via: - Email (MVP) - WhatsApp (Phase 2)

------------------------------------------------------------------------

## 5. Non-Goals (MVP)

-   No stock buy/sell recommendations
-   No automated portfolio rebalancing
-   No brokerage integration (initial phase)
-   No advanced machine learning models

------------------------------------------------------------------------

## 6. Technical Architecture

### Backend

-   Python
-   FastAPI
-   PostgreSQL
-   Scheduled cron jobs for recalculation

### Risk Engine

-   NumPy / Pandas for statistical calculations
-   Rolling window computation
-   Correlation matrix generation
-   Beta and VaR computation

### Frontend

-   React.js
-   Charting library (e.g., Recharts)

### Infrastructure

-   Cloud deployment (AWS / DigitalOcean)
-   Background job scheduler

------------------------------------------------------------------------

## 7. Data Requirements

-   Historical OHLC stock data
-   Index historical data
-   Sector classification mapping
-   Volatility index data

Data refresh frequency: - Daily (EOD for MVP) - Intraday (future phase)

------------------------------------------------------------------------

## 8. User Flow

1.  User signs up
2.  User enters portfolio or uploads CSV
3.  System calculates risk metrics
4.  Dashboard displays results
5.  Alerts trigger if thresholds crossed

------------------------------------------------------------------------

## 9. Monetization Strategy

### Free Tier

-   Basic Risk Score
-   Sector exposure

### Paid Tier (₹499/month)

-   Correlation heatmap
-   Stress simulation
-   Risk acceleration alerts

### Premium Tier (₹1999/month)

-   Advanced analytics
-   Macro sensitivity insights
-   Weekly risk report

------------------------------------------------------------------------

## 10. Compliance Positioning

The platform provides analytics and risk metrics only. It does NOT
provide investment advice or stock recommendations. Proper disclaimer
required during onboarding.

------------------------------------------------------------------------

## 11. KPIs for Success

-   100 beta users in first 60 days
-   20% paid conversion rate
-   Monthly churn \< 10%
-   Average weekly engagement \> 2 sessions per user

------------------------------------------------------------------------

## 12. Future Roadmap (Post-MVP)

-   Macro sensitivity model
-   AI-based risk explanation engine
-   Smart hedge suggestions (ETF exposure)
-   Broker API integration
-   Mobile application

------------------------------------------------------------------------

## 13. Timeline (60-Day Build Plan)

Phase 1 (Days 1--15): Risk engine core Phase 2 (Days 16--30): Dashboard
MVP Phase 3 (Days 31--45): Alert & acceleration engine Phase 4 (Days
46--60): Monetization + Beta launch

------------------------------------------------------------------------

## 14. Risks & Mitigation

Risk: Data inaccuracies\
Mitigation: Validate with multiple sources

Risk: Regulatory scrutiny\
Mitigation: Strict no-advice positioning

Risk: Low differentiation\
Mitigation: Focus on Risk Acceleration & stress simulation

------------------------------------------------------------------------

END OF DOCUMENT
