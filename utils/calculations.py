from typing import Dict, List, Union, Optional, Any, TypeVar, cast
from dataclasses import dataclass, field


@dataclass
class PhaseInputs:
    """Input parameters for phase value calculations.

    Attributes:
        launchValue: Peak sales value at launch in millions of dollars
        orderOfEntry: Market entry position ('first', 'second', 'third', 'later')
        discountRate: Annual discount rate for time value calculations (0-100)
        timeToMarket: Dict mapping phases to time to market in years
        costs: Dict mapping phases to R&D costs in millions
        probabilities: Dict mapping phases to success probabilities (0-100)
        includeRDCosts: Whether to include R&D costs in calculation
        dealStage: Current development stage code
        dealValue: Proposed deal value in millions
        desiredShare: Desired ownership percentage (0-100)
    """

    launchValue: float
    orderOfEntry: str
    discountRate: float
    timeToMarket: Dict[str, float]
    costs: Dict[str, float]
    probabilities: Dict[str, float]
    includeRDCosts: bool
    dealStage: str
    dealValue: float
    desiredShare: float


@dataclass
class PhaseValueResult:
    """Results of phase value calculation.

    Attributes:
        value: Risk-adjusted NPV for the phase in millions
        probability: Cumulative probability of success (0-100)
        discount_factor: Time value adjustment factor
        costs: Cumulative R&D costs if included in millions
    """

    value: float
    probability: float
    discount_factor: float
    costs: float


@dataclass
class OrderMultiplierResult:
    """Results of order multiplier calculation.

    Attributes:
        multiplier: Percentage of market value based on order of entry (0-100)
        description: Text description of the multiplier effect
    """

    multiplier: float
    description: str


@dataclass
class DealPercentagesResult:
    """Results of deal percentage calculations.

    Attributes:
        partnerShare: Partner's ownership percentage (0-100)
        companyShare: Company's retained percentage (0-100)
        valuePerShare: Value per 1% ownership in millions
        fairnessRatio: Ratio of deal value to phase value
    """

    partnerShare: float
    companyShare: float
    valuePerShare: float
    fairnessRatio: float


@dataclass
class StrategicDecisionResult:
    """Results of strategic decision analysis.

    Attributes:
        current_phase_value: Value at current phase in millions
        deal_now_value: Value from out-licensing now in millions
        continue_develop_value: Expected value from continued development in millions
        probability_next_phase: Probability of success in next phase (0-100)
        next_phase: Next development phase code or None if at registration
        out_license_percentage: Percentage to out-license (0-100)
        value_difference: Value difference between options in millions
        recommendation: Text recommendation based on analysis
    """

    current_phase_value: float
    deal_now_value: float
    continue_develop_value: float
    probability_next_phase: float
    next_phase: Optional[str]
    out_license_percentage: float
    value_difference: float
    recommendation: str


T = TypeVar("T")


def validate_inputs(inputs: Union[Dict, Any], cls: type) -> T:
    """Convert and validate inputs to the specified class type.

    Args:
        inputs: Dictionary or object containing input parameters
        cls: Target class type for validation

    Returns:
        Instance of the target class

    Raises:
        ValueError: If inputs are invalid or missing required fields
    """
    if isinstance(inputs, dict):
        try:
            if cls is PhaseInputs:
                return cast(
                    T,
                    PhaseInputs(
                        launchValue=inputs["launchValue"],
                        orderOfEntry=inputs["orderOfEntry"],
                        discountRate=inputs["discountRate"],
                        timeToMarket=inputs["timeToMarket"],
                        costs=inputs["costs"],
                        probabilities=inputs["probabilities"],
                        includeRDCosts=inputs["includeRDCosts"],
                        dealStage=inputs["dealStage"],
                        dealValue=inputs["dealValue"],
                        desiredShare=inputs["desiredShare"],
                    ),
                )
            else:
                raise ValueError(f"Unsupported class type: {cls.__name__}")
        except KeyError as e:
            raise ValueError(f"Missing required input parameter: {e}")

    # If already the correct type, return as is
    if isinstance(inputs, cls):
        return cast(T, inputs)

    raise ValueError(
        f"Invalid input type: {type(inputs).__name__}, expected {cls.__name__} or dict"
    )


