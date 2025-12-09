"""Tests for solar calculations module."""
import pandas as pd
from src.solar_calculations import (
    calculate_solar_position,
    estimate_annual_production,
    calculate_system_size,
    calculate_array_size,
)


def test_calculate_solar_position():
    """Test solar position calculation."""
    latitude, longitude = 33.4484, -112.0740  # Phoenix, AZ
    date_range = pd.date_range("2024-01-01 12:00", periods=1, freq="h", tz="UTC")

    result = calculate_solar_position(latitude, longitude, date_range)

    assert isinstance(result, pd.DataFrame)
    assert "zenith" in result.columns
    assert "azimuth" in result.columns
    assert len(result) == 1


def test_estimate_annual_production():
    """Test annual production estimation."""
    result = estimate_annual_production(
        system_capacity_kw=10.0,
        latitude=33.4484,
        longitude=-112.0740,
        tilt=25.0,
        azimuth=180.0,
    )

    assert "annual_production_kwh" in result
    assert result["annual_production_kwh"] > 0
    assert result["capacity_factor"] > 0
    assert result["capacity_factor"] < 1


def test_calculate_system_size():
    """Test system sizing calculation."""
    energy_demand = 12000  # kWh/year
    size = calculate_system_size(
        energy_demand_kwh_year=energy_demand, latitude=33.4484, longitude=-112.0740
    )

    assert size > 0
    assert isinstance(size, float)


def test_calculate_array_size():
    """Test array sizing calculation."""
    result = calculate_array_size(system_capacity_kw=10.0, module_power_w=400)

    assert result["num_modules"] == 25
    assert result["total_area_m2"] > 0
    assert result["actual_system_capacity_kw"] == 10.0
