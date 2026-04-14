"""
Event selection cuts for the H→ZZ*→4ℓ analysis.
"""

import awkward as ak
import vector


class Selections:
    """
    Encapsulates all event-level selection cuts and weight calculations
    for the four-lepton (H→ZZ*→4ℓ) analysis.

    Parameters
    ----------
    lumi : float
        Integrated luminosity in fb⁻¹, used to normalise MC event weights.
    """

    def __init__(self, lumi):
        # Kinematic and identification branches to read from the tree
        self.variables = [
            'lep_pt', 'lep_eta', 'lep_phi', 'lep_e',
            'lep_charge', 'lep_type',
            'trigE', 'trigM', 'lep_isTrigMatched',
            'lep_isLooseID', 'lep_isMediumID',
            'lep_isLooseIso', 'lep_type',
        ]

        # Monte Carlo weight branches used to normalise simulation to data luminosity
        self.weight_variables = [
            "filteff", "kfac", "xsec", "mcWeight",
            "ScaleFactor_PILEUP", "ScaleFactor_ELE",
            "ScaleFactor_MUON", "ScaleFactor_LepTRIGGER",
        ]

        self.lumi = lumi

    # ------------------------------------------------------------------
    # Selection cuts (return True for events that should be *removed*)
    # ------------------------------------------------------------------

    def cut_lep_type(self, lep_type):
        """
        Reject events whose four leptons are not a valid same-flavour
        opposite-charge (SFOC) combination.

        Valid sums of PDG IDs: 44 (4e), 48 (2e2μ), 52 (4μ).
        Returns True for events that fail this requirement.
        """
        lepton_type_sum = lep_type[:, 0] + lep_type[:, 1] + lep_type[:, 2] + lep_type[:, 3]
        invalid_flavor_combination = (
            (lepton_type_sum != 44) & (lepton_type_sum != 48) & (lepton_type_sum != 52)
        )
        return invalid_flavor_combination

    def cut_lep_charge(self, lep_charge):
        """
        Reject events where the total lepton charge is not zero.
        Returns True for events that fail this requirement.
        """
        nonzero_total_charge = (
            lep_charge[:, 0] + lep_charge[:, 1] + lep_charge[:, 2] + lep_charge[:, 3] != 0
        )
        return nonzero_total_charge

    def cut_trig_match(self, lep_trigmatch):
        """
        Require at least one lepton to be matched to a trigger object.
        Returns True for events that *pass* (used directly as a mask).
        """
        has_trigger_match = ak.sum(lep_trigmatch, axis=1) >= 1
        return has_trigger_match

    def cut_trig(self, trigE, trigM):
        """
        Require the electron or muon trigger to have fired.
        Returns True for events that *pass* (used directly as a mask).
        """
        return trigE | trigM

    def ID_iso_cut(self, IDel, IDmu, isoel, isomu, lepton_types):
        """
        Require all four leptons to satisfy identification and isolation criteria
        appropriate to their flavour (electrons: loose ID + loose iso;
        muons: medium ID + loose iso).

        Returns True for events that *pass* (used directly as a mask).
        """
        return (
            ak.sum(
                ((lepton_types == 13) & IDmu & isomu) | ((lepton_types == 11) & IDel & isoel),
                axis=1,
            ) == 4
        )

    # ------------------------------------------------------------------
    # Derived quantities
    # ------------------------------------------------------------------

    def calc_mass(self, lep_pt, lep_eta, lep_phi, lep_e):
        """
        Compute the invariant mass of the four-lepton system in MeV.

        Uses four-momentum addition via the `vector` library.
        """
        p4 = vector.zip({"pt": lep_pt, "eta": lep_eta, "phi": lep_phi, "E": lep_e})
        invariant_mass = (p4[:, 0] + p4[:, 1] + p4[:, 2] + p4[:, 3]).M
        return invariant_mass

    # ------------------------------------------------------------------
    # MC weights
    # ------------------------------------------------------------------

    def calc_weight(self, weight_variables, events):
        """
        Compute the per-event MC weight normalised to the data luminosity.

        The weight accounts for cross-section, filter efficiency, k-factor,
        generator weight, and all experimental scale factors.
        """
        total_weight = self.lumi * 1000 / events["sum_of_weights"]
        for variable in weight_variables:
            total_weight = total_weight * abs(events[variable])
        return total_weight

    # ------------------------------------------------------------------
    # Top-level cut application
    # ------------------------------------------------------------------

    def apply_cuts(self, sample_name, file_name, data):
        """
        Apply the full H→ZZ*→4ℓ selection to a batch of events.

        Parameters
        ----------
        sample_name : str
            Label of the physics sample (used to distinguish data from MC).
        file_name : str
            Path to the ROOT file being processed (used to detect data files).
        data : ak.Array
            Awkward array of events from a single tree iterate batch.

        Returns
        -------
        sample_data : list of ak.Array
            List containing the single filtered array for this batch.
        n_events_after_cuts : int or float
            Number of events (data) or sum of weights (MC) passing all cuts.
        """
        sample_data = []

        # Trigger requirement
        data = data[self.cut_trig(data.trigE, data.trigM)]
        data = data[self.cut_trig_match(data.lep_isTrigMatched)]

        # Record pT of each lepton ranked by pT
        data['leading_lep_pt']       = data['lep_pt'][:, 0]
        data['sub_leading_lep_pt']   = data['lep_pt'][:, 1]
        data['third_leading_lep_pt'] = data['lep_pt'][:, 2]
        data['last_lep_pt']          = data['lep_pt'][:, 3]

        # Transverse momentum thresholds (in MeV)
        data = data[data['leading_lep_pt']       > 20]
        data = data[data['sub_leading_lep_pt']   > 15]
        data = data[data['third_leading_lep_pt'] > 10]

        # Identification and isolation requirements
        data = data[self.ID_iso_cut(
            data.lep_isLooseID,
            data.lep_isMediumID,
            data.lep_isLooseIso,
            data.lep_isLooseIso,
            data.lep_type,
        )]

        # Lepton flavour and charge requirements
        data = data[~self.cut_lep_type(data['lep_type'])]
        data = data[~self.cut_lep_charge(data['lep_charge'])]

        # Compute four-lepton invariant mass
        data['mass'] = self.calc_mass(
            data['lep_pt'], data['lep_eta'], data['lep_phi'], data['lep_e']
        )

        # MC-only: compute normalisation weight
        if 'data' not in sample_name:
            data['totalWeight'] = self.calc_weight(self.weight_variables, data)

        sample_data.append(data)

        if 'data' not in file_name:
            n_events_after_cuts = sum(data['totalWeight'])
        else:
            n_events_after_cuts = len(data)

        return sample_data, n_events_after_cuts
