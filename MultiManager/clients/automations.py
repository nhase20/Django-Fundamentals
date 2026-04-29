# clients/automations.py


# ─────────────────────────────────────────────
# ACTION 1 — Dynamic asset allocation engine
# Inputs: risk_profile (str), time_horizon (int years), risk_rating (str)
# Output: dict that always sums to 100
# ─────────────────────────────────────────────

# Map each risk profile to a starting equity weight
_PROFILE_BASE_EQUITY = {
    "Aggressive":               78,
    "Moderate Aggressive":      65,
    "Global Aggressive":        68,
    "Moderate":                 55,
    "Global Moderate":          52,
    "Global Moderate Aggressive": 60,
    "Conservative":             35,
    "Global Conservative":      32,
    "Cautious":                 22,
    "Global Cautious":          25,
}

# Map risk rating to an equity adjustment (positive = more equity)
_RATING_EQUITY_ADJUSTMENT = {
    "pure equity":  +10,
    "high":         +6,
    "medium":       0,
    "low-medium":   -5,
    "low":          -10,
    "flexible":     0,
}


def dynamic_asset_allocation(client):
    """
    Produces a unique allocation for every client by combining:
      1. Risk profile  → base equity weight
      2. Time horizon  → horizon modifier (longer = more equity)
      3. Risk rating   → rating modifier (higher tolerance = more equity)

    All four buckets are adjusted proportionally so they always sum to 100.
    """

    # ── Step 1: base equity from profile ──
    base_equity = _PROFILE_BASE_EQUITY.get(client.risk_profile, 50)

    # ── Step 2: horizon modifier ──
    horizon = client.time_horizon or 5
    if horizon >= 20:
        horizon_mod = +8
    elif horizon >= 15:
        horizon_mod = +5
    elif horizon >= 10:
        horizon_mod = +3
    elif horizon >= 7:
        horizon_mod = +1
    elif horizon >= 3:
        horizon_mod = -2
    else:
        horizon_mod = -6   # very short horizon → pull back on equity

    # ── Step 3: risk rating modifier ──
    rating_mod = _RATING_EQUITY_ADJUSTMENT.get(client.risk_rating, 0)

    # ── Step 4: final equity weight, clamped to sensible bounds ──
    equity = max(10, min(92, base_equity + horizon_mod + rating_mod))

    # ── Step 5: distribute the remaining 100 − equity across bonds, cash, alternatives ──
    # Rule: more equity = less bonds; cash stays relatively stable;
    # alternatives scale slightly with equity (higher risk = more alternatives)
    remaining = 100 - equity

    # Alternatives: 3% base, scales with equity aggression
    alternatives = max(2, min(12, round(equity * 0.06)))

    # Cash: conservative clients hold more cash; aggressive hold very little
    cash = max(2, min(18, round((100 - equity) * 0.22)))

    # Bonds: everything that's left
    bonds = remaining - cash - alternatives

    # Safety: if bonds went negative due to rounding, clip and re-assign
    if bonds < 2:
        bonds = 2
        cash = max(2, remaining - bonds - alternatives)

    # Final rounding pass — ensure exact 100
    total = equity + bonds + cash + alternatives
    diff = 100 - total
    bonds += diff   # absorb any 1-point rounding discrepancy into bonds

    return {
        "Equities":     equity,
        "Bonds":        bonds,
        "Cash":         cash,
        "Alternatives": alternatives,
    }


# ─────────────────────────────────────────────
# ACTION 2 — Personalised client insight engine
# Returns a structured dict the template can render directly
# ─────────────────────────────────────────────

