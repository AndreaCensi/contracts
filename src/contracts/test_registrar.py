good_examples = []
syntax_fail_examples = []
semantic_fail_examples = []
contract_fail_examples = []


# If exact is True, we are providing a canonical form
# for the expression and we want it back.
def good(a, b, exact=True):
    good_examples.append((a, b, exact))


def semantic_fail(a, b, exact=True):
    semantic_fail_examples.append((a, b, exact))


def syntax_fail(s):
    syntax_fail_examples.append(s)


def fail(a, b, exact=True):
    contract_fail_examples.append((a, b, exact))


