"""Solar PV system calculations and modeling."""
import numpy as np
import pandas as pd
from typing import Dict
import pvlib
from pvlib import location


def calculate_solar_position(
    latitude: float, longitude: float, date_range: pd.DatetimeIndex
) -> pd.DataFrame:
    """
    Calculate solar position for given location and time range.

    Args:
        latitude: Location latitude in degrees
        longitude: Location longitude in degrees
        date_range: pandas DatetimeIndex for calculation period

    Returns:
        DataFrame with solar position data (zenith, azimuth, elevation)
    """
    site = location.Location(latitude, longitude, tz="UTC")
    solar_position = site.get_solarposition(date_range)
    return solar_position


def estimate_annual_production(
    system_capacity_kw: float,
    latitude: float,
    longitude: float,
    tilt: float,
    azimuth: float,
    module_efficiency: float = 0.20,
    performance_ratio: float = 0.75,
) -> Dict[str, float]:
    """
    Estimate annual energy production for a PV system.

    Args:
        system_capacity_kw: System capacity in kW
        latitude: Site latitude
        longitude: Site longitude
        tilt: Panel tilt angle in degrees
        azimuth: Panel azimuth in degrees (180 = south)
        module_efficiency: Module efficiency (default 20%)
        performance_ratio: System performance ratio (default 0.75)

    Returns:
        Dictionary with production estimates
    """
    # Create location
    site = location.Location(latitude, longitude, tz="UTC")

    # Create simple time range for one year
    times = pd.date_range("2024-01-01", "2024-12-31 23:00:00", freq="h", tz=site.tz)

    # Get solar position and clearsky irradiance
    solar_position = site.get_solarposition(times)
    clearsky = site.get_clearsky(times)

    # Simple POA (Plane of Array) calculation
    poa_irradiance = pvlib.irradiance.get_total_irradiance(
        surface_tilt=tilt,
        surface_azimuth=azimuth,
        dni=clearsky["dni"],
        ghi=clearsky["ghi"],
        dhi=clearsky["dhi"],
        solar_zenith=solar_position["apparent_zenith"],
        solar_azimuth=solar_position["azimuth"],
    )

    # Calculate DC power output (simplified)
    poa_global = poa_irradiance["poa_global"]
    dc_power = system_capacity_kw * (poa_global / 1000) * performance_ratio

    # Annual production
    annual_production_kwh = dc_power.sum()

    # Monthly breakdown
    monthly_production = dc_power.resample("ME").sum()

    return {
        "annual_production_kwh": float(annual_production_kwh),
        "average_daily_kwh": float(annual_production_kwh / 365),
        "peak_month": monthly_production.idxmax().strftime("%B"),
        "peak_month_kwh": float(monthly_production.max()),
        "capacity_factor": float(annual_production_kwh / (system_capacity_kw * 8760)),
    }


def calculate_system_size(
    energy_demand_kwh_year: float,
    latitude: float,
    longitude: float,
    performance_ratio: float = 0.75,
) -> float:
    """
    Calculate required system size to meet energy demand.

    Args:
        energy_demand_kwh_year: Annual energy demand in kWh
        latitude: Site latitude
        longitude: Site longitude
        performance_ratio: Expected system performance ratio

    Returns:
        Required system capacity in kW"""
    # Estimate peak sun hours for location (simplified)
    # Using average values based on latitude
    if abs(latitude) < 30:
        peak_sun_hours = 5.5
    elif abs(latitude) < 40:
        peak_sun_hours = 4.5
    elif abs(latitude) < 50:
        peak_sun_hours = 3.5
    else:
        peak_sun_hours = 3.0

    # Calculate system size
    system_size_kw = energy_demand_kwh_year / (365 * peak_sun_hours * performance_ratio)

    return round(system_size_kw, 2)


def calculate_array_size(
    system_capacity_kw: float,
    module_power_w: int = 400,
    module_efficiency: float = 0.20,
) -> Dict[str, float]:
    """
    Calculate physical array dimensions.

    Args:
        system_capacity_kw: System capacity in kW
        module_power_w: Individual module power rating in watts
        module_efficiency: Module efficiency

    Returns:
        Dictionary with array sizing information
    """
    system_capacity_w = system_capacity_kw * 1000
    num_modules = int(np.ceil(system_capacity_w / module_power_w))

    # Typical module dimensions (meters)
    module_length = 2.0
    module_width = 1.0
    module_area = module_length * module_width

    total_area_m2 = num_modules * module_area
    total_area_ft2 = total_area_m2 * 10.764

    return {
        "num_modules": num_modules,
        "total_area_m2": round(total_area_m2, 2),
        "total_area_ft2": round(total_area_ft2, 2),
        "module_power_w": module_power_w,
        "actual_system_capacity_kw": round(num_modules * module_power_w / 1000, 2),
    }