def calculate_phase_value(
    inputs: Union[Dict, PhaseInputs], phase: str
) -> PhaseValueResult:
    """Calculate the Net Present Value (NPV) for a given development phase.

    Args:
        inputs (Union[Dict, PhaseInputs]): Dictionary or dataclass containing valuation inputs including:
            - launchValue: Peak sales value at launch (in millions)
            - orderOfEntry: Market entry position (first, second, third, later)
            - discountRate: Annual discount rate for time value calculations (0-100)
            - timeToMarket: Dict of time to market for each phase (in years)
            - costs: Dict of R&D costs for each phase (in millions)
            - probabilities: Dict of success probabilities for each phase (0-100)
            - includeRDCosts: Whether to include R&D costs in calculation
        phase (str): Development phase to calculate value for (preclinical, phase1, etc.)

    Returns:
        PhaseValueResult: Dictionary containing:
            - value: Risk-adjusted NPV for the phase (in millions)
            - probability: Cumulative probability of success (0-100)
            - discount_factor: Time value adjustment factor
            - costs: Cumulative R&D costs if included (in millions)

    Raises:
        ValueError: If discount rate is negative or greater than 100
        ValueError: If time to market is negative
        ZeroDivisionError: If discount factor calculation would result in division by zero
    """
    # Validate inputs and convert to PhaseInputs
    phase_inputs = validate_inputs(inputs, PhaseInputs)

    # Validate parameters
    if phase_inputs.discountRate < 0 or phase_inputs.discountRate > 100:
        raise ValueError("Discount rate must be between 0 and 100")

    if phase_inputs.timeToMarket[phase] < 0:
        raise ValueError("Time to market cannot be negative")

    # Calculate base value
    base_value = (
        phase_inputs.launchValue
        * calculate_order_multiplier(phase_inputs.orderOfEntry).multiplier
    )

    # Calculate probability
    probability = calculate_cumulative_probability(phase_inputs, phase)

    # Calculate discount factor
    try:
        discount_factor = (
            1 + (phase_inputs.discountRate / 100)
        ) ** phase_inputs.timeToMarket[phase]
    except Exception:
        raise ValueError("Invalid discount rate calculation")

    # Calculate phase value
    phase_value = (base_value * probability / 100) / discount_factor
    costs = 0.0

    # Add R&D costs if needed
    if phase_inputs.includeRDCosts:
        costs = sum(phase_inputs.costs[p] for p in get_phases_up_to(phase))
        phase_value -= costs

    return PhaseValueResult(
        value=phase_value,
        probability=probability,
        discount_factor=discount_factor,
        costs=costs,
    )


def calculate_order_multiplier(order: str) -> OrderMultiplierResult:
    """Calculate the market value multiplier based on order of market entry.

    Args:
        order (str): Market entry position ('first', 'second', 'third', 'later')

    Returns:
        OrderMultiplierResult: Dictionary containing:
            - multiplier: Value between 0 and 1 representing market share discount
            - description: Text description of the multiplier effect

    Raises:
        ValueError: If invalid order position is provided
    """
    multipliers = {
        "first": (1.0, "100% for first-in-class"),
        "second": (0.67, "67% for second-in-class"),
        "third": (0.5, "50% for third-in-class"),
        "later": (0.3, "30% for later entrants"),
    }

    if order not in multipliers:
        raise ValueError(
            f"Invalid order position: {order}. Must be one of {list(multipliers.keys())}"
        )

    value, description = multipliers[order]
    return OrderMultiplierResult(multiplier=value, description=description)


def calculate_cumulative_probability(
    inputs: Union[Dict, PhaseInputs], phase: str
) -> float:
    """Calculate the cumulative probability of success up to a given phase.

    Args:
        inputs (Union[Dict, PhaseInputs]): Dictionary or dataclass containing valuation inputs
        phase (str): Target development phase

    Returns:
        float: Product of success probabilities (0-100) for all phases up to target

    Raises:
        ValueError: If any probability is outside valid range (0-100)
    """
    # Validate inputs and convert to PhaseInputs
    phase_inputs = validate_inputs(inputs, PhaseInputs)

    phases = get_phases_up_to(phase)
    probabilities = [phase_inputs.probabilities[p] for p in phases]

    for prob in probabilities:
        if not 0 <= prob <= 100:
            raise ValueError(
                f"Invalid probability value: {prob}. Must be between 0 and 100"
            )

    # Convert percentages to decimals for multiplication
    prob_decimals = [p / 100 for p in probabilities]

    # Calculate product of probabilities
    return product(prob_decimals) * 100


