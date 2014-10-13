try:
    import numpy
except ImportError:
    pass
else:

    import unittest

    from contracts import decorate, new_contract, ContractNotRespected

    new_contract('rgb', 'array[HxWx3],H>0,W>0')
    new_contract('rgba', 'array[HxWx4],H>0,W>0')

    def blend_function(image1, image2, bug=False):
        """
            Blends two RGB or RGBA images together.

             :param image1: The first image to blend.
             :type image1: (rgb|rgba),array[HxWx*]
             :param image2: The second image to blend.
             :type image2: (rgb|rgba),array[HxWx*]
             :param bug: Introduce a bug to check the contracts.
             :type bug: bool

             :return: The blended image.
             :rtype: rgb,array[HxWx3]
        """
        H, W = image1.shape[0], image1.shape[1]

        if bug:
            # if we want to show a bug, return a different shape
            W += 1

        result = numpy.zeros((H, W, 3), 'uint8')

        # put here the actual function
        image2

        return result

    im_float = numpy.zeros((10, 10, 3), dtype='float32')
    rgb_small = numpy.zeros((10, 10, 3), dtype='uint8')
    rgb_large = numpy.zeros((20, 20, 3), dtype='uint8')

    rgba_small = numpy.zeros((10, 10, 3), dtype='uint8')
    rgba_large = numpy.zeros((20, 20, 3), dtype='uint8')

    class ArrayTest(unittest.TestCase):

        def setUp(self):
            self.blend = decorate(blend_function)

        def test_correct_behavior(self):
            self.blend(rgb_small, rgb_small)
            self.blend(rgb_small, rgba_small)
            self.blend(rgba_small, rgb_small)
            self.blend(rgb_large, rgba_large)
            self.blend(rgba_large, rgb_large)

        def test_incorrect1(self):
            self.assertRaises(ContractNotRespected, self.blend, None, None)

        def test_incorrect2(self):
            self.assertRaises(ContractNotRespected, self.blend,
                              None, rgb_small)

        def test_incorrect3(self):
            self.assertRaises(ContractNotRespected, self.blend,
                              rgb_small, None)

        def test_incorrect4(self):
            self.assertRaises(ContractNotRespected, self.blend,
                              rgb_small, rgb_large)

        def test_incorrect5(self):
            self.assertRaises(ContractNotRespected, self.blend,
                              rgb_small, rgb_large)

        def test_incorrect6(self):
            # check that rtype checking works, introduce a bug
            self.assertRaises(ContractNotRespected, self.blend, rgb_small,
                              rgb_small, bug=True)

