# clients/automations.py

def classify_retailer(client):
    """Score-based risk classification using time horizon and age."""
    score = 0

    if client.time_horizon:
        if client.time_horizon >= 15:
            score += 5
        elif client.time_horizon >= 7:
            score += 3
        else:
            score += 1

    if client.age:
        if client.age >= 55:
            score += 1
        elif client.age >= 40:
            score += 3
        else:
            score += 5

    if score <= 3:
        return "Conservative"
    elif score <= 6:
        return "Moderate"
    elif score <= 8:
        return "Moderate Aggressive"
    else:
        return "Aggressive"


def retail_benchmark_selector(client):
    risk = client.risk_profile
    horizon = client.time_horizon
    age = client.age
    goal = client.investment_goal  # was client.client_goals — field is investment_goal

    if risk == "Aggressive":
        if horizon >= 10:
            return "Nasdaq-100"
        if age < 35:
            return "Russell 2000"
        return "S&P 500"

    elif risk in ("Moderate Aggressive", "Moderate"):
        if goal and "independence" in goal.lower():
            return "MSCI World Index"
        if horizon >= 5:
            return "S&P 500"
        return "Dow Jones Industrial Average (DJIA)"

    elif risk in ("Conservative", "Cautious"):
        if goal and "preservation" in goal.lower():
            return "Dow Jones Industrial Average (DJIA)"
        if age >= 50:
            return "MSCI World Index"
        return "S&P 500"

    return "S&P 500"


def retail_asset_allocation(client):
    """Returns allocation dict based on risk profile and time horizon."""
    risk = client.risk_profile
    horizon = client.time_horizon

    if risk == "Aggressive":
        if horizon >= 10:
            return {"Equities": 80, "Bonds": 10, "Cash": 5, "Alternatives": 5}
        return {"Equities": 70, "Bonds": 15, "Cash": 10, "Alternatives": 5}

    elif risk == "Moderate Aggressive":
        return {"Equities": 65, "Bonds": 20, "Cash": 10, "Alternatives": 5}

    elif risk == "Moderate":
        return {"Equities": 60, "Bonds": 25, "Cash": 10, "Alternatives": 5}

    elif risk == "Conservative":
        return {"Equities": 40, "Bonds": 40, "Cash": 15, "Alternatives": 5}

    elif risk == "Cautious":
        return {"Equities": 25, "Bonds": 50, "Cash": 20, "Alternatives": 5}

    # Global profiles
    elif "Global" in risk:
        return {"Equities": 55, "Bonds": 25, "Cash": 10, "Alternatives": 10}

    # Fallback
    return {"Equities": 50, "Bonds": 30, "Cash": 15, "Alternatives": 5}