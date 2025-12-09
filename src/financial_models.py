"""Financial modeling and analysis for PV projects."""
import numpy as np
import numpy_financial as npf
import pandas as pd
from typing import Dict, Tuple
from dataclasses import dataclass


@dataclass
class FinancialInputs:
    """Container for financial model inputs."""

    system_capacity_kw: float
    total_capex: float
    annual_production_kwh: float
    electricity_rate_kwh: float
    opex_annual: float
    escalation_rate: float
    discount_rate: float
    project_lifetime_years: int
    incentives_total: float = 0.0
    degradation_rate: float = 0.005  # 0.5% per year


def calculate_npv(cash_flows: np.ndarray, discount_rate: float) -> float:
    """
    Calculate Net Present Value.

    Args:
        cash_flows: Array of annual cash flows
        discount_rate: Discount rate (e.g., 0.06 for 6%)

    Returns:
        NPV in currency units
    """
    years = np.arange(len(cash_flows))
    discount_factors = (1 + discount_rate) ** years
    present_values = cash_flows / discount_factors
    return float(np.sum(present_values))


def calculate_irr(cash_flows: np.ndarray, initial_guess: float = 0.1) -> float:
    """
    Calculate Internal Rate of Return.

    Args:
        cash_flows: Array of annual cash flows (including initial investment)
        initial_guess: Starting guess for IRR calculation

    Returns:
        IRR as decimal (e.g., 0.12 for 12%)
    """
    return float(npf.irr(cash_flows))


def calculate_payback_period(cash_flows: np.ndarray) -> float:
    """
    Calculate simple payback period.

    Args:
        cash_flows: Array of annual cash flows

    Returns:
        Payback period in years
    """
    cumulative_cash_flow = np.cumsum(cash_flows)

    if not np.any(cumulative_cash_flow >= 0):
        return float("inf")  # Never pays back

    payback_index = np.where(cumulative_cash_flow >= 0)[0][0]

    if payback_index == 0:
        return 0.0

    # Linear interpolation for fractional year
    prev_cumulative = cumulative_cash_flow[payback_index - 1]
    curr_cash_flow = cash_flows[payback_index]

    fraction = abs(prev_cumulative) / curr_cash_flow
    payback_period = payback_index + fraction

    return float(payback_period)


def calculate_lcoe(
    total_capex: float,
    opex_annual: float,
    annual_production_kwh: float,
    discount_rate: float,
    lifetime_years: int,
    degradation_rate: float = 0.005,
) -> float:
    """
    Calculate Levelized Cost of Energy.

    Args:
        total_capex: Total capital expenditure
        opex_annual: Annual operating expenses
        annual_production_kwh: First year energy production
        discount_rate: Discount rate
        lifetime_years: Project lifetime in years
        degradation_rate: Annual degradation rate

    Returns:
        LCOE in currency per kWh
    """
    years = np.arange(lifetime_years)

    # Production degrades each year
    production = annual_production_kwh * (1 - degradation_rate) ** years

    # Discount factors
    discount_factors = (1 + discount_rate) ** years

    # Present value of costs
    pv_costs = total_capex + np.sum(opex_annual / discount_factors)

    # Present value of production
    pv_production = np.sum(production / discount_factors)

    lcoe = pv_costs / pv_production

    return float(lcoe)


