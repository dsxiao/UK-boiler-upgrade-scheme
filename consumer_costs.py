import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

plt.rcParams["font.family"] = "Times New Roman"
chart_dir = Path("consumer-cost-outputs")
chart_dir.mkdir(exist_ok=True)

# Inputs
heat_pump_ic = 12850     
heat_pump_grant = 7500                  
gas_boiler_ic = 3500    
heat_pump_mc = 200
gas_boiler_mc = 100
electricity_rate = 26.32  
gas_rate = 7.97            
heat_demand_yearly = 8550           
heat_pump_efficiency = 3.73                        
gas_boiler_efficiency = 0.90
gas_emissions = 0.18231     
electricity_emissions = 0.13096
heat_pump_lifetime = 18
discount_rate = 0.035

# Model
def present_value_factor(discount_rate, years):
    '''Converts a constant yearly cost into its present value (annuity factor)'''
    return (1 - (1 + discount_rate) ** -years) / discount_rate

def household_costs(
        electricity_rate_pence=electricity_rate,
        gas_rate_pence=gas_rate,
        scop=heat_pump_efficiency,
        heat_pump_install_gbp=heat_pump_ic,
        gas_boiler_install_gbp=gas_boiler_ic,
        grant_gbp=heat_pump_grant):
    '''Returns costs and emissions for one scenario. Both systems are assumed to
    run for heat_pump_lifetime_years (no gas boiler replacement is modelled).'''
    years = heat_pump_lifetime
    pv_factor = present_value_factor(discount_rate, years)

    # Fuel needed to deliver the same heat
    gas_used_kwh_per_year = heat_demand_yearly / gas_boiler_efficiency
    electricity_used_kwh_per_year = heat_demand_yearly / scop

    # Annual running costs (fuel + maintenance)
    gas_boiler_running_cost_gbp_per_year = (
        gas_used_kwh_per_year * gas_rate_pence / 100 + gas_boiler_mc)
    heat_pump_running_cost_gbp_per_year = (
        electricity_used_kwh_per_year * electricity_rate_pence / 100
        + heat_pump_mc)

    # Lifetime costs in present value
    gas_boiler_lifetime_cost_gbp = gas_boiler_install_gbp + (gas_boiler_running_cost_gbp_per_year * pv_factor)
    heat_pump_lifetime_cost_before_grant_gbp = heat_pump_install_gbp + (heat_pump_running_cost_gbp_per_year * pv_factor)
    heat_pump_lifetime_cost_after_grant_gbp = heat_pump_lifetime_cost_before_grant_gbp - grant_gbp

    # Household net cost: positive = household is worse off with the heat pump
    household_net_cost_gbp = heat_pump_lifetime_cost_after_grant_gbp - gas_boiler_lifetime_cost_gbp

    # Emissions over the lifetime (tonnes CO2e)
    gas_boiler_lifetime_emissions_tonnes = gas_used_kwh_per_year * gas_emissions * years / 1000
    heat_pump_lifetime_emissions_tonnes = electricity_used_kwh_per_year * electricity_emissions * years / 1000
    emissions_abated_tonnes = gas_boiler_lifetime_emissions_tonnes - heat_pump_lifetime_emissions_tonnes

    return {
        "gas_boiler_running_cost_gbp_per_year": gas_boiler_running_cost_gbp_per_year,
        "heat_pump_running_cost_gbp_per_year": heat_pump_running_cost_gbp_per_year,
        "gas_boiler_lifetime_cost_gbp": gas_boiler_lifetime_cost_gbp,
        "heat_pump_lifetime_cost_before_grant_gbp": heat_pump_lifetime_cost_before_grant_gbp,
        "heat_pump_lifetime_cost_after_grant_gbp": heat_pump_lifetime_cost_after_grant_gbp,
        "household_net_cost_gbp": household_net_cost_gbp,
        "emissions_abated_tonnes": emissions_abated_tonnes,
        "household_net_cost_per_tonne_gbp": household_net_cost_gbp / emissions_abated_tonnes,
        "pv_factor": pv_factor,
    }

