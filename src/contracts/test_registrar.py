from typing import Union

good_examples: list[tuple[Union[str, list[str]], object, bool]] = []
syntax_fail_examples: list[str] = []
semantic_fail_examples: list[tuple[Union[str, list[str]], object, bool]] = []
contract_fail_examples: list[tuple[Union[str, list[str]], object, bool]] = []


# If exact is True, we are providing a canonical form
# for the expression and we want it back.
def good(a: Union[str, list[str]], b: object, exact: bool = True):
    good_examples.append((a, b, exact))


def semantic_fail(a: Union[str, list[str]], b: object, exact=True):
    semantic_fail_examples.append((a, b, exact))


def syntax_fail(s: str):
    syntax_fail_examples.append(s)


def fail(a: Union[str, list[str]], b: object, exact: bool = True):
    contract_fail_examples.append((a, b, exact))
