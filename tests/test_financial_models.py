"""Tests for financial models module."""
import pytest
import numpy as np
from src.financial_models import (
    FinancialInputs,
    calculate_npv,
    calculate_irr,
    calculate_payback_period,
    calculate_lcoe,
    run_financial_model,
)


def test_calculate_npv():
    """Test NPV calculation."""
    cash_flows = np.array([-10000, 2000, 2000, 2000, 2000, 2000])
    npv = calculate_npv(cash_flows, discount_rate=0.06)

    assert isinstance(npv, float)
    assert npv > -10000  # Should be less negative than initial investment


def test_calculate_irr():
    """Test IRR calculation."""
    cash_flows = np.array([-10000, 3000, 3000, 3000, 3000])
    irr = calculate_irr(cash_flows)

    assert isinstance(irr, float)
    assert 0 < irr < 1  # Should be between 0 and 100%


def test_calculate_payback_period():
    """Test payback period calculation."""
    cash_flows = np.array([-10000, 3000, 3000, 3000, 3000, 3000])
    payback = calculate_payback_period(cash_flows)

    assert isinstance(payback, float)
    assert 3 < payback < 4  # Should pay back between year 3 and 4


def test_calculate_lcoe():
    """Test LCOE calculation."""
    lcoe = calculate_lcoe(
        total_capex=15000,
        opex_annual=200,
        annual_production_kwh=12000,
        discount_rate=0.06,
        lifetime_years=25,
    )

    assert isinstance(lcoe, float)
    assert lcoe > 0
    assert lcoe < 1  # Should be reasonable $/kWh


def test_run_financial_model():
    """Test complete financial model."""
    inputs = FinancialInputs(
        system_capacity_kw=10.0,
        total_capex=15000,
        annual_production_kwh=14000,
        electricity_rate_kwh=0.12,
        opex_annual=200,
        escalation_rate=0.02,
        discount_rate=0.06,
        project_lifetime_years=25,
        incentives_total=3000,
    )

    results = run_financial_model(inputs)

    assert "npv" in results
    assert "irr" in results
    assert "payback_period_years" in results
    assert "lcoe" in results
    assert isinstance(results["npv"], float)
    assert results["irr"] > 0


@pytest.fixture
def sample_financial_inputs():
    """Fixture providing sample financial inputs."""
    return FinancialInputs(
        system_capacity_kw=50.0,
        total_capex=75000,
        annual_production_kwh=70000,
        electricity_rate_kwh=0.15,
        opex_annual=1000,
        escalation_rate=0.025,
        discount_rate=0.07,
        project_lifetime_years=25,
    )


def test_financial_model_with_fixture(sample_financial_inputs):
    """Test financial model using fixture."""
    results = run_financial_model(sample_financial_inputs)

    assert results["npv"] > 0  # Should be profitable
    assert results["payback_period_years"] < 25  # Should pay back within lifetime
