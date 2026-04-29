import awkward as ak
import vector


class Selections:
    def __init__(self, lumi):
        self.variables = [
            'lep_pt', 'lep_eta', 'lep_phi', 'lep_e',
            'lep_charge', 'lep_type',
            'trigE', 'trigM', 'lep_isTrigMatched',
            'lep_isLooseID', 'lep_isMediumID',
            'lep_isLooseIso', 'lep_type',
        ]

        self.weight_variables = [
            "filteff", "kfac", "xsec", "mcWeight",
            "ScaleFactor_PILEUP", "ScaleFactor_ELE",
            "ScaleFactor_MUON", "ScaleFactor_LepTRIGGER",
        ]

        self.lumi = lumi

    def cut_lep_type(self, lep_type):
        lepton_type_sum = lep_type[:, 0] + lep_type[:, 1] + lep_type[:, 2] + lep_type[:, 3]
        invalid_flavor_combination = (
            (lepton_type_sum != 44) & (lepton_type_sum != 48) & (lepton_type_sum != 52)
        )
        return invalid_flavor_combination

    def cut_lep_charge(self, lep_charge):
        nonzero_total_charge = (
            lep_charge[:, 0] + lep_charge[:, 1] + lep_charge[:, 2] + lep_charge[:, 3] != 0
        )
        return nonzero_total_charge

    def cut_trig_match(self, lep_trigmatch):
        has_trigger_match = ak.sum(lep_trigmatch, axis=1) >= 1
        return has_trigger_match

    def cut_trig(self, trigE, trigM):
        return trigE | trigM

    def ID_iso_cut(self, IDel, IDmu, isoel, isomu, lepton_types):
        return (
            ak.sum(
                ((lepton_types == 13) & IDmu & isomu) | ((lepton_types == 11) & IDel & isoel),
                axis=1,
            ) == 4
        )

    def calc_mass(self, lep_pt, lep_eta, lep_phi, lep_e):
        p4 = vector.zip({"pt": lep_pt, "eta": lep_eta, "phi": lep_phi, "E": lep_e})
        invariant_mass = (p4[:, 0] + p4[:, 1] + p4[:, 2] + p4[:, 3]).M
        return invariant_mass

    def calc_weight(self, weight_variables, events):
        total_weight = self.lumi * 1000 / events["sum_of_weights"]
        for variable in weight_variables:
            total_weight = total_weight * abs(events[variable])
        return total_weight

    def apply_cuts(self, sample_name, file_name, data):
        sample_data = []

        data = data[self.cut_trig(data.trigE, data.trigM)]
        data = data[self.cut_trig_match(data.lep_isTrigMatched)]

        data['leading_lep_pt']       = data['lep_pt'][:, 0]
        data['sub_leading_lep_pt']   = data['lep_pt'][:, 1]
        data['third_leading_lep_pt'] = data['lep_pt'][:, 2]
        data['last_lep_pt']          = data['lep_pt'][:, 3]

        data = data[data['leading_lep_pt']       > 20]
        data = data[data['sub_leading_lep_pt']   > 15]
        data = data[data['third_leading_lep_pt'] > 10]

        data = data[self.ID_iso_cut(
            data.lep_isLooseID,
            data.lep_isMediumID,
            data.lep_isLooseIso,
            data.lep_isLooseIso,
            data.lep_type,
        )]

        data = data[~self.cut_lep_type(data['lep_type'])]
        data = data[~self.cut_lep_charge(data['lep_charge'])]

        data['mass'] = self.calc_mass(
            data['lep_pt'], data['lep_eta'], data['lep_phi'], data['lep_e']
        )

        if 'data' not in sample_name:
            data['totalWeight'] = self.calc_weight(self.weight_variables, data)

        sample_data.append(data)

        if 'data' not in file_name:
            n_events_after_cuts = sum(data['totalWeight'])
        else:
            n_events_after_cuts = len(data)

        return sample_data, n_events_after_cuts
