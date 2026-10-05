import random
import math
from scipy.stats import chi2
import matplotlib.pyplot as plt
from scipy import stats
from itertools import combinations


NUM_ROWS = 50
SEATS_LAYOUT = ['A', 'B', 'C', 'D', 'E', 'F']
TOTAL_PASSENGERS = NUM_ROWS * len(SEATS_LAYOUT)
MEAN_STOW_TIME = 0.5
MEAN_MOVE_BASE = 0.25
MEAN_MOVE_PER_BLOCKER = 0.5

class Passenger:
    # for every passenger we create this instance and add to a list
    def __init__(self, passenger_id, row, seat):
        self.id = passenger_id
        self.row = row
        self.seat = seat

class Airplane:
    #airplane to hold the current seated passengers
    def __init__(self):
        self.seats = {r: {s: None for s in SEATS_LAYOUT} for r in range(1, NUM_ROWS + 1)}

    def get_blocking_passengers_count(self, passenger):
        # count how many are in the way
        blocking_count = 0
        passenger_row = self.seats[passenger.row]
        blocking_map = {
            #A is blocked by B,C f.e
            'A': ['B', 'C'], 'B': ['C'], 'C': [],
            'F': ['E', 'D'], 'E': ['D'], 'D': []
        }
        seats_to_check = blocking_map[passenger.seat]
        for seat_letter in seats_to_check:
            if passenger_row[seat_letter] is not None:
                blocking_count += 1
        return blocking_count

    def seat_passenger(self, passenger):
        self.seats[passenger.row][passenger.seat] = passenger

def run_single_simulation_parallel(boarding_strategy):
    airplane = Airplane()
    total_time = 0.0
    num_seated = 0
    
    active_passengers = []

    passengers = []
    p_id = 1
    for r in range(1, NUM_ROWS + 1):
        for s in SEATS_LAYOUT:
            passengers.append(Passenger(p_id, r, s))
            p_id += 1
    
    if boarding_strategy == 'random':
        boarding_queue = passengers[:]
        random.shuffle(boarding_queue)
    if boarding_strategy == 'front_to_back':
        boarding_queue = sorted(passengers, key=lambda p: p.row)
    if boarding_strategy == 'back_to_front':
        boarding_queue = sorted(passengers, key=lambda p: p.row, reverse=True)
    if boarding_strategy == 'one_per_row_back_to_front':
        # 1. Group passengers by row
        rows_dict = {r: [] for r in range(1, NUM_ROWS + 1)}
        for p in passengers:
            rows_dict[p.row].append(p)
        
        seat_priority = {'A': 0, 'F': 0, 'B': 1, 'E': 1, 'C': 2, 'D': 2}
        for r in range(1, NUM_ROWS + 1):
            #order each row by the priority (a,f first and next column)
            rows_dict[r].sort(key=lambda p: seat_priority[p.seat])
            
        boarding_queue = []
        #add one from each row per layout
        for i in range(len(SEATS_LAYOUT)): # columns
            for r in range(NUM_ROWS, 0, -1): # rows backwards (50 to 1)
                boarding_queue.append(rows_dict[r][i])

    #runs until everyone is seated
    while num_seated < TOTAL_PASSENGERS:
        
        # fill with new passengers from the queue
        if boarding_queue:
            last_active_row = 0
            if active_passengers:
                # Get the row of the passenger closest to the entrance
                last_active_row = active_passengers[-1]['passenger'].row
            
            # Keep adding passengers as long as they don't need to pass someone (row is strictly smaller)
            while boarding_queue:
                next_passenger = boarding_queue[0]
                if not active_passengers or next_passenger.row < last_active_row:
                    next_passenger = boarding_queue.pop(0)
                    
                    # Calculate their personal seating time *now*
                    stow_time = random.expovariate(1.0 / MEAN_STOW_TIME)
                    blocker_count = airplane.get_blocking_passengers_count(next_passenger)
                    mean_move_time = MEAN_MOVE_BASE + (MEAN_MOVE_PER_BLOCKER * blocker_count)
                    seating_time = random.expovariate(1.0 / mean_move_time) if mean_move_time > 0 else 0
                    
                    active_passengers.append({
                        'passenger': next_passenger,
                        'time_remaining': stow_time + seating_time
                    })
                    last_active_row = next_passenger.row
                else:
                    # The next passenger is blocked by someone already in the aisle
                    break
        
        if not active_passengers:
            break

        time_step = min(p['time_remaining'] for p in active_passengers)
        
        # advance the clock according to the fastest pessanger
        total_time += time_step

        # Update all active passengers, seating who finished
        updated_active_passengers = []
        for p_info in active_passengers:
            p_info['time_remaining'] -= time_step
            
            if math.isclose(p_info['time_remaining'], 0.0): # Compare with a small number for float safety, can maybe do 0
                # This passenger is now seated
                airplane.seat_passenger(p_info['passenger'])
                num_seated += 1
            else:
                # This passenger is still not done seating
                updated_active_passengers.append(p_info)
        
        active_passengers = updated_active_passengers
        
    return total_time

