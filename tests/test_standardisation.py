import pk_aug.augmentation as pkaug

EXPECTED_DICTS_1 = [{"unit": "l·(kg·h)(-1)", "num": "l", "denom": "kg·h"},
                  {"unit": "ng·ml(-1)·h(-1)", "num": "ng", "denom": "ml·h"},
                  {"unit": "μmol·l−1", "num": "μmol", "denom": "l"},
                  {"unit": "10−6·cm/s/h", "num": "cm", "denom": "(10)^6·s·h"}]


def test_standardise_divide():
    for dic in EXPECTED_DICTS_1:
        inp_mention = dic["unit"]
        unit = pkaug.standardise_unit(inp_mention)
        num, denom = pkaug.standardise_divide(unit)
        assert num == dic["num"]
        assert denom == dic["denom"]


def test_two():
    assert 1 == 1
