# Concepts in plain language

## The decision
A factory that builds advanced packages (for example stacked memory modules or multi-chiplet packages) has to decide how much in-line inspection to run. Too little, and defective units reach customers. Too much, and inspection costs money and slows the line.

## Cost of quality
Quality managers add up three kinds of cost:

| Kind | Meaning | In this project |
|---|---|---|
| Appraisal | The cost of checking | `inspection` (direct cost) and `slowdown` (lost throughput) |
| Internal failure | Defects caught before shipping | `scrap` (value already invested in the unit) |
| External failure | Defects that reach the customer | `escaped` (returns, field failures) |

The **cost of quality** is the sum of the three. The goal is to find the plan with the smallest sum.

## An inspection plan
A plan states what share of units to inspect after each assembly step: none, 10%, 25%, 50% or all. With three steps and five levels there are 125 possible plans.

## Why simulate
Defects appear by chance and inspections sometimes miss them. A Monte Carlo simulation produces many virtual units, lets chance play out, and averages the cost. Every plan is tested on the same virtual units so that differences between plans are real.

## The self-check
For this simple process an exact formula also exists. The simulation must agree with it, and the tests enforce that. That is how we know the simulation is wired correctly.

## What-if analysis
Inputs are estimates. The what-if notebook changes one assumption at a time and shows which ones matter most and when the best plan flips.

## Limits (read these)
- All inputs are made up. Results demonstrate a method, not any real process.
- Units are independent; real lines have batches, rework and tool queues.
- Detection is a single rate; real inspection varies by defect type.
- Nothing here is validated against a real factory.
