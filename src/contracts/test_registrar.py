
good_examples = []
syntax_fail_examples = []
semantic_fail_examples = []
contract_fail_examples = []

def good(a, b): good_examples.append((a, b))
def syntax_fail(s): syntax_fail_examples.append(s)
def fail(a, b): contract_fail_examples.append((a, b))
def semantic_fail(a, b): semantic_fail_examples.append((a, b))

