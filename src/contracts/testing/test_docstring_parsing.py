import unittest

from ..docstring_parsing import DocStringInfo, Arg, parse_docstring_annotations

examples = { """ 
        Provides a RGB representation of the values by interpolating the range 
        [min(value),max(value)] into the colorspace [min_color, max_color].
        
        :param value: The field to represent.
        :type  value: HxW array
            
        :param max_value: If specified, everything *above* is clipped.
        :type max_value: float
        :param min_value: If specified, everything *below* is clipped.
        :type min_value: float
    
        :param min_color:  Color to give to the minimum values.
        
        
        :return: A RGB image.
        :rtype: HxWx3 uint8

        :return: gray

    """ :  DocStringInfo(docstring=
                         ' \n        Provides a RGB representation of the values by interpolating the range \n'
                         '        [min(value),max(value)] into the colorspace [min_color, max_color].\n',
  params={
        'value': Arg('The field to represent.', 'HxW array'),
        'max_value': Arg('If specified, everything *above* is clipped.', 'float'),
        'min_value': Arg('If specified, everything *below* is clipped.', 'float'),
        'min_color': Arg('Color to give to the minimum values.', None),
  },
  returns=[ Arg('A RGB image.', "HxWx3 uint8"), Arg('gray', None)] 
)          
}



class DocStringTest(unittest.TestCase):
    
    def test_parsing(self):
        for string in examples:
            parsed = parse_docstring_annotations(string)
            "%s" % parsed
            "%r" % parsed
            result = examples[string]
            self.assertEqual(result, parsed)
                
        
        
