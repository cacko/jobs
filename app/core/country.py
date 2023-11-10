import pycountry


def to_iso(text: str):
    try:
        cnt = pycountry.countries.get(alpha_2=text)
        return cnt.alpha_2
    except AttributeError:
        cnt = pycountry.countries.search_fuzzy(text)
        assert cnt
        return cnt[0].alpha_2


def to_name(code: str):
    try:
        cnt = pycountry.countries.get(alpha_2=code)
        return cnt.name
    except AttributeError:
        return code
