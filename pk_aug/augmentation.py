import re
from typing import List, Dict
import regex as reg

TO_REMOVE = []  # ['[', '(', ']', ')']
DOT_SYNS = ['x', '*', '×', '•', ' ', '⋅']
UNIT_SYNONYMS = {
    '·': DOT_SYNS,
    'μg': ['micrograms', 'micro g', 'microg', 'microgram'],
    'h': ['hr', 'hrs', 'hour', 'hours'],
    '%': ['percent', 'percentage'],
    'l': ['liters', 'litre', 'liter', 'litres'],
    'min': ['minutes', 'minute', 'mins'],
    'd': ['days', 'day'],
    'kg': ['kilogram', 'kilograms'],
    's': ['sec'],
    'nM': ['nmol', 'nanomol'],
    'mM': ['mmol', 'milimol'],
    'μM': ['mumol', 'micromol', 'micromols'],
    'pM': ['pmol', 'pmols']

}

MAGNITUDES = {
    'TIME': ['s', 'min', 'h', 'd'],
    'MASS': ['ng', 'μg', 'mg', 'g', 'kg'],
    'VOLUME': ['nl', 'µl', 'ml', 'l'],
    'CONCENTRATION': ['pM', 'nM', 'μM', 'mM', 'M']
}


def subs_underscore_dot(inp_mention: str, standard_dot: str = '·') -> str:
    """
    Substitutes '.' by '·' if '.' is not surrounded by numbers
    """
    match_dot = r"(?<!\d)\.(?!\d)|\.(?!\d)|(?<!\d)\."
    inp_mention = re.sub(match_dot, standard_dot, inp_mention)
    return inp_mention


def sub_all_mult(inp_mention: str, standard_dot: str = '·') -> str:
    for x in DOT_SYNS:
        if x in inp_mention:
            inp_mention = inp_mention.replace(x, standard_dot)
    inp_mention = re.sub(r'·+', standard_dot, inp_mention)
    return inp_mention


def check_syns(inp_term: str, replacement_dict: Dict) -> str:
    for main_form, synonyms in replacement_dict.items():
        if inp_term in synonyms:
            return main_form
        synonyms_changed = [x + "-1" for x in synonyms]
        main_form_changed = main_form + "-1"
        if inp_term in synonyms_changed:
            return main_form_changed
    return inp_term


def make_subs_dict(inp_terms: List[str], replacement_dict: Dict) -> List[str]:
    out_terms = [check_syns(inp_term=term, replacement_dict=replacement_dict) for term in inp_terms]
    assert len(inp_terms) == len(out_terms)
    return out_terms


def unit_std_dict(inp_mention: str, standard_dot: str = '·', standard_div: str = '/') -> str:
    subunits_one = inp_mention.split(standard_dot)
    std_subunits_one = []
    subunits_one = ["/" if x == "per" else x for x in subunits_one]
    for subu in subunits_one:
        if standard_div in subu:
            subunits_two = subu.split(standard_div)
            std_subunits_two = [check_syns(inp_term=t, replacement_dict=UNIT_SYNONYMS) for t in subunits_two]
            std_subunits_one.append(f"{standard_div}".join(std_subunits_two))
        else:
            std_subunits_one.append(check_syns(inp_term=subu, replacement_dict=UNIT_SYNONYMS))

    assert len(subunits_one) == len(std_subunits_one)
    return f"{standard_dot}".join(std_subunits_one)


def standardise_unit(inp_mention: str) -> str:
    inp_mention = inp_mention.strip()
    inp_mention = "".join([x.lower() if x != 'M' else x for x in inp_mention])
    inp_mention = inp_mention.replace("per cent", "%")
    inp_mention = inp_mention.replace(" per ", "/")
    inp_mention = inp_mention.replace("per ", "/")
    if '.' in inp_mention:
        inp_mention = subs_underscore_dot(inp_mention=inp_mention)
    for x in TO_REMOVE:
        inp_mention = inp_mention.replace(x, '')
    inp_mention = sub_all_mult(inp_mention=inp_mention)
    inp_mention = unit_std_dict(inp_mention=inp_mention)

    inp_mention = inp_mention.replace("micro·", "μ")
    inp_mention = inp_mention.replace("micro", "μ")
    return inp_mention


