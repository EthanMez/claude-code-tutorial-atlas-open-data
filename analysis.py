import argparse
import os
import yaml

from utils.data_loader import data_loader
from utils.plotting import plot_histogram
from pathlib import Path
import pickle

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Run the H→ZZ*→4ℓ analysis on ATLAS Open Data.'
    )
    parser.add_argument('--config', type=str, required=True,
                        help='Path to the YAML configuration file.')
    parser.add_argument('--mode', type=str, choices=['full', 'test'], default='full',
                        help='Data loading mode: "full" (default) or "test".')
    args = parser.parse_args()
    
    with open(args.config, 'r') as config_file:
        config = yaml.safe_load(config_file)

    if os.path.exists('data/all_data.pkl') and os.path.exists('data/samples.pkl'):
        print("Loading processed data from disk...")
        with open('data/all_data.pkl', 'rb') as f:
            all_data = pickle.load(f)
        with open('data/samples.pkl', 'rb') as f:
            samples = pickle.load(f)

    else:
        all_data, samples = data_loader(
            fraction=config['data']['fraction'],
            lumi=config['data']['lumi'],
            mode=args.mode,
        )

        data_dir = Path('data')
        data_dir.mkdir(parents=True, exist_ok=True)

        with (data_dir / 'all_data.pkl').open('wb') as f:
            pickle.dump(all_data, f)

        with (data_dir / 'samples.pkl').open('wb') as f:
            pickle.dump(samples, f)

    plot_histogram(
        all_data,
        samples,
        save_dir=config['plotting']['save_dir'],
        mass_range=config['plotting']['mass_range'],
        bin_width=config['plotting']['bin_width'],
        lumi=config['data']['lumi'],
        fraction=config['data']['fraction'],
    )
