import pandas as pd
import matplotlib.pyplot as plt

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
    gas_boiler_lifetime_cost_gbp = gas_boiler_install_gbp + gas_boiler_running_cost_gbp_per_year * pv_factor
    heat_pump_lifetime_cost_before_grant_gbp = heat_pump_install_gbp + heat_pump_running_cost_gbp_per_year * pv_factor
    heat_pump_lifetime_cost_after_grant_gbp = heat_pump_lifetime_cost_before_grant_gbp - grant_gbp

    # Household net cost: positive = household is worse off with the heat pump
    household_net_cost_gbp = heat_pump_lifetime_cost_after_grant_gbp - gas_boiler_lifetime_cost_gbp

    # Emissions over the lifetime (tonnes CO2e)
    gas_boiler_lifetime_emissions_tonnes = gas_used_kwh_per_year * gas_emissions * years / 1000
    heat_pump_lifetime_emissions_tonnes = (
        electricity_used_kwh_per_year * electricity_emissions * years / 1000)
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
for name, value in baseline.items():
    print(f"  {name:45s} {value:12,.2f}")