import pk_aug.augmentation as pkaug

EXPECTED_DICTS_2 = [
    {"unit": "ng·h·ml", "num": "ng·h·ml", "denom": ""}, #passed
    {"unit": "h-1", "num": "", "denom": "h"}, #passed
    {"unit": "/h", "num": "", "denom": "h"}, #passed
    {"unit": "h(-1)", "num": "", "denom": "h"}, #passed
    {"unit": "μM·h", "num": "μM·h", "denom": ""}, #passed
    {"unit": "ng·h/ml", "num": "ng·h", "denom": "ml"}, #passed
    {"unit": "l/[h·kg]", "num": "l", "denom": "h·kg"}, #passed
    {"unit": "ng/ml·h", "num": "ng", "denom": "ml·h"}, #passed
    {"unit": "mM/(l·h)", "num": "mM", "denom": "l·h"}, #passed
    {"unit": "l/h/kg", "num": "l", "denom": "h·kg"}, #passed
    {"unit": "ml·h-1·kg-1", "num": "ml", "denom": "h·kg"}, #passed
    {"unit": "mg·l-1·h-1", "num": "mg", "denom": "l·h"}, #passed
    {"unit": "l/h/70·kg", "num": "l", "denom": "h·70·kg"}, #passed
    {"unit": "μl/min/mg·protein", "num": "μl", "denom": "min·mg·protein"}, #passed
    {"unit": "(ml·h−1)·kg−1", "num": "ml", "denom": "h·kg"}, #passed
    {"unit": "l·h(-1)·70·kg(-1)", "num": "l", "denom": "h·70·kg"},
    # {"unit": "ml·h-1·kg-1", "num": "ml", "denom": "h·kg"},

]

def test_standardise_divide():
    for dic in EXPECTED_DICTS_2:
        inp_mention = dic["unit"]
        unit = pkaug.standardise_unit(inp_mention)
        num, denom = pkaug.standardise_divide(unit)
        assert num == dic["num"]
        assert denom == dic["denom"]
