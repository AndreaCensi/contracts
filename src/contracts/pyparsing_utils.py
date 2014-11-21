from .syntax import (Forward, Suppress, FollowedBy, Group, OneOrMore, Optional,
                     opAssoc)
 
 
def myOperatorPrecedence(baseExpr, opList):
    """Helper method for constructing grammars of expressions made up of
       operators working in a precedence hierarchy.  Operators may be unary or
       binary, left- or right-associative.  Parse actions can also be attached
       to operator expressions.
 
       Parameters:
        - baseExpr - expression representing the most basic element for the
        - opList - list of tuples, one for each operator precedence level in 
          expression grammar; each tuple is of the form
          (opExpr, numTerms, rightLeftAssoc, parseAction), where:
           - opExpr is the pyparsing expression for the operator;
              may also be a string, which will be converted to a Literal;
              if numTerms is 3, opExpr is a tuple of two expressions, for the
              two operators separating the 3 terms
           - numTerms is the number of terms for this operator (must
              be 1, 2, or 3)
           - rightLeftAssoc is the indicator whether the operator is
              right or left associative, using the pyparsing-defined
              constants opAssoc.RIGHT and opAssoc.LEFT.
           - parseAction is the parse action to be associated with
              expressions matching this operator expression (the
              parse action tuple member may be omitted)
    """
    ret = Forward()
    allops = [x[0] for x in opList]
    opnames = ",".join(str(x) for x in allops)
    ret.setName('operatorSystem(%s)' % opnames)
    # parenthesis = Suppress('(') + ret + FollowedBy(NotAny(oneOf(allops)))
    # - Suppress(')')
    parenthesis = Suppress('(') - ret - Suppress(')')
    lastExpr = parenthesis.setName('parenthesis(%s)' % opnames) | baseExpr
    #lastExpr.setName('Base operand (%s) or parenthesis' % str(baseExpr))
    for operDef in opList:
        opExpr, arity, rightLeftAssoc, pa = (operDef + (None,))[:4]
        if arity == 3:
            if opExpr is None or len(opExpr) != 2:
                raise ValueError(
                    "if numterms=3, opExpr must be a tuple or list of two "
                    "expressions")
            opExpr1, opExpr2 = opExpr
        thisExpr = Forward().setName("operation_with(%s)" % opExpr)
        if rightLeftAssoc == opAssoc.LEFT:
            if arity == 1:
                matchExpr = FollowedBy(lastExpr + opExpr) + Group(
                    lastExpr + OneOrMore(opExpr))
            elif arity == 2:
                if opExpr is not None:
                    #                    matchExpr = Group(lastExpr +
                    # FollowedBy(opExpr) + OneOrMore(opExpr - lastExpr))

                    matchExpr = Group(
                        lastExpr + FollowedBy(opExpr) - OneOrMore(
                            opExpr - lastExpr))
                else:
                    matchExpr = FollowedBy(lastExpr + lastExpr) + Group(
                        lastExpr + OneOrMore(lastExpr))
            elif arity == 3:
                matchExpr = FollowedBy(
                    lastExpr + opExpr1 + lastExpr + opExpr2 + lastExpr) + \
                            Group(
                                lastExpr + opExpr1 + lastExpr + opExpr2 +
                                lastExpr)
            else:
                raise ValueError(
                    "operator must be unary (1), binary (2), or ternary (3)")
        elif rightLeftAssoc == opAssoc.RIGHT:
            if arity == 1:
                # try to avoid LR with this extra test
                if not isinstance(opExpr, Optional):
                    opExpr = Optional(opExpr)
                matchExpr = FollowedBy(opExpr.expr - thisExpr) - Group(
                    opExpr - thisExpr)
            elif arity == 2:
                if opExpr is not None:
                    matchExpr = FollowedBy(
                        lastExpr + opExpr - thisExpr) + Group(
                        lastExpr + OneOrMore(opExpr - thisExpr))
                else:
                    matchExpr = FollowedBy(lastExpr + thisExpr) + Group(
                        lastExpr + OneOrMore(thisExpr))
            elif arity == 3:
                matchExpr = FollowedBy(
                    lastExpr + opExpr1 + thisExpr + opExpr2 + thisExpr) + \
                            Group(
                                lastExpr + opExpr1 + thisExpr + opExpr2 +
                                thisExpr)
            else:
                raise ValueError(
                    "operator must be unary (1), binary (2), or ternary (3)")
        else:
            raise ValueError(
                "operator must indicate right or left associativity")
        if pa:
            matchExpr.setParseAction(pa)
        thisExpr << (matchExpr | lastExpr).setName(
            'operation with %s' % opExpr)
        lastExpr = thisExpr
    ret << lastExpr
    return ret