def get_cumulative_probability(inputs: PhaseInputs, phase: str) -> float:
    """Calculate the cumulative probability of success up to a given phase.

    Args:
        inputs (PhaseInputs): Dictionary containing valuation inputs
        phase (str): Target development phase

    Returns:
        float: Product of success probabilities for all phases up to and including
            the target phase
    """
    phases = get_phases_up_to(phase)
    return product([inputs.probabilities[p] for p in phases])


def get_order_multiplier(inputs: PhaseInputs, order: str) -> float:
    """Calculate the market value multiplier based on order of market entry.

    Args:
        inputs (PhaseInputs): Dictionary containing valuation inputs
        order (str): Market entry position (first, second, third, later)

    Returns:
        float: Multiplier value between 0 and 1 representing market share discount:
            - first: 1.0 (100% of market value)
            - second: 0.67 (67% of market value)
            - third: 0.5 (50% of market value)
            - later: 0.3 (30% of market value)
    """
    multipliers = {
        "first": 1.0,  # 100% for first-in-class
        "second": 0.67,  # 67% for second-in-class
        "third": 0.5,  # 50% for third-in-class
        "later": 0.3,  # 30% for later entrants
    }
    return multipliers.get(order, 1.0)


def get_phases_up_to(phase: str) -> List[str]:
    """Get list of development phases up to and including the target phase.

    Args:
        phase (str): Target development phase

    Returns:
        List[str]: Ordered list of phases from preclinical up to target phase
    """
    all_phases = ["preclinical", "phase1", "phase2", "phase3", "registration"]

    try:
        phase_index = all_phases.index(phase)
    except ValueError:
        raise ValueError(f"Invalid phase: {phase}. Must be one of {all_phases}")

    return all_phases[: phase_index + 1]


def product(numbers: List[Union[int, float]]) -> float:
    """Calculate the product of a list of numbers.

    Args:
        numbers (List[Union[int, float]]): List of numbers to multiply together

    Returns:
        float: Product of all numbers in the input list
    """
    result = 1.0
    for n in numbers:
        result *= n
    return result


def calculate_deal_percentages(
    inputs: Union[Dict, PhaseInputs],
) -> DealPercentagesResult:
    """Calculate ownership percentages and deal metrics based on deal parameters.

    Args:
        inputs (Union[Dict, PhaseInputs]): Dictionary or dataclass containing valuation inputs including:
            - dealStage: Current development stage
            - dealValue: Proposed deal value (in millions)
            - desiredShare: Desired ownership percentage (0-100)
            - Other standard PhaseInputs fields

    Returns:
        DealPercentagesResult: Dictionary containing:
            - partnerShare: Partner's ownership percentage (0-100)
            - companyShare: Company's retained percentage (0-100)
            - valuePerShare: Value per 1% ownership (in millions)
            - fairnessRatio: Ratio of deal value to phase value

    Raises:
        ValueError: If deal value is negative
        ValueError: If desired share is outside valid range (0-100)
    """
    # Validate inputs and convert to PhaseInputs
    phase_inputs = validate_inputs(inputs, PhaseInputs)

    # Validate parameters
    if phase_inputs.dealValue < 0:
        raise ValueError("Deal value cannot be negative")
    if not 0 <= phase_inputs.desiredShare <= 100:
        raise ValueError("Desired share must be between 0 and 100")

    # Calculate phase value at deal stage
    phase_result = calculate_phase_value(phase_inputs, phase_inputs.dealStage)
    phase_value = phase_result.value

    # Calculate ownership percentages
    if phase_value > 0:
        partner_share = (phase_inputs.dealValue / phase_value) * 100
        partner_share = min(max(round(partner_share, 1), 0), 100)
    else:
        partner_share = phase_inputs.desiredShare

    company_share = 100 - partner_share
    value_per_share = phase_value / 100 if phase_value > 0 else 0
    fairness_ratio = phase_inputs.dealValue / phase_value if phase_value > 0 else 0

    return DealPercentagesResult(
        partnerShare=partner_share,
        companyShare=company_share,
        valuePerShare=value_per_share,
        fairnessRatio=fairness_ratio,
    )


