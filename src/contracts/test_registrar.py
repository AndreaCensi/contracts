from typing import List, Tuple, Union

good_examples: List[Tuple[Union[str, List[str]], object, bool]] = []
syntax_fail_examples: List[str] = []
semantic_fail_examples: List[Tuple[Union[str, List[str]], object, bool]] = []
contract_fail_examples: List[Tuple[Union[str, List[str]], object, bool]] = []


# If exact is True, we are providing a canonical form
# for the expression and we want it back.
def good(a: Union[str, List[str]], b: object, exact: bool = True):
    good_examples.append((a, b, exact))


def semantic_fail(a: Union[str, List[str]], b: object, exact=True):
    semantic_fail_examples.append((a, b, exact))


def syntax_fail(s: str):
    syntax_fail_examples.append(s)


def fail(a: Union[str, List[str]], b: object, exact: bool = True):
    contract_fail_examples.append((a, b, exact))
