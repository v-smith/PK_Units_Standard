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


def standardise_divide(inp_mention: str) -> str:
    '''
    Converts all units into dict of numerator and denominator (removes all "/" and "-1")
    '''
    # find up to first /
    # match1= reg.findall(r"^(.*?)(?=/)", inp_mention)
    if len(re.findall("/", inp_mention))>=1:
        splt= inp_mention.split("/")
        minus_list= []
        for item in splt:
            if re.findall("-\d+|−\d+", item):
                minus_list.append(item)
                print(item)

        #convert minus items to correct format
        #replace minus items in original list
        nominator= splt[0]
        denominator = '.'.join(splt[1:])

    #when more than 1 slash
    #inp_mention =
    #that ahead of dash is numerator and that after is denominator (however nb that a second dash can be considered as a multiplication)


    r2 = re.findall("-\d+|−\d+", inp_mention)
    replace_list= []
    print(r2)
    #need to separate if these are in brackets
    if len(r2)>=1:
        print("there are more than 1 minus digit")
        #for i in r2:
            #inp_mention = inp_mention.replace(i, replace_list)

    return inp_mention


test_ones = ["·10−6·cm/s/h",  "ng·ml(-1)·h(-1)", "μmol·l−1", "l·(kg·h)(-1)"]
for x in test_ones:
    t2 = standardise_unit(x)
    final = standardise_divide(t2)
