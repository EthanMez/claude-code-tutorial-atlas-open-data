"""
Entry point for the H→ZZ*→4ℓ analysis.

Reads a YAML configuration file, loads ATLAS Open Data samples,
applies event selections, and produces the four-lepton invariant
mass histogram.

Usage
-----
    python analysis.py --config config.yaml
"""

import argparse

import yaml

from utils.data_loader import data_loader
from utils.plotting import plot_histogram

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Run the H→ZZ*→4ℓ analysis on ATLAS Open Data.'
    )
    parser.add_argument('--config', type=str, required=True,
                        help='Path to the YAML configuration file.')
    args = parser.parse_args()

    with open(args.config, 'r') as config_file:
        config = yaml.safe_load(config_file)

    all_data, samples = data_loader(
        fraction=config['data']['fraction'],
        lumi=config['data']['lumi'],
    )

    plot_histogram(
        all_data,
        samples,
        save_dir=config['plotting']['save_dir'],
        mass_range=config['plotting']['mass_range'],
        bin_width=config['plotting']['bin_width'],
        lumi=config['data']['lumi'],
        fraction=config['data']['fraction'],
    )
