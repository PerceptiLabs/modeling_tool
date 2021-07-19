import sys
import argparse
import logging
from prettytable import PrettyTable

from trainer_benchmarks.mnist import MnistSuite
from trainer_benchmarks.wildfires import WildfiresSuite
from trainer_benchmarks.humanactivity import HumanActivitySuite
from trainer_benchmarks.covid19 import CovidXraySuite

logger = logging.getLogger('perceptilabs.applogger')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


BENCHMARK_SUITES = {
    'mnist': MnistSuite,
    'wildfires': WildfiresSuite,
    'humanactivity': HumanActivitySuite,
    'covid19': CovidXraySuite
}


def print_results(results, suite_name):
    table = PrettyTable(['Metric', 'Keras baseline', 'Recommendation', 'Custom'])
    table.title = f"{suite_name.upper()} Suite Results"
    for metric, (baseline_value, rec_value, custom_value) in results.items():
        table.add_row([metric, baseline_value, rec_value, custom_value])
    print(table)
    

def get_input_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--modeltype', default='custom', type=str, choices=['custom', 'recommended', 'baseline', 'all'],
                        help='Type of model in the benchmarkSuite that needs to be used.')
    parser.add_argument('-d', '--suites', default='all', type=str, nargs='*', choices=list(BENCHMARK_SUITES.keys())+['all'],
                        help='Benchmarking suites that need to be tested.')
    
    args = parser.parse_args()
    return args


def main():
    args = get_input_args()
    suites = list(args.suites if 'all' not in args.suites else BENCHMARK_SUITES)
    model_type = args.modeltype
    for suite_name in suites:
        print(f"Running suite '{suite_name}' with type '{model_type}'")
        suite = BENCHMARK_SUITES[suite_name]()
        results = suite.get_results(which=model_type)
        print_results(results, suite_name)
    
if __name__ == "__main__":
    main()
