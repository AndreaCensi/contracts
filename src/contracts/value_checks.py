
aliases = {
    'rgb': 'array(HxWx3,uint8)',
    'grayscale': 'array(HxW,uint8)',
                      
    'finite': '!anynan !anyinf',
}

# tests:
tests = [
    'rgb',
    'rgba',
    'rgb|rgba',
    'float',
    'float >0',
    'float >=0',
    'float <0',
    'float <=0',
    'float <=0 >1',
    'int',
    'array',
    'array()',
    'array(3x3)',
    'finite'
] 




