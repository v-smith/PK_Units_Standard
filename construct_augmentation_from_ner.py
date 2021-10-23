import json
from typing import List

import pandas as pd
import typer
from pathlib import Path
from pk_aug.utils import read_jsonl
import pk_aug.augmentation as pkaug
from collections import Counter


def main(
        input_file: Path = typer.Option(default="data/train-all-reviewed.jsonl"),
        output_dict: Path = typer.Option(default="data/dictionaries/data_augment_clean.json"),
        output_freqs: Path = typer.Option(default="data/dictionaries/u_mention_freqs.csv"),

):
    """

    :param input_file:
    :param output_dict:
    :param output_freqs:
    :return:
    """

    annotations = list(read_jsonl(input_file))

    units_standard_syns = dict()
    pk_standard_syns = dict()
    original = []
    standardised = []
    magnitudes = []
    all_mag_bool = []
    original_freq = dict()

    for an in annotations:
        for r in an['relations']:
            for sp_ch in ['head_span', 'child_span']:
                ent_instance = r[sp_ch]
                if ent_instance['label'] == 'UNITS':
                    # TRY TO STANDARDISE UNIT
                    ch_start = ent_instance['start']
                    ch_end = ent_instance['end']
                    original_mention = an['text'][ch_start:ch_end]

                    units_mention = pkaug.standardise_unit(original_mention)
                    num, denom = pkaug.standardise_divide(units_mention)
                    std_unit_mention, std_unit_magnitudes, all_as_mag = pkaug.convert_final_std(inp_num=num,
                                                                                                inp_denom=denom)

                    if original_mention not in original:
                        original.append(original_mention)
                        standardised.append(std_unit_mention)
                        magnitudes.append(std_unit_magnitudes)
                        all_mag_bool.append(all_as_mag)
                        original_freq[original_mention] = 1
                    else:
                        original_freq[original_mention] += 1

                    if std_unit_mention in units_standard_syns.keys():
                        if original_mention not in units_standard_syns[std_unit_mention]:
                            units_standard_syns[std_unit_mention] += [original_mention]
                    else:
                        units_standard_syns[std_unit_mention] = [original_mention]
                    # FIND PK PARAMETER MENTION
                    if sp_ch == 'head_span':
                        if r['child_span']['label'] == "VALUE":
                            for subr in an['relations']:
                                if subr['label'] == "C_VAL" and subr['child_span'] == r['child_span'] and \
                                        subr['head_span']['label'] == "PK":
                                    pk_start = subr['head_span']['start']
                                    pk_end = subr['head_span']['end']
                                    pk_mention = an['text'][pk_start:pk_end]
                                    if std_unit_mention in pk_standard_syns.keys():
                                        if pk_mention not in pk_standard_syns[std_unit_mention]:
                                            pk_standard_syns[std_unit_mention] += [pk_mention]
                                    else:
                                        pk_standard_syns[std_unit_mention] = [pk_mention]

    assert original == list(original_freq.keys())

    final_DF = pd.DataFrame(dict(Mention_frequency=list(original_freq.values()),
                            Mention=original, Standardised=standardised, Magnitudes=magnitudes,
                                 All_as_Mag=all_mag_bool
                                 )).sort_values('Mention_frequency', ascending=False)

    final_DF.to_csv("AllSTD.csv")

    replacable_units: List[List[str]] = [v for v in units_standard_syns.values()]
    replacable_parameters: List[List[str]] = [v for v in pk_standard_syns.values()]
    final_dictionary = dict(UNITS=replacable_units, PK=replacable_parameters)
    with open(output_dict, 'w') as outfile:
        json.dump(final_dictionary, outfile, indent=4)


if __name__ == "__main__":
    typer.run(main)