def calculate_required_deal_value(
    inputs: Union[Dict, PhaseInputs], desired_share: float
) -> float:
    """Calculate the required deal value to achieve a desired ownership percentage.

    Args:
        inputs (Union[Dict, PhaseInputs]): Dictionary or dataclass containing valuation inputs
        desired_share (float): Target ownership percentage (0-100)

    Returns:
        float: Required deal value in millions to achieve desired ownership

    Raises:
        ValueError: If desired share is outside valid range (0-100)
    """
    # Validate inputs and convert to PhaseInputs
    phase_inputs = validate_inputs(inputs, PhaseInputs)

    # Validate parameters
    if not 0 <= desired_share <= 100:
        raise ValueError("Desired share must be between 0 and 100")

    # Calculate phase value
    phase_result = calculate_phase_value(phase_inputs, phase_inputs.dealStage)
    return (desired_share / 100) * phase_result.value


def calculate_strategic_decision(
    inputs: Union[Dict, PhaseInputs], current_stage: str, out_license_percentage: float
) -> StrategicDecisionResult:
    """Calculate metrics for strategic decision between development and out-licensing.

    Args:
        inputs (Union[Dict, PhaseInputs]): Dictionary or dataclass containing valuation inputs
        current_stage (str): Current development stage
        out_license_percentage (float): Percentage to out-license (0-100)

    Returns:
        StrategicDecisionResult: Dictionary containing:
            - current_phase_value: Value at current phase (in millions)
            - deal_now_value: Value from out-licensing now (in millions)
            - continue_develop_value: Expected value from continued development (in millions)
            - probability_next_phase: Probability of success in next phase (0-100)
            - next_phase: Next development phase code (or None if at registration)
            - out_license_percentage: Percentage to out-license (0-100)
            - value_difference: Value difference between options (in millions)
            - recommendation: Text recommendation based on analysis

    Raises:
        ValueError: If out_license_percentage is outside valid range (0-100)
        ValueError: If current_stage is not valid
    """
    # Validate inputs and convert to PhaseInputs
    phase_inputs = validate_inputs(inputs, PhaseInputs)

    # Validate parameters
    if not 0 <= out_license_percentage <= 100:
        raise ValueError("Out-license percentage must be between 0 and 100")

    # Get current and next phase values
    current_result = calculate_phase_value(phase_inputs, current_stage)
    current_value = current_result.value

    # Determine next phase
    all_phases = ["preclinical", "phase1", "phase2", "phase3", "registration"]
    try:
        current_index = all_phases.index(current_stage)
        next_phase = (
            all_phases[current_index + 1]
            if current_index < len(all_phases) - 1
            else None
        )
    except ValueError:
        raise ValueError(f"Invalid current stage: {current_stage}")

    # Calculate values for each option
    if next_phase:
        next_result = calculate_phase_value(phase_inputs, next_phase)
        next_value = next_result.value
        probability = phase_inputs.probabilities[current_stage]
        continue_value = next_value * (probability / 100)
    else:
        next_value = 0
        probability = 0
        continue_value = 0

    # Calculate deal now value (includes retained upside)
    deal_value = (out_license_percentage / 100) * current_value
    retained_value = ((100 - out_license_percentage) / 100) * current_value
    deal_now_value = deal_value + retained_value

    # Calculate value difference and determine recommendation
    value_difference = continue_value - deal_now_value
    recommendation = (
        "Continue Development"
        if value_difference > 0
        else "Out-License Now" if value_difference < 0 else "Either Option Viable"
    )

    return StrategicDecisionResult(
        current_phase_value=current_value,
        deal_now_value=deal_now_value,
        continue_develop_value=continue_value,
        probability_next_phase=probability,
        next_phase=next_phase,
        out_license_percentage=out_license_percentage,
        value_difference=value_difference,
        recommendation=recommendation,
    )
