import re
from typing import List, Dict, Tuple

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
        splt_on_divide = inp_mention.split("/", 1)
        replaced_second_divide = [x.replace("/", "·") for x in splt_on_divide]
        replaced_second_divide = ["(" + item + ")(-1)" for item in replaced_second_divide[1:]]
        replaced_second_divide.insert(0, splt_on_divide[0])
        new_inp_mention = "·".join(replaced_second_divide)
        new_inp_mention = new_inp_mention.strip("·")
    else:
        new_inp_mention = inp_mention

    return new_inp_mention


def check_weight_dot_split(inp_mention: str) -> List:
    if len(re.findall("70·kg\(-1\)|70·kg-1|70·\(kg\)-1", inp_mention))>=1:
        weight_split = re.split("70·kg\(-1\)|70·kg-1|70·\(kg\)-1", inp_mention)
        weight_split = [minus for minus in weight_split if (minus != "" and minus is not None)]
        weight_split = "".join(weight_split)
        dot_split = re.split(r"·", weight_split)
        dot_split.extend(["70·kg(-1)"])
        dot_split = [dot for dot in dot_split if (dot != "" and dot is not None)]
    else:
        dot_split = re.split(r"·", inp_mention)
        dot_split = [dot for dot in dot_split if (dot != "" and dot is not None)]

    return dot_split


def check_weight_bracket_dot_split(inp_mention: str) -> List:
    if len(re.findall("70·kg\(-1\)|70·kg-1|70·\(kg\)-1", inp_mention))>=1:
        weight_split = re.split("70·kg\(-1\)|70·kg-1|70·\(kg\)-1", inp_mention)
        weight_split = [minus for minus in weight_split if (minus != "" and minus is not None)]
        weight_split = "".join(weight_split)
        dot_split = re.split(r"·(?=[^\)]*(?:\(|$))", weight_split)
        dot_split.extend(["70·kg(-1)"])
        dot_split = [dot for dot in dot_split if (dot != "" and dot is not None)]
    else:
        dot_split = re.split(r"·(?=[^\)]*(?:\(|$))", inp_mention)
        dot_split = [dot for dot in dot_split if (dot != "" and dot is not None)]
    return dot_split


def check_for_brackets(inp_mention: str) -> List:
    if len(re.findall(r"\((.*?)\)\(-\d+\)|\((.*?)\)\(−\d+\)", inp_mention)) >= 1:
        # split on dots outside of brackets only
        dot_split = check_weight_bracket_dot_split(inp_mention)
        brackets_split = [re.split(r"\((.*?)\)", dot) and re.split(r"(-\d)|(−\d)", dot) for dot in dot_split]
        brackets_split = [[bracket for bracket in i if bracket is not None] for i in brackets_split]
        brackets_split = [[num_bracket.strip("(){}[]") for num_bracket in i] for i in brackets_split]
        brackets_split = [[bracket for bracket in i if bracket != ""] for i in brackets_split]
        final_split = [[strip_bracket.replace("−", "-") for strip_bracket in i] for i in brackets_split]
    elif len(re.findall(r"\(-(\d)\)|\(−(\d)\)|-(\d)|−(\d)", inp_mention)) >= 1:
        dot_split = check_weight_dot_split(inp_mention)
        minus_one_split = [re.split(r"\((-\d)\)|\((−\d)\)|(-\d)|(−\d)", dot2) for dot2 in dot_split]
        minus_one_split = [[minus for minus in i if (minus != "" and minus is not None)] for i in minus_one_split]
        minus_one_split = [[num_minus.strip("(){}[]") for num_minus in i] for i in minus_one_split]
        final_split = [[strip_minus.replace("−", "-") for strip_minus in i] for i in minus_one_split]
    else:
        final_split = [[inp_mention]]

    return final_split


def standardise_divide(inp_mention: str) -> Tuple:
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

    # add all those without -digits to nominator list
    num_list = [sublist for sublist in units_split if len(sublist) == 1]
    minus_list = [sub for sub in units_split if sub not in num_list]

    # sort out if any minus digits that are not 1s
    denom_list = []
    for sublist in minus_list:
        if sublist[1] != "-1":
            power = sublist[1].replace("-", "^")
            subject = "(" + sublist[0] + ")"
            new_sublist = "".join([subject, power])
            denom_list.append([new_sublist])
        else:
            new_subject = sublist[0]
            denom_list.append([new_subject])

    # get final denominator and nominator lists
    num_list = [item for sublist in num_list for item in sublist]
    denom_list = [item for sublist in denom_list for item in sublist]

    # join elements with mutliplication sign
    numerator = "·".join(num_list)
    denominator = "·".join(denom_list)
    print(numerator, "/", denominator)

    return numerator, denominator


test_ones = ["l·h(-1)·70·kg(-1)", "l/h/70·kg", "h-1", "/h", "ng·h·ml", "10−6·cm/s/h", "ng·ml(-1)·h(-1)", "μmol·l−1", "l·(kg·h)(-1)"]
for x in test_ones:
    t2 = standardise_unit(x)
    final = standardise_divide(t2)
