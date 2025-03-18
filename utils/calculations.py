import math


def get_order_multiplier(inputs, order):
    """Get the order of entry multiplier."""
    return inputs["orderMultipliers"].get(
        order, inputs["orderMultipliers"][4]
    )  # Default to 4th+ if invalid


def get_cumulative_probability(inputs, phase):
    """Calculate cumulative probability of success."""
    probabilities = inputs["probabilities"]

    if phase == "preclinical":
        return (
            probabilities["preclinical"]
            * probabilities["phase1"]
            * probabilities["phase2"]
            * probabilities["phase3"]
            * probabilities["registration"]
        ) / math.pow(100, 5)
    elif phase == "phase1":
        return (
            probabilities["phase1"]
            * probabilities["phase2"]
            * probabilities["phase3"]
            * probabilities["registration"]
        ) / math.pow(100, 4)
    elif phase == "phase2":
        return (
            probabilities["phase2"]
            * probabilities["phase3"]
            * probabilities["registration"]
        ) / math.pow(100, 3)
    elif phase == "phase3":
        return (probabilities["phase3"] * probabilities["registration"]) / math.pow(
            100, 2
        )
    elif phase == "registration":
        return probabilities["registration"] / 100
    else:
        return 1


def calculate_phase_value(inputs, phase):
    """Calculate phase value with NPV adjustments."""
    base_value = inputs["launchValue"] * get_order_multiplier(
        inputs, inputs["orderOfEntry"]
    )
    risk_adjusted = base_value * get_cumulative_probability(inputs, phase)

    # Apply time-based NPV adjustment using custom timing values
    time_to_market = inputs["timeToMarket"].get(phase, 0)

    # Calculate NPV with discount rate
    discount_factor = math.pow(1 + (inputs["discountRate"] / 100), time_to_market)
    npv_adjusted = risk_adjusted / discount_factor

    if not inputs["includeRDCosts"]:
        return npv_adjusted

    # Subtract cumulative costs up to this phase INCLUDING the current phase
    cumulative_costs = 0
    costs = inputs["costs"]

    # Calculate costs up to and including current phase
    if phase == "preclinical":
        cumulative_costs += costs["preclinical"]  # Include current phase cost
    elif phase == "phase1":
        cumulative_costs += (
            costs["preclinical"] + costs["phase1"]
        )  # Include current phase cost
    elif phase == "phase2":
        cumulative_costs += (
            costs["preclinical"] + costs["phase1"] + costs["phase2"]
        )  # Include current phase cost
    elif phase == "phase3":
        cumulative_costs += (
            costs["preclinical"] + costs["phase1"] + costs["phase2"] + costs["phase3"]
        )  # Include current phase cost
    elif phase == "registration":
        cumulative_costs += (
            costs["preclinical"]
            + costs["phase1"]
            + costs["phase2"]
            + costs["phase3"]
            + costs["registration"]
        )  # Include current phase cost

    return npv_adjusted - cumulative_costs


def calculate_deal_percentages(inputs):
    """Calculate deal percentages based on asset value and deal value."""
    phase_value = calculate_phase_value(inputs, inputs["dealStage"])
    deal_value = inputs["dealValue"]

    # Calculate ownership percentage based on deal value relative to asset value
    ownership_percent = (
        min((deal_value / phase_value) * 100, 100) if phase_value > 0 else 0
    )

    return {
        "partnerShare": ownership_percent,
        "companyShare": 100 - ownership_percent,
        "totalValue": phase_value,
        "valuePerShare": phase_value / 100,  # Value per 1% ownership
    }


def calculate_required_deal_value(inputs, percentage):
    """Calculate required deal value for desired percentage."""
    phase_value = calculate_phase_value(inputs, inputs["dealStage"])
    return (phase_value * percentage) / 100


def calculate_strategic_decision(inputs, current_phase, out_license_percentage):
    """Calculate strategic decision between continuing development vs out-licensing."""
    # Get all phases and find the next phase
    phases = ["preclinical", "phase1", "phase2", "phase3", "registration"]
    if current_phase == "registration":
        next_phase = None  # No next phase after registration
    else:
        next_phase_index = phases.index(current_phase) + 1
        next_phase = phases[next_phase_index]

    # Calculate current phase value
    current_phase_value = calculate_phase_value(inputs, current_phase)

    # Calculate out-license option based on the current phase value
    # Deal value is the portion sold at the out-license percentage
    deal_value = (current_phase_value * out_license_percentage) / 100
    # Retained value is the remaining portion
    company_share_percentage = 100 - out_license_percentage
    retained_value = (current_phase_value * company_share_percentage) / 100

    total_deal_value = (
        deal_value + retained_value
    )  # This equals the current phase value

    # If there's no next phase, only the current deal is possible
    if next_phase is None:
        return {
            "current_phase": current_phase,
            "next_phase": None,
            "deal_now_value": total_deal_value,
            "continue_develop_value": 0,
            "recommendation": "Deal Now",
            "value_difference": total_deal_value,
            "probability_next_phase": 0,
            "out_license_percentage": out_license_percentage,
        }

    # Calculate value of continuing development
    next_phase_value = calculate_phase_value(inputs, next_phase)

    # Calculate the probability of successfully progressing to the next phase
    probability_next_phase = inputs["probabilities"][current_phase] / 100

    # Calculate the costs to complete the current phase
    current_phase_cost = inputs["costs"][current_phase]

    # For the expected value, we need:
    # 1. The full value at the next phase if successful
    # 2. Multiplied by the probability of success
    expected_continue_value = probability_next_phase * next_phase_value

    # Determine recommendation by comparing risk-adjusted next phase value with current value
    value_difference = expected_continue_value - current_phase_value
    if value_difference > 0:
        recommendation = "Continue Development"
    else:
        recommendation = "Deal Now"

    return {
        "current_phase": current_phase,
        "next_phase": next_phase,
        "current_phase_value": current_phase_value,
        "deal_now_value": current_phase_value,  # This is the full asset value now
        "continue_develop_value": expected_continue_value,
        "recommendation": recommendation,
        "value_difference": abs(value_difference),
        "probability_next_phase": probability_next_phase * 100,
        "out_license_percentage": out_license_percentage,
        "current_phase_cost": current_phase_cost,
    }


def get_cumulative_costs(inputs, phase):
    """Calculate cumulative costs up to and including the specified phase."""
    costs = inputs["costs"]
    cumulative_costs = 0

    phases = ["preclinical", "phase1", "phase2", "phase3", "registration"]
    phase_index = phases.index(phase)

    for i in range(phase_index + 1):
        cumulative_costs += costs[phases[i]]

    return cumulative_costs