baseline = household_costs()
print("BASELINE")
baseline_table = pd.DataFrame(
    [(name, value) for name, value in baseline.items()],
    columns=["Metric", "Value"])
baseline_table["Value"] = baseline_table["Value"].map(lambda value: f"{value:,.2f}")
baseline_output = baseline_table.to_string(index=False)
print(baseline_output)
with open(chart_dir /"baseline_output.txt", "w", encoding="utf-8") as output_file:
    output_file.write(baseline_output + "\n")

# Break-even price ratio: heat pump running cost per kWh of heat is lower than gas when (electricity price / gas price) < SCOP / boiler efficiency
current_price_ratio = electricity_rate / gas_rate
break_even_price_ratio = heat_pump_efficiency / gas_boiler_efficiency
print(f"\nCurrent electricity/gas price ratio: {current_price_ratio:.2f}")
print(f"Break-even price ratio (SCOP / boiler efficiency): {break_even_price_ratio:.2f}")

# SCENARIOS (each overrides only what it changes)
scenarios = {
    "Baseline": {},
    "Lower SCOP (3.0)": {"scop": 3.0},
    "Higher SCOP (4.0)": {"scop": 4.0},
    "Heat pump cost 10,000": {"heat_pump_install_gbp": 10000},
    "Heat pump cost 15,000": {"heat_pump_install_gbp": 15000},
    "Jan-Mar 2026 prices": {"electricity_rate_pence": 27.69, "gas_rate_pence": 5.93},
    "Electricity VAT back to 5%": {"electricity_rate_pence": electricity_rate * 1.05},
}
scenario_results = pd.DataFrame(
    {name: household_costs(**overrides) for name, overrides in scenarios.items()}).T
print("\nSCENARIOS")
print(scenario_results[["household_net_cost_gbp", "emissions_abated_tonnes",
                        "household_net_cost_per_tonne_gbp"]].round(1).to_string())

# Chart 1: Baseline household outcome summary
baseline_metrics = [
    ("Household net cost", f"£{baseline['household_net_cost_gbp']:,.2f}", "#A4135C"),
    ("Emissions abated", f"{baseline['emissions_abated_tonnes']:,.2f}", "#4C9AA8"),
    ("Cost per tonne abated", f"£{baseline['household_net_cost_per_tonne_gbp']:,.2f}", "#17365D"),
]
fig, axes = plt.subplots(1, 3, figsize=(10, 3.2))
for ax, (title, value, color) in zip(axes, baseline_metrics):
    ax.set_axis_off()
    ax.text(0.5, 0.68, title, ha="center", va="center", fontsize=13)
    ax.text(0.5, 0.43, value, ha="center", va="center", fontsize=22,
            color=color, fontweight="bold")
    unit = "tonnes CO2e" if title == "Emissions abated" else (
        "per tonne CO2e" if title == "Cost per tonne abated" else "present value")
    ax.text(0.5, 0.22, unit, ha="center", va="center", fontsize=10)
fig.suptitle("Baseline household outcomes", fontsize=16)
fig.tight_layout(rect=(0, 0, 1, 0.88))
plt.savefig(chart_dir / "Chart 1 - Baseline metrics.png", dpi=200, bbox_inches="tight")

# Chart 2: Household net cost by scenario (appendix / backup)
sorted_results = scenario_results.sort_values("household_net_cost_gbp")
fig, ax = plt.subplots(figsize=(6.5, 3.6))
net_costs = sorted_results["household_net_cost_gbp"]
chart_2_colors = [
    "#F01D75" if scenario == "Baseline" else "#FFA1CD"
    for scenario in sorted_results.index
]
bars = ax.barh(sorted_results.index, net_costs, color=chart_2_colors)
ax.bar_label(bars, labels=[f"£{value:,.0f}" for value in net_costs], padding=4)
ax.axvline(0, color="black", linewidth=1)
ax.set_title("Household net cost by scenario")
ax.set_xlabel("Household net cost vs gas boiler, after grant (GBP, present value)")
ax.margins(x=0.16)
plt.tight_layout(); plt.savefig(chart_dir / "Chart 2 - Household net cost by scenario.png", dpi=200)

