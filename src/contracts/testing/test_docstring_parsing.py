import unittest

from ..docstring_parsing import DocStringInfo, Arg, number_of_spaces
from contracts.interface import add_prefix


examples = {"""
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

    """: DocStringInfo(docstring='\n        Provides a RGB representation of the values by interpolating the range\n'
                         '        [min(value),max(value)] into the colorspace [min_color, max_color].\n',
  params={
        'value': Arg('The field to represent.', 'HxW array'),
        'max_value': Arg('If specified, everything *above* is clipped.', 'float'),
        'min_value': Arg('If specified, everything *below* is clipped.', 'float'),
        'min_color': Arg('Color to give to the minimum values.', None),
  },
  returns=[Arg('A RGB image.', "HxWx3 uint8"), Arg('gray', None)]
)
}


class DocStringTest(unittest.TestCase):

    def test_parsing(self):
        for string in examples:
            parsed = DocStringInfo.parse(string)
            "%s" % parsed
            "%r" % parsed
            result = examples[string]
            self.assertEqual(result, parsed)

    def test_number_of_spaces(self):
        self.assertEqual(number_of_spaces(''), 0)
        self.assertEqual(number_of_spaces(' '), 1)
        self.assertEqual(number_of_spaces('  '), 2)
        self.assertEqual(number_of_spaces('11'), 0)
        self.assertEqual(number_of_spaces(' 223'), 1)
        self.assertEqual(number_of_spaces('  4343'), 2)

    def test_reparsing(self):
        for string, result in examples.items(): #@UnusedVariable
            parsed = DocStringInfo.parse(string)
            converted = "%s" % parsed
            reparsed = DocStringInfo.parse(converted)

            msg = ('First string:\n%s\nParsed as:\n%s\n' %
                (add_prefix(string, '|'), add_prefix('%r' % parsed, '|')))

            msg += ('Converted:\n%s\nReparsed as:\n%s\n' %
                (add_prefix(converted, '|'), add_prefix('%r' % reparsed, '|')))

            self.assertEqual(parsed, reparsed, msg=msg)

    def test_inline_params(self):
        def test_inline_parsing(docstring, expected_type="type",
                                expected_desc="desc"):
            info = DocStringInfo.parse(docstring)
            self.assertTrue("name" in info.params)
            self.assertEqual(info.params["name"].type, expected_type)
            self.assertEqual(info.params["name"].desc, expected_desc)

        # Proper syntax
        test_inline_parsing(":param type name: desc")
        test_inline_parsing(":param name: desc", None)
        test_inline_parsing(":param name:", None, None)

        # Weird syntax for people who like to break things.
        test_inline_parsing(" : param type name : desc ")
        test_inline_parsing(" : param  name : desc ", None)
        test_inline_parsing(" : param  name : ", None, None)
        test_inline_parsing(" : param type , > 0  name : ", "type , > 0", None)

    def test_inline_returns(self):
        def test_inline_parsing(docstring, expected_type="type",
                                expected_desc="desc"):
            info = DocStringInfo.parse(docstring)
            self.assertTrue(len(info.returns) > 0)
            self.assertEqual(info.returns[0].type, expected_type)
            self.assertEqual(info.returns[0].desc, expected_desc)

        # Proper syntax
        test_inline_parsing(":returns type: desc")
        test_inline_parsing(":returns: desc", None)
        test_inline_parsing(":returns:", None, None)

        # Weird syntax for people who like to break things.
        test_inline_parsing(" : returns type : desc ")
        test_inline_parsing(" : returns : desc ", None)
        test_inline_parsing(" : returns : ", None, None)
        test_inline_parsing(" : returns type , > 0 : ", "type , > 0", None)