def plot_results(results_dict):
    fig, ax = plt.subplots(figsize=(14, 8))

    num_runs = len(next(iter(results_dict.values())))
    runs = range(1, num_runs + 1)

    for strategy_name, times in results_dict.items():
        ax.plot(runs, times, label=strategy_name, alpha=0.8)

    ax.set_title('Boarding Time per Run for Each Strategy')
    ax.set_xlabel('Run Number')
    ax.set_ylabel('Boarding Time (minutes)')
    ax.legend(title='Boarding Strategy')
    plt.show()

def kruskal_wallis_manual(*groups):
    print("Kruskal-Wallis test")

    all_data_with_groups = []
    for group_index, group in enumerate(groups):
        for value in group:
            all_data_with_groups.append({'value': value, 'group': group_index})

    all_data_with_groups.sort(key=lambda x: x['value'])

    # ranks for each run
    for i, item in enumerate(all_data_with_groups):
        item['rank'] = i + 1

    # sum for each group
    num_groups = len(groups)
    rank_sums = [0] * num_groups
    for item in all_data_with_groups:
        rank_sums[item['group']] += item['rank']

    # calc H
    N = len(all_data_with_groups)

    summation_term = 0
    for i in range(num_groups):
        n_i = len(groups[i])
        R_i = rank_sums[i]
        summation_term += (R_i ** 2) / n_i

    H_statistic = (12 / (N * (N + 1))) * summation_term - 3 * (N + 1)

    # calc P value
    degrees_of_freedom = num_groups - 1
    p_value = chi2.sf(H_statistic, df=degrees_of_freedom)

    print("Test Hypotheses:")
    print("1. There is no difference in the boarding time distributions.")
    print("2. At least one method's distribution is different.\n")

    print(f"Manually Calculated H-statistic: {H_statistic:.4f}")
    print(f"p-value (from Chi-squared distribution): {p_value}")

    alpha = 0.05

    if p_value < alpha:
        print(f"The p-value ({p_value:.2e}) is less than the significance level ({alpha}).")
    else:
        print(f"The p-value ({p_value}) is not less than the significance level ({alpha}).")

def perform_shapiro_wilk_tests(results_dict):
    print("Shapiro-Wilk test")
    print("Test Hypotheses:")
    print("1. Null Hypothesis: The data is normally distributed.")
    print("2. Alternative Hypothesis: The data is not normally distributed.\n")

    alpha = 0.05

    for strategy_name, times in results_dict.items():
        stat, p_value = stats.shapiro(times)

        print(f"Results for '{strategy_name}':")
        print(f"W-statistic: {stat:.4f}")
        print(f"P-value: {p_value:.4f}")

        if p_value < alpha:
            print(f"Conclusion: The P-value is less than {alpha}, so we reject the null hypothesis.")
            print("The data cannot be assumed to be normally distributed.")
        else:
            print(f"Conclusion: The P-value is greater than or equal to {alpha}, so we fail to reject the null hypothesis.")
            print("There is not enough evidence to rule out normality.")

