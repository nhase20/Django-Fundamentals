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
    
def retail_benchmark_selector(client):
    
    risk = client.risk_profile
    horizon = client.time_horizon
    age = client.age
    goal = client.client_goals

    if risk == "Aggressive":
        
        # Long horizon → high growth tech
        if horizon >= 10:
            return "Nasdaq-100"
        
        # Younger + aggressive → small cap growth
        if age < 35:
            return "Russell 2000"
        
        return "S&P 500"

    elif risk == "Balanced":
        
        # Want global diversification
        if goal == "independence":
            return "MSCI World Index"
        
        # Medium horizon → balanced US exposure
        if horizon >= 5:
            return "S&P 500"
        
        return "Dow Jones Industrial Average (DJIA)"

    elif risk == "Conservative":
        
        # Wealth preservation → stable companies
        if goal == "preservation":
            return "Dow Jones Industrial Average (DJIA)"
        
        # Older investors → less volatility
        if age >= 50:
            return "MSCI World Index"
        
        return "S&P 500"

    # fallback
    return "S&P 500"

def select_institutional_benchmark(client):

    objective = client.return_objective.strip()
    risk = client.risk_tolerance
    liquidity = client.liquidity
    performance = client.performance
    tier = client.tier  

    if objective == "income":
        return "Bond Index"

    if objective == "capital":
        if risk == "aggressive":
            return "S&P 500"
        else:
            return "Multi-Asset Benchmark"

    if objective == "total":

        # Tier-based refinement
        if "Tier 3" in tier:
            return "Multi-Asset Benchmark"

        if risk == "aggressive":
            return "S&P 500"

        return "Multi-Asset Benchmark"

    if performance == "outperforn":
        return "S&P 500"

    if performance == "minimize":
        return "Bond Index"

    if liquidity == "high":
        return "S&P 500"  # liquid markets

    if liquidity == "low":
        return "Multi-Asset Benchmark"

    # fallback
    return "Custom Benchmark"