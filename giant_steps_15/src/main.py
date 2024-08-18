import math
from typing import List, Tuple
from itertools import combinations
from concurrent.futures import ProcessPoolExecutor


def find_coin_quantity_for_each_type(coins_config: List[int], value: int):
    """ Finds the quantity of coins, given a configuration, needed to represent the value """

    coins_less_than_value = [coin for coin in coins_config if value >= coin]
    quantity_of_coins_less_than_value = len(coins_less_than_value)
    sub_coins_config = []
    for quantity in range(quantity_of_coins_less_than_value):
        sub_coins_config.append(coins_less_than_value[quantity:])

    coin_quantity = None
    for sub_config in sub_coins_config:
        sub_coin_quantity = {key: 0 for key in sub_config}
        k = value
        coin_index = 0
        while k > 0:
            if k >= sub_config[coin_index]:
                k -= sub_config[coin_index]
                sub_coin_quantity[sub_config[coin_index]] += 1
            else:
                coin_index += 1

        if coin_quantity is None or sum([coin_quantity[key] for key in coin_quantity]) > sum([sub_coin_quantity[key] for key in sub_coin_quantity]):
            coin_quantity = sub_coin_quantity.copy()

    return coin_quantity


def mean_of_coins_quantity(coins_config: List[int]) -> float:
    """ Calculates the mean quantity of coins used. Always consider 100 as a case! """

    quantity_of_coins = {}
    if len(coins_config) == 0:
        return 100

    for k in range(1, 100 + 1):
        coin_quantity = find_coin_quantity_for_each_type(coins_config, k)
        quantity_of_coins[k] = (sum([coin_quantity[key] for key in coin_quantity]))

    return sum([quantity_of_coins[key] for key in quantity_of_coins]) / 99


def construct_new_coins_config(coins_config: List[int], included_coins: Tuple[int]):
    """ Constructs the new configuration the coins added to the base case """

    new_coins_config = []
    included_index = len(included_coins) - 1

    if len(coins_config) == 0:
        while included_index > -1:
            new_coins_config.append(included_coins[included_index])
            included_index -= 1
    else:
        for coin in coins_config:
            while included_index > -1:
                if included_coins[included_index] > coin and \
                        included_coins[included_index] not in coins_config:
                    new_coins_config.append(included_coins[included_index])
                    included_index -= 1
                else:
                    break
            new_coins_config.append(coin)

    if 1 not in new_coins_config:
        new_coins_config.append(1)
    return new_coins_config


def parallel_min(*args):
    """ Finds the minimum mean for a chunk of combinations """

    inclusions, coins_config, number_of_steps = args
    min_mean = 100
    min_config = []

    inclusion_index = 0
    for inclusion in inclusions:
        new_coins_config = construct_new_coins_config(coins_config, inclusion)
        min_mean_candidate = mean_of_coins_quantity(new_coins_config)
        if min_mean_candidate < min_mean:
            min_config = [new_coins_config.copy()]
            min_mean = min_mean_candidate
        elif min_mean_candidate < min_mean:
            min_config.append(new_coins_config.copy())
        if inclusion_index == number_of_steps:
            break
        inclusion_index += 1

    return {"min_mean": min_mean, "min_config": min_config}


def find_best_inclusion(number_of_threads: int, coins_config: List[int], how_many_inclusions: int):
    """ Finds the best inclusion considering all posibilities. Does this in parallel """
    """ To save RAM generators were created and jumped to the point of calculation to avoid conflict """
    """ Then finds the minimum for each parallel minimum """

    adjusted_how_many_inclusions = how_many_inclusions if 1 in coins_config else how_many_inclusions - 1
    quantity_of_combinations = math.comb(100-1, adjusted_how_many_inclusions)

    generators = [combinations([i for i in range(2, 100 + 1)], adjusted_how_many_inclusions) for _ in range(number_of_threads)]
    steps_ahead = [quantity_of_combinations // number_of_threads for _ in range(number_of_threads)]
    steps_ahead[-1] += quantity_of_combinations % number_of_threads
    for thread_index in range(number_of_threads):
        for steps in range(thread_index * steps_ahead[thread_index - 1]):
            generators[thread_index].__next__()

    results = []
    with ProcessPoolExecutor(number_of_threads) as executor:
        futures = [executor.submit(parallel_min, generators[thread_index], coins_config, steps_ahead[thread_index]) for thread_index in range(number_of_threads)]
        for future in futures:
            results.append(future.result())

    min_mean = None
    min_config = None
    for result_index, row in enumerate(results):
        if result_index == 0:
            min_mean = row["min_mean"]
            min_config = row["min_config"]
        else:
            if row["min_mean"] < min_mean:
                min_mean = row["min_mean"]
                min_config = row["min_config"]

    return min_mean, min_config


if __name__ == "__main__":
    number_of_threads = 6

    # x_coins_config = [10, 7, 1]
    # find_coin_quantity_for_each_type(x_coins_config, 14)

    # a) [100, 50, 43, 25, 10, 5, 1]
    a_coins_config = [100, 50, 25, 10, 5, 1]
    a_how_many_coins = 1
    a_min_mean, a_min_candidate = find_best_inclusion(number_of_threads, a_coins_config, a_how_many_coins)
    print(f"a) The minimum is {a_min_mean} with configuration {a_min_candidate}")

    # b) [100, 50, 43, 25, 10, 5, 2, 1]
    b_coins_config = [100, 50, 25, 10, 5, 1]
    b_how_many_coins = 2
    b_min_mean, b_min_candidate = find_best_inclusion(number_of_threads, b_coins_config, b_how_many_coins)
    print(f"b) The minimum is {b_min_mean} with configuration {b_min_candidate}")

    # c) [46, 29, 8, 3, 1] e 3.44
    c_coins_config = []
    c_how_many_coins = 5
    c_min_mean, c_min_candidate = find_best_inclusion(number_of_threads, c_coins_config, c_how_many_coins)
    print(f"c) The minimum is {c_min_mean} with configuration {c_min_candidate}")




