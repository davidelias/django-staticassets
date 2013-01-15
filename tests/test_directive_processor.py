from staticassets.processors.directive import DirectiveProcessor

from .test import TestCase


class DirectiveProcessorTest(TestCase):
    fixtures_dir = 'directives'

    def setUp(self):
        self.processor = DirectiveProcessor()

    def test_parse_double_slash(self):
        directives, content = self.processor.parse(self.fixture('double_slash'))

        self.assertEqual([['require', 'a'], ['require', 'b']], directives)
        self.assertEqual('// header\n//\n\nvar A = {};\n', content)

    def test_parse_hash(self):
        directives, content = self.processor.parse(self.fixture('hash'))

        self.assertEqual([['require', 'a'], ['require', 'b']], directives)
        self.assertEqual('# header\n#\n\nA = {}\n', content)

    def test_parse_triple_hash(self):
        directives, content = self.processor.parse(self.fixture('triple_hash'))

        self.assertEqual([['require', 'a'], ['require', 'b']], directives)
        self.assertEqual('###\nheader\n\n###\n\nA = {}\n', content)

    def test_parse_slash_star(self):
        directives, content = self.processor.parse(self.fixture('slash_star'))

        self.assertEqual([['require', 'a'], ['require', 'b']], directives)
        self.assertEqual('/* header\n *\n */\n\nvar A = {};\n', content)

    def test_parse_slash_star_single(self):
        directives, content = self.processor.parse(self.fixture('slash_star_single'))

        self.assertEqual([['require', 'a']], directives)
        self.assertEqual('\n\nvar A = {};\n', content)

    def test_parse_without_directives(self):
        directives, content = self.processor.parse(self.fixture('without_directives'))

        self.assertEqual([], directives)
        self.assertEqual('/*\n * header\n */\n\nvar A = {};\n', content)
