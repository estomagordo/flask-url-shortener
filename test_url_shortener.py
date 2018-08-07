import unittest

import main


class TestUrlShortener(unittest.TestCase):

    def test_shortened_length(self):
        urla = 'http://www.google.com'
        urlb = 'https://en.wikipedia.org/wiki/2018_FIFA_World_Cup/'
        
        for _ in range(5):
            short_a = main.shorten(urla)
            short_b = main.shorten(urlb)

            self.assertEqual(12, len(short_a))
            self.assertEqual(12, len(short_b))

if __name__ == '__main__':
    unittest.main()