import json
import typer
from pathlib import Path
from pk_aug.utils import read_jsonl
import pk_aug.augmentation as pkaug
from collections import Counter
import pandas as pd


def main(
        input_file: Path = typer.Option(default="data/train-all-reviewed.jsonl"),
        units_dict: Path = typer.Option(default="data/dictionaries/data_augment.json"),
        output_freqs: Path = typer.Option(default="data/dictionaries/u_mention_freqs.csv")
):
    annotations = list(read_jsonl(input_file))
    with open(units_dict) as cf:
        config = json.load(cf)

    param_units_dict = {}

    original = []
    standard = []
    all_unit_mentions = []
    for an in annotations:
        for r in an['relations']:
            for sp_ch in ['head_span', 'child_span']:
                ent_instance = r[sp_ch]
                if ent_instance['label'] == 'UNITS':
                    ch_start = ent_instance['start']
                    ch_end = ent_instance['end']
                    units_mention = an['text'][ch_start:ch_end]
                    original.append(units_mention)
                    units_mention = pkaug.standardise_unit(units_mention)
                    standard.append(units_mention)
                    all_unit_mentions.append(units_mention)
                    # Find the pk mention:
                    if sp_ch == 'head_span':
                        if r['child_span']['label'] == "VALUE":
                            for subr in an['relations']:
                                if subr['label'] == "C_VAL" and subr['child_span'] == r['child_span'] and \
                                        subr['head_span']['label'] == "PK":
                                    pk_start = subr['head_span']['start']
                                    pk_end = subr['head_span']['end']
                                    pk_mention = an['text'][pk_start:pk_end]
                                    pk_mention = pk_mention.lower()
                                    if units_mention in param_units_dict.keys():
                                        if pk_mention not in param_units_dict[units_mention]:
                                            tmp_list = param_units_dict[units_mention] + [pk_mention]
                                            param_units_dict[units_mention] = tmp_list
                                    else:
                                        param_units_dict[units_mention] = [pk_mention]

    counts_units = Counter(all_unit_mentions).most_common()

    already_printed = []
    for x, y in zip(original, standard):
        if x not in already_printed:
            print(x, ' --> ', y)
            already_printed.append(x)
    pd.DataFrame(counts_units, columns=['unit_mention', 'frequency']).to_csv(output_freqs)
    a = 1


if __name__ == "__main__":
    typer.run(main)