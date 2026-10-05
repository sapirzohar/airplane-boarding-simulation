# Airplane Boarding Simulation

A Python simulation project comparing different airplane boarding strategies and evaluating their efficiency using statistical analysis.

The simulation models the boarding process of an airplane with **50 rows and 6 seats per row**, including passenger seating delays, overhead baggage storage time, and seat-access interference between passengers.

## Boarding Strategies

Four boarding strategies are compared:

- **Front-to-Back**
- **Back-to-Front**
- **Random Boarding**
- **One-per-Row** – a custom strategy designed to reduce aisle blocking by boarding one passenger from each row in waves, starting from the back of the aircraft.

## Simulation

Each boarding strategy is simulated **100 times**.

Passenger boarding time includes:

- Overhead baggage storage time
- Additional seating time when other passengers block access to the assigned seat
- Parallel seating when passengers can proceed without blocking one another

Random boarding and seating times are generated using exponential distributions.

## Statistical Analysis

The simulation results are compared using:

- Mean boarding time
- Standard deviation
- 95% confidence intervals
- Shapiro-Wilk normality test
- One-way ANOVA
- Welch's t-test
- Mann-Whitney U test
- Kruskal-Wallis test

The project also includes visualizations comparing boarding times across simulation runs.

## Results

In the reported 100-run experiment, the custom **One-per-Row** strategy achieved the lowest average boarding time by a large margin.

Approximate average boarding times were:

| Strategy | Average Boarding Time |
| --- | ---: |
| Front-to-Back | 298.95 min |
| Back-to-Front | 215.88 min |
| Random | 181.86 min |
| One-per-Row | 15.78 min |

The statistical tests indicated significant differences between the boarding strategies.

## Technologies

- Python
- SciPy
- Matplotlib
- Random
- Math
- Itertools

## File

`airplane_boarding_simulation.py` – complete simulation, statistical analysis, and visualization code.
