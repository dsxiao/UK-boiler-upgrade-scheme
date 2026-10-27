# UK Boiler Upgrade Scheme (BUS): Consumer Costs

Code, data and documentation for the consumer cost section of the group project on the Boiler Upgrade Scheme (BUS) in England and Wales.

---

## What this repository answers

> At today's prices, does a household gain or lose from switching to a heat pump?

## Data sources

| Variable in `consumer_costs.py` | Description | Value | Source |
|---|---|---|---|
| `heat_pump_ic` | ASHP installation cost (median, 2022 to 2025 data) | £12,850 | *Evaluation of the Boiler Upgrade Scheme: 2026 report* |
| `heat_pump_grant` | Grant | £7,500 | *Evaluation of the Boiler Upgrade Scheme: 2026 report* |
| `gas_boiler_ic` | Average cost of a gas boiler (including VAT) | £3,500 | *Boiler Upgrade Scheme 2026 to 2030: Summary Business Case*, page 7, footnote 8 |
| `heat_pump_mc` | ASHP average yearly maintenance cost | £200 | Checkatrade, *Heat Pump Servicing and Repair Cost in 2026* |
| `gas_boiler_mc` | Gas boiler average yearly maintenance cost | £100 | *Boiler service costs in the UK (2026 price guide)* |
| `electricity_rate` | Electricity unit rate | 26.32 p/kWh | Ofgem, *Changes to energy price cap between 1 October and 31 December 2026* |
| `gas_rate` | Gas unit rate | 7.97 p/kWh | Ofgem, same page |
| `heat_demand_yearly` | Heat demand for typical domestic consumption | 8,550 kWh/yr | Ofgem Typical Domestic Consumption Value (medium, gas) of 9,500 kWh, from *Summary of changes to energy price cap 1 July to 30 September 2026*; 9,500 × 0.9 boiler efficiency = 8,550 |
| `heat_pump_efficiency` | Seasonal coefficient of performance (SCOP) | 3.73 | *Evaluation of the Boiler Upgrade Scheme: 2026 report*, page 74 |
| `gas_boiler_efficiency` | Gas boiler efficiency | 0.90 | British Gas, *How efficient is my gas boiler?* (every new boiler sold in the UK is at least 90% efficient) |
| `gas_emissions` | Natural gas, kg CO₂e/kWh (gross CV) | 0.18231 | *Greenhouse gas reporting: conversion factors 2026*, GOV.UK |
| `electricity_emissions` | Electricity, kg CO₂e/kWh | 0.13096 | *Greenhouse gas reporting: conversion factors 2026*, GOV.UK |
| `heat_pump_lifetime` | Heat pump lifetime | 18 years | *Evaluation of the Boiler Upgrade Scheme: 2026 report*, page 54, footnote 88 |
| `discount_rate` | Discount rate | 3.5% | HM Treasury, *The Green Book*: social time preference rate of 3.50% in real terms for years 1 to 30 |

## Calculations

**Annual running cost**

```
yearly running cost = amount used (kWh/yr) × unit rate (p/kWh) / 100 + average yearly maintenance cost
```

where amount used is heat demand / boiler efficiency for gas, and heat demand / SCOP for the heat pump.

**Lifetime cost**

```
lifetime cost = installation cost + yearly running cost × PV factor
PV factor = (1 − (1 + r)^−n) / r        (13.19 at 3.5% over 18 years)
```

**Break-even price ratio**

The highest electricity price, relative to gas, at which a heat pump costs exactly the same to run as a gas boiler.

```
break-even ratio = heat pump efficiency (SCOP) / boiler efficiency = 3.73 / 0.9 = 4.14
```

Electricity can cost up to 4.14 times as much as gas before the heat pump loses its running-cost advantage. When the electricity/gas price ratio is below 4.14, running a heat pump is cheaper than running a boiler.

**Electricity-to-gas price ratio**

```
ratio = electricity unit rate / gas unit rate = 26.32 / 7.97 = 3.30
```