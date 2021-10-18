import pk_aug.augmentation as pkaug

EXPECTED_DICTS = [{"unit": "l·(kg·h)(-1)", "num": "l", "denom": "kg·h"},
                  {"unit": "ng·ml(-1)·h(-1)", "num": "ng·h", "denom": "ml"},
                  {"unit": "μmol·l−1", "num": "μmol", "denom": "l"},
                  {"unit": "10−6·cm/s/h", "num": "cm·h", "denom": "(10)^6·s"}]


def test_standardise_divide():
    for dic in EXPECTED_DICTS:
        inp_mention = dic["unit"]
        unit = pkaug.standardise_unit(inp_mention)
        num, denom = pkaug.standardise_divide(unit)
        assert num == dic["num"]
        assert denom == dic["denom"]


def test_two():
    assert 1 == 1