def perform_anova_test(results_dict):
    print("ANOVA Test")
    print("Test Hypotheses:")
    print("1. Null Hypothesis: The means of all methods are equal.")
    print("2. Alternative Hypothesis: The mean of at least one method is different.\n")
    
    f_statistic, p_value = stats.f_oneway(*results_dict.values())
    
    print("Test Results:")
    print(f"F-statistic: {f_statistic:.4f}")
    print(f"P-value: {p_value}")

    alpha = 0.05
    print(f"\nSignificance level (alpha) set to: {alpha}\n")

    print("Conclusion:")
    if p_value < alpha:
        print(f"The P-value ({p_value:.2e}) is less than the significance level ({alpha}).")
        print("Therefore, we reject the null hypothesis.")
        print("This result suggests there is a statistically significant difference between the means of the methods.")
    else:
        print(f"The P-value ({p_value}) is not less than the significance level ({alpha}).")
        print("Therefore, we fail to reject the null hypothesis.")

def perform_pairwise_tests(results_dict):
    print("Pairwise Comparisons")
    print("Comparing each pair of methods to see if their difference is statistically significant.")
    
    strategy_names = list(results_dict.keys())
    pairs = combinations(strategy_names, 2)
    
    alpha = 0.05

    for pair in pairs:
        name1, name2 = pair
        data1 = results_dict[name1]
        data2 = results_dict[name2]

        print(f"\nComparing {name1} vs. {name2}")

        #Welch's T-test (does not assume equal variance)
        t_stat, t_pvalue = stats.ttest_ind(data1, data2, equal_var=False)
        print("Welch's T-test:")
        print(f"T-statistic: {t_stat:.4f}, P-value: {t_pvalue:.2e}")
        if t_pvalue < alpha:
            print("Conclusion: Significant difference found (p < 0.05).")
        else:
            print("Conclusion: No significant difference found (p >= 0.05).")

        #Man-Whitney test
        u_stat, u_pvalue = stats.mannwhitneyu(data1, data2, alternative='two-sided')
        print("Mann-Whitney test:")
        print(f"U-statistic: {u_stat:.4f}, P-value: {u_pvalue:.2e}")
        if u_pvalue < alpha:
            print("Conclusion: Significant difference found (p < 0.05).")
        else:
            print("Conclusion: No significant difference found (p >= 0.05).")

if __name__ == "__main__":
    NUM_RUNS = 100
    
    print("Starting Airplane Boarding Simulation")
    print(f"Running {NUM_RUNS} simulations for each strategy.\n")

    random_times = [run_single_simulation_parallel('random') for _ in range(NUM_RUNS)]
    front_to_back_times = [run_single_simulation_parallel('front_to_back') for _ in range(NUM_RUNS)]
    back_to_front_times = [run_single_simulation_parallel('back_to_front') for _ in range(NUM_RUNS)]
    interleaved_times = [run_single_simulation_parallel('one_per_row_back_to_front') for _ in range(NUM_RUNS)]

    def print_stats(strategy_name, times):
        mean_time = sum(times) / len(times)
        std_dev = math.sqrt(sum([(t - mean_time) ** 2 for t in times]) / (len(times) - 1))

        z_score = 1.96 # For 95% confidence
        std_error = std_dev / math.sqrt(NUM_RUNS)
        margin_of_error = z_score * std_error
        lower_bound = mean_time - margin_of_error
        upper_bound = mean_time + margin_of_error
        
        print(f"Strategy: {strategy_name}")
        print(f"Average Boarding Time: {mean_time:.2f} minutes")
        print(f"Standard Deviation: {std_dev:.2f} minutes")
        print(f"95% Confidence Interval: [{lower_bound:.2f}, {upper_bound:.2f}] minutes\n")

    print_stats("Random", random_times)
    print_stats("Front-to-Back", front_to_back_times)
    print_stats("Back-to-Front", back_to_front_times)
    print_stats("One per row (back to front each with aisle ordering)", interleaved_times)

    all_results = [
        front_to_back_times,
        back_to_front_times,
        random_times,
        interleaved_times
    ]    
    results_dict = {
        "Front-to-Back": front_to_back_times,
        "Back-to-Front": back_to_front_times,
        "Random": random_times,
        "One per row": interleaved_times
    }
    perform_shapiro_wilk_tests(results_dict)
    perform_anova_test(results_dict)
    perform_pairwise_tests(results_dict)
    kruskal_wallis_manual(front_to_back_times,
        back_to_front_times,
        random_times,
        interleaved_times)
    plot_results(results_dict)