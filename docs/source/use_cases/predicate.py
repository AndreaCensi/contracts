from contracts import contract, new_contract

new_contract('positive', lambda x: x>0)

@contract(interval='positive')
def timer(interval):
    print('sleep for %s' % interval)


timer(2)
timer(-1)