###############################################################################

def check_for_divide(inp_mention: str) -> str:
    if len(inp_mention.split("/")) > 1:
        splt_on_divide = inp_mention.split("/")
        replaced_divides = ["(" + item + ")-1" for item in splt_on_divide[1:]]
        replaced_divides.insert(0, splt_on_divide[0])
        inp_mention = "·".join(replaced_divides)
    return inp_mention


def check_for_brackets(inp_mention: str) -> str:
    if len(re.findall(r"\((.*?)\)\(-\d+\)|\((.*?)\)\(−\d+\)", inp_mention)) >= 1:
        # split on dots outside of brackets only
        dot_split = re.split("\·(?![^()*])", inp_mention)
        brackets_split = [re.split("\((.*?)\)|\((.*?)\)", xnominator) for xnominator in dot_split]
        brackets_split = [[x for x in i if (x != "" and x is not None)] for i in brackets_split]
        # brackets_split = [[x for x in i if x != None] for i in brackets_split]
        brackets_split = [[i.strip("(").strip(")") for i in x] for x in brackets_split]
        final_split = [[i.replace("−", "-") for i in x] for x in brackets_split]
    elif len(re.findall("\(-(?:\d)\)|\(−(?:\d)\)|-(?:\d)|−(?:\d)", inp_mention)) >= 1:
        # split on -digits
        dot_split = re.split("·", inp_mention)
        # minus = re.findall("\(-\d+\)|\(−\d+\)|-\d+|−\d+", item)
        minus_one_split = [re.split("\((-\d)\)|\((−\d)\)|(-\d)|(−\d)", x) for x in dot_split]
        minus_one_split = [[x for x in i if x != ""] for i in minus_one_split]
        minus_one_split = [[x for x in i if x is not None] for i in minus_one_split]
        minus_one_split = [[i.strip("(").strip(")") for i in x] for x in minus_one_split]
        final_split = [[i.replace("−", "-") for i in x] for x in minus_one_split]
    else:
        final_split = inp_mention

    return final_split


def standardise_divide(inp_mention: str) -> str:
    """
    Converts all units into dict of numerator and denominator (removes all "/" and "-1")
    N.B. second slash equivalent to multiplication
    """
    # check for / and convert all to -1
    inp_mention = check_for_divide(inp_mention)

    # check for brackets
    units_split = check_for_brackets(inp_mention)

    # convert -1s to nominators and denominators
    num_list = []
    minus_list = []
    denom_list = []

    # add all those without -digits to nominator list
    num_list = [sublist for sublist in units_split if len(sublist) == 1]
    minus_list = [x for x in units_split if x not in num_list]

    # sort out if any minus digits that are not 1s
    updated_minus_list = []
    denom_list = []
    for sublist in minus_list:
        if sublist[1] != "-1":
            power = sublist[1].replace("-", "^")
            subject = "(" + sublist[0] + ")"
            new_sublist = "".join([subject, power])
            denom_list.append([new_sublist])
        else:
            new_subject = sublist[0]
            updated_minus_list.append([new_subject])

    # get final denominator and nominator lists
    add_to_denom_list = updated_minus_list[0::2]
    add_to_nom_list = updated_minus_list[1::2]
    num_list.extend(add_to_nom_list)
    denom_list.extend(add_to_denom_list)
    num_list = [item for sublist in num_list for item in sublist]
    denom_list = [item for sublist in denom_list for item in sublist]

    # join elements with mutliplication sign
    numerator = "·".join(num_list)
    denominator = "·".join(denom_list)
    print(numerator, "/", denominator)

    return numerator, denominator


test_ones = ["10−6·cm/s/h", "ng·ml(-1)·h(-1)", "l·(kg·h)(-1)", "μmol·l−1"]
for x in test_ones:
    t2 = standardise_unit(x)
    final = standardise_divide(t2)