def run_financial_model(inputs: FinancialInputs) -> Dict[str, float]:
    """
    Run complete financial model for PV project.

    Args:
        inputs: FinancialInputs dataclass with all parameters

    Returns:
        Dictionary with financial metrics
    """

    # Year 0: Initial investment (negative cash flow)
    cash_flows = np.zeros(inputs.project_lifetime_years + 1)
    cash_flows[0] = -(inputs.total_capex - inputs.incentives_total)

    # Years 1-N: Revenue minus OPEX
    for year in range(1, inputs.project_lifetime_years + 1):
        # Production degrades each year
        production = inputs.annual_production_kwh * (1 - inputs.degradation_rate) ** (
            year - 1
        )

        # Electricity rate escalates
        electricity_rate = inputs.electricity_rate_kwh * (
            1 + inputs.escalation_rate
        ) ** (year - 1)

        # Revenue from energy savings/sales
        revenue = production * electricity_rate

        # Operating expenses
        opex = inputs.opex_annual * (1 + inputs.escalation_rate) ** (year - 1)

        # Net cash flow
        cash_flows[year] = revenue - opex

    # Calculate metrics
    npv = calculate_npv(cash_flows, inputs.discount_rate)
    irr = calculate_irr(cash_flows) if npv > 0 else 0.0
    payback = calculate_payback_period(cash_flows)
    lcoe = calculate_lcoe(
        inputs.total_capex,
        inputs.opex_annual,
        inputs.annual_production_kwh,
        inputs.discount_rate,
        inputs.project_lifetime_years,
        inputs.degradation_rate,
    )

    # Calculate ROI
    total_revenue = np.sum(cash_flows[1:])
    roi = (total_revenue / inputs.total_capex) * 100

    # First year savings
    year1_savings = cash_flows[1]

    # Lifetime savings
    lifetime_savings = np.sum(cash_flows[1:])

    return {
        "npv": round(npv, 2),
        "irr": round(irr * 100, 2),  # Convert to percentage
        "payback_period_years": round(payback, 2),
        "lcoe": round(lcoe, 4),
        "roi_percentage": round(roi, 2),
        "annual_savings_year1": round(year1_savings, 2),
        "total_lifetime_savings": round(lifetime_savings, 2),
        "total_revenue": round(total_revenue, 2),
    }


def sensitivity_analysis(
    inputs: FinancialInputs,
    parameter: str,
    variation_range: Tuple[float, float],
    num_points: int = 10,
) -> pd.DataFrame:
    """
    Perform sensitivity analysis on a single parameter.

    Args:
        inputs: Base case financial inputs
        parameter: Parameter name to vary (e.g., 'electricity_rate_kwh')
        variation_range: (min_multiplier, max_multiplier) e.g., (0.8, 1.2) for ±20%
        num_points: Number of points to calculate

    Returns:
        DataFrame with sensitivity results
    """
    base_value = getattr(inputs, parameter)
    multipliers = np.linspace(variation_range[0], variation_range[1], num_points)

    results = []
    for mult in multipliers:
        # Create modified inputs
        modified_inputs = FinancialInputs(**vars(inputs))
        setattr(modified_inputs, parameter, base_value * mult)

        # Run model
        metrics = run_financial_model(modified_inputs)

        results.append(
            {
                "parameter_value": base_value * mult,
                "multiplier": mult,
                "npv": metrics["npv"],
                "irr": metrics["irr"],
                "payback_period": metrics["payback_period_years"],
            }
        )

    return pd.DataFrame(results)


def scenario_comparison(
    base_inputs: FinancialInputs, scenarios: Dict[str, Dict[str, float]]
) -> pd.DataFrame:
    """
    Compare multiple scenarios.

    Args:
        base_inputs: Base case inputs
        scenarios: Dict of scenario_name: {parameter: value} modifications

    Returns:
        DataFrame comparing all scenarios
    """
    results = []

    # Base case
    base_metrics = run_financial_model(base_inputs)
    base_metrics["scenario"] = "Base Case"
    results.append(base_metrics)

    # Alternative scenarios
    for scenario_name, modifications in scenarios.items():
        modified_inputs = FinancialInputs(**vars(base_inputs))

        for param, value in modifications.items():
            setattr(modified_inputs, param, value)

        metrics = run_financial_model(modified_inputs)
        metrics["scenario"] = scenario_name
        results.append(metrics)

    df = pd.DataFrame(results)
    return df[
        ["scenario", "npv", "irr", "payback_period_years", "lcoe", "roi_percentage"]
    ]
