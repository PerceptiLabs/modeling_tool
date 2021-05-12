import sys
from prettytable import PrettyTable

from trainer_benchmarks.mnist import MnistSuite


BENCHMARK_SUITES = {
    'mnist': MnistSuite
}


def print_results(results):
    table = PrettyTable(['Metric', 'Keras baseline', 'Recommendation'])
    for metric, (baseline_value, rec_value) in results.items():
        table.add_row([metric, baseline_value, rec_value])
    print(table)
    

def main():
    suite_name = 'mnist'
    suite = BENCHMARK_SUITES[suite_name]()

    results = suite.get_results(which='both')
    print_results(results)

    
if __name__ == "__main__":
    main()