# Chart 3: Stacked lifetime cost (installation + running)
pv_factor = baseline["pv_factor"]
categories = ["Gas boiler", "Heat pump\n(no grant)", "Heat pump\n(with grant)"]
installation_costs = [gas_boiler_ic,
                      heat_pump_ic,
                      heat_pump_ic - heat_pump_grant]
running_costs_pv = [baseline["gas_boiler_running_cost_gbp_per_year"] * pv_factor,
                    baseline["heat_pump_running_cost_gbp_per_year"] * pv_factor,
                    baseline["heat_pump_running_cost_gbp_per_year"] * pv_factor]
fig, ax = plt.subplots(figsize=(6, 4))
installation_bars = ax.bar(categories, installation_costs, color="#F2F233", label="Installation")
running_bars = ax.bar(categories, running_costs_pv, bottom=installation_costs, color="#51B01C", label="Running cost (PV)")
ax.bar_label(installation_bars,
             labels=[f"£{value:,.0f}" for value in installation_costs],
             label_type="center")
ax.bar_label(running_bars,
             labels=[f"£{value:,.0f}" for value in running_costs_pv],
             label_type="center",
             color="white")
ax.set_title("Lifetime cost by heating system", y=1.12, loc="left")
ax.set_ylabel("GBP")
ax.legend(loc="lower left", bbox_to_anchor=(0, 1.02), ncol=2, frameon=False)
plt.tight_layout()
plt.savefig(chart_dir / "Chart 3 - Stacked lifetime cost.png", dpi=200, bbox_inches="tight")

# Chart 4: Price ratio over time. ADD the earlier Ofgem quarters (2022 Q2 to 2025 Q4) later to this!
ofgem_unit_rates = pd.DataFrame({
    "quarter": ["2026 Q1", "2026 Q2", "2026 Q3", "2026 Q4"],
    "electricity_pence_per_kwh": [27.69, 24.67, 26.11, 26.32],
    "gas_pence_per_kwh": [5.93, 5.74, 7.33, 7.97]})
ofgem_unit_rates["price_ratio"] = (ofgem_unit_rates["electricity_pence_per_kwh"]
                                   / ofgem_unit_rates["gas_pence_per_kwh"])
fig, ax = plt.subplots(figsize=(7, 4))
ax.plot(ofgem_unit_rates["quarter"], ofgem_unit_rates["price_ratio"], marker="o", color="#095E50")
ax.axhline(break_even_price_ratio, color="black", linestyle="--", linewidth=1)
ax.text(0, break_even_price_ratio + 0.05, f"Break-even ratio {break_even_price_ratio:.2f}", fontsize=8)
ax.set_title("Electricity-to-gas unit-rate ratio over time")
ax.set_ylabel("Electricity / gas unit-rate ratio")
plt.tight_layout(); plt.savefig(chart_dir / "Chart 4 - Price ratio over time.png", dpi=200)

# Chart 5: Net cost per tonne and emissions abated by scenario
cost_per_tonne = sorted_results["household_net_cost_per_tonne_gbp"]
tonnes_abated = sorted_results["emissions_abated_tonnes"]
fig, ax = plt.subplots(figsize=(10, 4.8))
chart_5_colors = [
    "#17365D" if scenario == "Baseline" else "#6B90DB"
    for scenario in sorted_results.index
]
bars = ax.barh(sorted_results.index, cost_per_tonne, color=chart_5_colors)
labels = [
    f"£{cost:,.0f}/tonne"
    for cost, tonne in zip(cost_per_tonne, tonnes_abated)
]
ax.bar_label(bars, labels=labels, padding=5)
ax.axvline(0, color="black", linewidth=1)
ax.set_title("Net cost per tonne and emissions abated by scenario")
ax.set_xlabel("Household net cost per tonne abated (GBP, present value)")
ax.margins(x=0.3)
plt.tight_layout()
plt.savefig(chart_dir / "Chart 5 - Cost per tonne and emissions abated.png", dpi=200)