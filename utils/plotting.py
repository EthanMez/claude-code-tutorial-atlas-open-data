import awkward as ak
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import AutoMinorLocator


def plot_histogram(all_data, samples, save_dir, mass_range, bin_width, lumi, fraction):
    xmin, xmax = mass_range
    bin_edges = np.arange(xmin, xmax + bin_width, bin_width)
    bin_centres = (bin_edges[:-1] + bin_edges[1:]) / 2

    data_counts, _ = np.histogram(ak.to_numpy(all_data['Data']['mass']), bins=bin_edges)
    data_stat_errors = np.sqrt(data_counts)

    signal_masses  = ak.to_numpy(all_data[r'Signal ($m_H$ = 125 GeV)']['mass'])
    signal_weights = ak.to_numpy(all_data[r'Signal ($m_H$ = 125 GeV)'].totalWeight)
    signal_color   = samples[r'Signal ($m_H$ = 125 GeV)']['color']

    mc_masses  = []
    mc_weights = []
    mc_colors  = []
    mc_labels  = []

    for sample_name in samples:
        if sample_name not in ['Data', r'Signal ($m_H$ = 125 GeV)']:
            mc_masses.append(ak.to_numpy(all_data[sample_name]['mass']))
            mc_weights.append(ak.to_numpy(all_data[sample_name].totalWeight))
            mc_colors.append(samples[sample_name]['color'])
            mc_labels.append(sample_name)

    fig, main_axes = plt.subplots(figsize=(12, 8))

    main_axes.errorbar(
        x=bin_centres, y=data_counts, yerr=data_stat_errors,
        fmt='ko', 
        label='Data',
    )

    mc_histogram = main_axes.hist(
        mc_masses, bins=bin_edges,
        weights=mc_weights, stacked=True,
        color=mc_colors, label=mc_labels,
    )
    mc_stacked_counts = mc_histogram[0][-1]

    mc_stat_uncertainty = np.sqrt(
        np.histogram(
            np.hstack(mc_masses), bins=bin_edges,
            weights=np.hstack(mc_weights) ** 2,
        )[0]
    )

    main_axes.hist(
        signal_masses, bins=bin_edges,
        bottom=mc_stacked_counts,
        weights=signal_weights, color=signal_color,
        label=r'Signal ($m_H$ = 125 GeV)',
    )

    main_axes.bar(
        bin_centres,
        2 * mc_stat_uncertainty,
        alpha=0.5,
        bottom=mc_stacked_counts - mc_stat_uncertainty,
        color='none', hatch="////", width=bin_width,
        label='Stat. Unc.',
    )

    main_axes.set_xlim(left=xmin, right=xmax)
    main_axes.set_ylim(bottom=0, top=np.amax(data_counts) * 2.0)

    main_axes.xaxis.set_minor_locator(AutoMinorLocator())
    main_axes.yaxis.set_minor_locator(AutoMinorLocator())

    main_axes.tick_params(which='both', direction='in', top=True, right=True)

    main_axes.set_xlabel(
        r'4-lepton invariant mass $\mathrm{m_{4\ell}}$ [GeV]',
        fontsize=13, x=1, horizontalalignment='right',
    )
    main_axes.set_ylabel(
        f'Events / {bin_width} GeV',
        y=1, horizontalalignment='right',
    )

    effective_lumi_label = str(lumi * fraction)

    plt.text(0.1, 0.93, 'ATLAS Open Data',
             transform=main_axes.transAxes, fontsize=16)
    plt.text(0.1, 0.88, 'for education',
             transform=main_axes.transAxes, style='italic', fontsize=12)
    plt.text(0.1, 0.82,
             r'$\sqrt{s}$=13 TeV,$\int$L dt = ' + effective_lumi_label + r' fb$^{-1}$',
             transform=main_axes.transAxes, fontsize=16)
    plt.text(0.1, 0.76, r'$H \rightarrow ZZ^* \rightarrow 4\ell$',
             transform=main_axes.transAxes, fontsize=16)

    legend = main_axes.legend(frameon=False, fontsize=16)

    plt.tight_layout()
    plt.savefig(f"{save_dir}/histogram.pdf")
