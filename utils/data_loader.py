import time

import atlasopenmagic as atom
import awkward as ak
import uproot

from utils.selections import Selections


def data_loader(apply_selections=True, lumi=36.6, fraction=1.0, mode='full'):
    atom.available_releases()
    atom.set_release('2025e-13tev-beta')

    skim = "exactly4lep"

    sample_definitions = {
        r'Data': {
            'dids': ['data']
        },
        r'Background $Z,t\bar{t},t\bar{t}+V,VVV$': {
            'dids': [
                410470, 410155, 410218, 410219, 412043,
                364243, 364242, 364246, 364248,
                700320, 700321, 700322, 700323, 700324, 700325,
            ],
            'color': "#6b59d3",  # purple
        },
        r'Background $ZZ^{*}$': {
            'dids': [700600],
            'color': "#ff0000",  # red
        },
        r'Signal ($m_H$ = 125 GeV)': {
            'dids': [345060, 346228, 346310, 346311, 346312,
                     346340, 346341, 346342],
            'color': "#00cdff",  # light blue
        },
    }

    samples = atom.build_dataset(sample_definitions, skim=skim, protocol='https', cache=True)

    all_data = {}

    if apply_selections:

        if mode == 'test':
            print("Running in test mode: processing only the first file of each sample.")
            for sample_name in samples:
                samples[sample_name]['list'] = samples[sample_name]['list'][:1]

        for sample_name in samples:
            print(f'Processing {sample_name} samples')

            # Accumulate processed arrays across all files for this sample
            event_batches = []

            for file_path in samples[sample_name]['list']:
                start_time = time.time()
                print(f'\t{file_path}:')

                tree = uproot.open(file_path + ":analysis")

                processed_batches = []
                selec = Selections(lumi=lumi)

                for batch in tree.iterate(
                    selec.variables + selec.weight_variables + ["sum_of_weights", "lep_n"],
                    library="ak",
                    entry_stop=tree.num_entries * fraction,
                ):
                    n_events_in = len(batch)
                    batch_data, n_events_after_cuts = selec.apply_cuts(sample_name, file_path, batch)
                    processed_batches.extend(batch_data)

                    elapsed = time.time() - start_time
                    print(f'\t\t nIn: {n_events_in},\t nOut: \t{n_events_after_cuts}\t in {round(elapsed, 1)}s')

                if processed_batches:
                    event_batches.append(ak.concatenate(processed_batches))

            all_data[sample_name] = ak.concatenate(event_batches)

    return all_data, samples
