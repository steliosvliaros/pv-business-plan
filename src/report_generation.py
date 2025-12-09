"""Report generation utilities for PV business plans."""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List
from fpdf import FPDF
from datetime import datetime


class PVBusinessPlanPDF(FPDF):
    """Custom PDF class for PV business plan reports."""

    def __init__(self, project_name: str):
        super().__init__()
        self.project_name = project_name

    def header(self):
        """Page header."""
        self.set_font("Arial", "B", 15)
        self.cell(0, 10, f"PV Business Plan: {self.project_name}", 0, 1, "C")
        self.ln(5)

    def footer(self):
        """Page footer."""
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")

    def chapter_title(self, title: str):
        """Add chapter title."""
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, title, 0, 1, "L")
        self.ln(2)

    def chapter_body(self, body: str):
        """Add chapter body text."""
        self.set_font("Arial", "", 11)
        self.multi_cell(0, 5, body)
        self.ln()


def generate_executive_summary_pdf(
    project_data: Dict, financial_results: Dict, output_path: Path
) -> Path:
    """
    Generate executive summary PDF report.

    Args:
        project_data: Project information dictionary
        financial_results: Financial analysis results
        output_path: Path to save PDF

    Returns:
        Path to generated PDF
    """
    pdf = PVBusinessPlanPDF(project_data["project_name"])
    pdf.add_page()

    # Executive Summary
    pdf.chapter_title("Executive Summary")
    summary_text = f"""
Project: {project_data['project_name']}
Location: {project_data['location']}
System Capacity: {project_data['system_capacity_kw']:.2f} kW
Estimated Annual Production: {project_data['annual_production_kwh']:,.0f} kWh

This photovoltaic (PV) system represents a compelling investment opportunity
with strong financial returns and environmental benefits.
"""
    pdf.chapter_body(summary_text)

    # Financial Highlights
    pdf.chapter_title("Financial Highlights")
    financial_text = f"""
Total Investment: ${project_data['total_capex']:,.2f}
Net Present Value (NPV): ${financial_results['npv']:,.2f}
Internal Rate of Return (IRR): {financial_results['irr']:.2f}%
Payback Period: {financial_results['payback_period_years']:.1f} years
Levelized Cost of Energy (LCOE): ${financial_results['lcoe']:.4f}/kWh
Return on Investment: {financial_results['roi_percentage']:.2f}%

First Year Savings: ${financial_results['annual_savings_year1']:,.2f}
25-Year Lifetime Savings: ${financial_results['total_lifetime_savings']:,.2f}
"""
    pdf.chapter_body(financial_text)

    # Recommendation
    pdf.chapter_title("Recommendation")
    if financial_results["npv"] > 0 and financial_results["irr"] > 8:
        recommendation = """STRONGLY RECOMMENDED
        - This project demonstrates excellent financial viability."""
    elif financial_results["npv"] > 0:
        recommendation = "RECOMMENDED - This project shows positive returns."
    else:
        recommendation = "REQUIRES REVIEW - Financial returns may be marginal."

    pdf.chapter_body(recommendation)

    # Save
    output_file = (
        output_path
        / f"executive_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    )
    pdf.output(str(output_file))

    return output_file


def create_financial_charts(
    financial_data: Dict, cash_flows: pd.Series, output_dir: Path
) -> List[Path]:
    """
    Create financial analysis charts.

    Args:
        financial_data: Financial metrics dictionary
        cash_flows: Series of annual cash flows
        output_dir: Directory to save charts

    Returns:
        List of paths to generated charts
    """
    sns.set_style("whitegrid")
    chart_paths = []

    # 1. Cash Flow Chart
    fig, ax = plt.subplots(figsize=(10, 6))
    years = range(len(cash_flows))
    ax.bar(years, cash_flows, color=["red" if x < 0 else "green" for x in cash_flows])
    ax.axhline(y=0, color="black", linestyle="-", linewidth=0.5)
    ax.set_xlabel("Year")
    ax.set_ylabel("Cash Flow ($)")
    ax.set_title("Annual Cash Flows")
    ax.grid(True, alpha=0.3)

    chart_path = output_dir / "cash_flow_chart.png"
    plt.tight_layout()
    plt.savefig(chart_path, dpi=300, bbox_inches="tight")
    plt.close()
    chart_paths.append(chart_path)

    # 2. Cumulative Cash Flow
    fig, ax = plt.subplots(figsize=(10, 6))
    cumulative = cash_flows.cumsum()
    ax.plot(years, cumulative, marker="o", linewidth=2, markersize=4)
    ax.axhline(y=0, color="red", linestyle="--", linewidth=1, label="Break-even")
    ax.fill_between(
        years, cumulative, 0, where=(cumulative >= 0), alpha=0.3, color="green"
    )
    ax.set_xlabel("Year")
    ax.set_ylabel("Cumulative Cash Flow ($)")
    ax.set_title("Cumulative Cash Flow (Payback Analysis)")
    ax.legend()
    ax.grid(True, alpha=0.3)

    chart_path = output_dir / "cumulative_cash_flow.png"
    plt.tight_layout()
    plt.savefig(chart_path, dpi=300, bbox_inches="tight")
    plt.close()
    chart_paths.append(chart_path)

    # 3. Key Metrics Dashboard
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    # NPV
    axes[0, 0].bar(
        ["NPV"],
        [financial_data["npv"]],
        color="green" if financial_data["npv"] > 0 else "red",
    )
    axes[0, 0].set_title("Net Present Value")
    axes[0, 0].set_ylabel("$ (thousands)")
    axes[0, 0].axhline(y=0, color="black", linestyle="-", linewidth=0.5)

    # IRR
    axes[0, 1].bar(["IRR"], [financial_data["irr"]], color="blue")
    axes[0, 1].set_title("Internal Rate of Return")
    axes[0, 1].set_ylabel("Percentage (%)")
    axes[0, 1].axhline(y=0, color="black", linestyle="-", linewidth=0.5)

    # Payback Period
    axes[1, 0].barh(
        ["Payback"], [financial_data["payback_period_years"]], color="orange"
    )
    axes[1, 0].set_title("Payback Period")
    axes[1, 0].set_xlabel("Years")

    # ROI
    axes[1, 1].bar(["ROI"], [financial_data["roi_percentage"]], color="purple")
    axes[1, 1].set_title("Return on Investment")
    axes[1, 1].set_ylabel("Percentage (%)")

    chart_path = output_dir / "key_metrics_dashboard.png"
    plt.tight_layout()
    plt.savefig(chart_path, dpi=300, bbox_inches="tight")
    plt.close()
    chart_paths.append(chart_path)

    return chart_paths


def export_financial_model_excel(
    project_data: Dict,
    financial_results: Dict,
    cash_flows: pd.DataFrame,
    output_path: Path,
) -> Path:
    """
    Export financial model to Excel.

    Args:
        project_data: Project information
        financial_results: Financial metrics
        cash_flows: DataFrame with detailed cash flows
        output_path: Path to save Excel file

    Returns:
        Path to generated Excel file
    """
    output_file = (
        output_path / f"financial_model_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    )

    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        # Summary sheet
        summary_df = pd.DataFrame(
            [
                {"Metric": "Project Name", "Value": project_data["project_name"]},
                {"Metric": "Location", "Value": project_data["location"]},
                {
                    "Metric": "System Capacity (kW)",
                    "Value": project_data["system_capacity_kw"],
                },
                {"Metric": "", "Value": ""},
                {
                    "Metric": "Total Investment",
                    "Value": f"${project_data['total_capex']:,.2f}",
                },
                {"Metric": "NPV", "Value": f"${financial_results['npv']:,.2f}"},
                {"Metric": "IRR", "Value": f"{financial_results['irr']:.2f}%"},
                {
                    "Metric": "Payback Period (years)",
                    "Value": financial_results["payback_period_years"],
                },
                {
                    "Metric": "LCOE ($/kWh)",
                    "Value": f"${financial_results['lcoe']:.4f}",
                },
                {
                    "Metric": "ROI",
                    "Value": f"{financial_results['roi_percentage']:.2f}%",
                },
            ]
        )
        summary_df.to_excel(writer, sheet_name="Summary", index=False)

        # Cash flows sheet
        cash_flows.to_excel(writer, sheet_name="Cash Flows", index=False)

        # Assumptions sheet
        assumptions_df = pd.DataFrame(
            [
                {
                    "Parameter": "Electricity Rate ($/kWh)",
                    "Value": project_data.get("electricity_rate", "N/A"),
                },
                {
                    "Parameter": "Escalation Rate",
                    "Value": project_data.get("escalation_rate", "N/A"),
                },
                {
                    "Parameter": "Discount Rate",
                    "Value": project_data.get("discount_rate", "N/A"),
                },
                {
                    "Parameter": "Project Lifetime (years)",
                    "Value": project_data.get("lifetime", 25),
                },
            ]
        )
        assumptions_df.to_excel(writer, sheet_name="Assumptions", index=False)

    return output_file