def generate_client_insights(client):
    """
    Builds a full narrative insight block for a client.
    Returns:
        suitability  — one-sentence verdict
        reasoning    — paragraph explaining the why
        benchmark    — suggested index benchmark
        scenarios    — list of 5 dicts (label, probability, return_range, description)
    """

    risk    = client.risk_profile
    horizon = client.time_horizon or 5
    age     = client.age or 30
    rating  = client.risk_rating
    goal    = client.investment_goal or ""
    group   = client.client_group

    # ── Suitability verdict ──
    suitability_map = {
        "Aggressive":               "High-growth equity portfolio with long-term capital appreciation focus.",
        "Moderate Aggressive":      "Growth-oriented portfolio balancing equities and some defensive exposure.",
        "Global Aggressive":        "Globally diversified high-growth portfolio with offshore equity exposure.",
        "Moderate":                 "Balanced portfolio with equal weight on growth and income.",
        "Global Moderate":          "Globally balanced portfolio with moderate offshore diversification.",
        "Global Moderate Aggressive": "Globally tilted growth portfolio with a bias toward offshore equity.",
        "Conservative":             "Income-focused portfolio prioritising capital preservation.",
        "Global Conservative":      "Globally diversified income portfolio with low volatility mandate.",
        "Cautious":                 "Capital preservation portfolio with minimal equity exposure.",
        "Global Cautious":          "Globally diversified capital preservation portfolio.",
    }
    suitability = suitability_map.get(risk, "Balanced portfolio aligned to your stated preferences.")

    # ── Reasoning paragraph ──
    # Build it dynamically from the actual inputs so every client reads differently
    horizon_text = (
        f"a long {horizon}-year investment horizon"  if horizon >= 15 else
        f"a medium {horizon}-year investment horizon" if horizon >= 7 else
        f"a shorter {horizon}-year investment horizon"
    )
    age_text = (
        "approaching retirement age"    if age >= 60 else
        "in their prime accumulation years" if age >= 40 else
        "in an early wealth-building phase" if age >= 25 else
        "at the very start of their investment journey"
    )
    rating_text = (
        "a high risk rating indicating comfort with volatility"   if rating in ("high", "pure equity") else
        "a moderate risk rating balancing growth and stability"   if rating == "medium" else
        "a conservative risk rating preferring stability"         if rating in ("low", "low-medium") else
        "a flexible risk rating"
    )
    goal_text = f' with a stated goal of "{goal}"' if goal and goal.lower() != "none" else ""

    reasoning = (
        f"This client is {age_text}, holds {horizon_text}, and carries {rating_text}{goal_text}. "
        f"Within the {group} client group, a {risk} mandate is appropriate because "
    )
    if risk in ("Aggressive", "Global Aggressive", "Moderate Aggressive", "Global Moderate Aggressive"):
        reasoning += (
            "the long horizon provides enough time to recover from short-term market downturns, "
            "and the risk rating confirms the client can tolerate equity volatility. "
            "Higher equity exposure maximises compounding over the investment period."
        )
    elif risk in ("Moderate", "Global Moderate"):
        reasoning += (
            "a balanced split between growth assets and defensive assets smooths "
            "return volatility while still capturing meaningful market upside. "
            "This suits clients who want growth but are sensitive to large drawdowns."
        )
    else:
        reasoning += (
            "preserving capital takes priority over maximising returns. "
            "Bond and income-heavy allocations reduce drawdown risk and "
            "provide more predictable income streams over the investment period."
        )

    # ── Benchmark ──
    if "Global" in risk:
        benchmark = "MSCI World Index"
    elif risk in ("Aggressive",):
        benchmark = "Nasdaq-100" if horizon >= 10 else "S&P 500"
    elif risk in ("Moderate Aggressive", "Moderate"):
        benchmark = "S&P 500"
    elif risk in ("Conservative", "Cautious"):
        benchmark = "Bloomberg Global Aggregate Bond Index"
    else:
        benchmark = "S&P 500"

    # ── Scenarios ──
    # Each scenario is defined relative to the profile's typical return band
    # Base expected returns are calibrated to typical SA multi-asset fund ranges
    _base_returns = {
        "Aggressive":               (10, 16),
        "Moderate Aggressive":      (8,  13),
        "Global Aggressive":        (9,  15),
        "Global Moderate Aggressive": (8, 13),
        "Moderate":                 (6,  10),
        "Global Moderate":          (6,  10),
        "Conservative":             (4,   7),
        "Global Conservative":      (4,   7),
        "Cautious":                 (2,   5),
        "Global Cautious":          (2,   5),
    }
    lo, hi = _base_returns.get(risk, (5, 10))

    scenarios = [
        {
            "label":        "Severe Bear Market",
            "probability":  "~10%",
            "return_range": f"{lo - 14}% to {lo - 8}%",
            "colour":       "#dc2626",
            "description": (
                f"A sharp equity market correction (e.g. 2008-style crisis) could push "
                f"returns significantly negative in the short term. A {risk} allocation "
                f"would experience a drawdown but the {horizon}-year horizon allows "
                f"full recovery given historical market cycles."
            ),
        },
        {
            "label":        "Mild Bear / Underperformance",
            "probability":  "~20%",
            "return_range": f"{lo - 6}% to {lo - 1}%",
            "colour":       "#f59e0b",
            "description": (
                "Rising interest rates, inflation pressure, or sector-specific weakness "
                "could suppress returns below expectations. Defensive assets (bonds, cash) "
                "in the allocation act as a cushion, limiting downside."
            ),
        },
        {
            "label":        "Base Case",
            "probability":  "~40%",
            "return_range": f"{lo}% to {hi}%",
            "colour":       "#2ec4b6",
            "description": (
                f"Under normal market conditions, a {risk} portfolio targeting the "
                f"{benchmark} should deliver returns in this range annually over the "
                f"full {horizon}-year horizon. This is the most likely outcome."
            ),
        },
        {
            "label":        "Bull Market Upside",
            "probability":  "~20%",
            "return_range": f"{hi + 1}% to {hi + 6}%",
            "colour":       "#10b981",
            "description": (
                "Strong economic growth, earnings surprises, or a rate-cutting cycle "
                "could push equity markets meaningfully higher. The portfolio's equity "
                "exposure directly benefits from this environment."
            ),
        },
        {
            "label":        "Exceptional Bull Run",
            "probability":  "~10%",
            "return_range": f"{hi + 7}% to {hi + 14}%",
            "colour":       "#4f46e5",
            "description": (
                "A sustained multi-year bull market (e.g. 2010–2021 style) could "
                "produce outsized returns well above the base case. While unlikely "
                "to persist for the full investment period, capitalising on even "
                "part of this environment compounds wealth significantly."
            ),
        },
    ]

    return {
        "suitability": suitability,
        "reasoning":   reasoning,
        "benchmark":   benchmark,
        "scenarios":   scenarios,
    }


