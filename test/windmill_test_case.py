import unittest


__author__ = 'neoinsanity'


class WindmillTestCase(unittest.TestCase):
    def assertFiles(self, archive_file, output_file):
        arch = open(archive_file, 'r').read()
        output = open(output_file, 'r').read()
        self.assertMultiLineEqual(arch, output)
