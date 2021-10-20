import pk_aug.augmentation as pkaug

EXPECTED_DICTS = [
    {"unit": "ng·h·ml", "num": "ng·h·ml", "denom": ""},
    {"unit": "h-1", "num": "", "denom": "h"},
    {"unit": "/h", "num": "", "denom": "h"},
    {"unit": "h(-1)", "num": "", "denom": "h"},
    {"unit": "μM·h", "num": "μM·h", "denom": ""},
    {"unit": "ng·h/ml", "num": "ng·h", "denom": "ml"},
    {"unit": "l/[h·kg]", "num": "l", "denom": "h·kg"},
    {"unit": "ng/ml·h", "num": "ng", "denom": "ml·h"},
    {"unit": "mM/(l·h)", "num": "mM", "denom": "l·h"},
    {"unit": "l/h/kg", "num": "l", "denom": "h·kg"},
    {"unit": "ml·h-1·kg-1", "num": "ml", "denom": "h·kg"},
    {"unit": "mg·l-1·h-1", "num": "mg", "denom": "l·h"},
    {"unit": "l/h/70·kg", "num": "l", "denom": "h·70·kg"},
    {"unit": "μl/min/mg·protein", "num": "μl", "denom": "min·mg·protein"},
    {"unit": "l·h(-1)·70·kg(-1)", "num": "l", "denom": "h·70·kg"},
    {"unit": "(ml·h−1)·kg−1", "num": "ml", "denom": "h·kg"}

    # {"unit": "ml·h-1·kg-1", "num": "ml", "denom": "h·kg"},

]