# ── Legacy helpers kept for backwards compatibility ──

def retail_benchmark_selector(client):
    return generate_client_insights(client)["benchmark"]


def retail_asset_allocation(client):
    return dynamic_asset_allocation(client)


def classify_retailer(client):
    horizon = client.time_horizon or 5
    age = client.age or 30
    score = 0
    score += 5 if horizon >= 15 else (3 if horizon >= 7 else 1)
    score += 1 if age >= 55 else (3 if age >= 40 else 5)
    if score <= 3:   return "Conservative"
    if score <= 6:   return "Moderate"
    if score <= 8:   return "Moderate Aggressive"
    return "Aggressive"

RISK_SCORE_MAP = {
    # Maps total score → risk profile label
    (0, 3):   'Conservative',
    (4, 6):   'Cautious',
    (7, 9):   'Moderate',
    (10, 12): 'Moderate Aggressive',
    (13, 15): 'Aggressive',
}

ASISA_MAP = {
    'Conservative':        '(ASISA) South African MA Income',
    'Cautious':            '(ASISA) South African MA Low Equity',
    'Moderate':            '(ASISA) South African MA Medium Equity',
    'Moderate Aggressive': '(ASISA) South African MA High Equity',
    'Aggressive':          '(ASISA) Wwide MA Flexible',
}

def calculate_risk_profile(answers: dict) -> tuple[str, str]:
    """
    answers keys: purpose, time_horizon, emergency_fund, 
                  volatility_comfort, income_or_growth
    Returns: (risk_profile_label, asisa_category)
    """
    score = 0
    score += {'retirement': 1, 'education': 2, 'wealth': 3}   .get(answers.get('purpose'), 2)
    score += {'short': 1, 'medium': 2, 'long': 3}             .get(answers.get('time_horizon'), 2)
    score += {'no': 0, 'yes': 1}                               .get(answers.get('emergency_fund'), 0)
    score += {'low': 1, 'medium': 2, 'high': 3}               .get(answers.get('volatility_comfort'), 1)
    score += {'income': 1, 'balanced': 2, 'growth': 3}        .get(answers.get('income_or_growth'), 2)

    for (lo, hi), label in RISK_SCORE_MAP.items():
        if lo <= score <= hi:
            return label, ASISA_MAP[label]
    return 'Moderate', ASISA_MAP['Moderate']