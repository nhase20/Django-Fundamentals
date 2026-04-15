def classify_retailer(client):
    score = 0

    if client.risk_tolerance:
        score += client.risk_tolerance

    if client.time_horizon:
        if client.time_horizon >= 15:
            score += 5
        elif client.time_horizon >= 7:
            score += 2
        else:
            score += 4
    
    if client.client_goals:
        if client.client_goals == "independence":
            score += 6
        elif client.client_goals == "retirement":
            score += 2
        else:
            score += 1
        
    if client.age:
        if client.age >= 45:
            score += 2
        elif client.age >= 35:
            score += 5
        else:
            score += 7



    # Classification
    if score <= 6:
        return "Conservative"
    elif score <= 12:
        return "Balanced"
    else:
        return "Aggressive"
    
def classify_institution(client):
    score = 0

    if client.assets_held:
        if client.assets_held >= 1_000_000_000:  # 1B+
            score += 7
        elif client.assets_held >= 100_000_000:  # 100M+
            score += 5
        else:
            score += 2

    if client.risk_tolerance == "aggressive":
        score += 6
    elif client.risk_tolerance == "moderate":
        score += 4
    else:
        score += 2

    if client.liquidity == "low":  # long-term
        score += 6
    elif client.liquidity == "medium":
        score += 4
    else:
        score += 2

    if client.time_horizon:
        if client.time_horizon >= 10:
            score += 6
        elif client.time_horizon >= 5:
            score += 4
        else:
            score += 2

    # Performance objective
    if client.performance == "outperform":
        score += 5
    elif client.performance == "match":
        score += 3
    else:
        score += 2

    if score <= 15:
        return "Tier 1  (Growth Focused)"
    elif score <= 25:
        return "Tier 2  (Balanced Institution)"
    else:
        return "Tier 3 (Large/Complex Institution)"
