import unittest
from hangman import *

class TestHangman(unittest.TestCase):
    def test_is_valid_guess(self):
        guessed_letters = set(['a', 'b', 'c'])

        # Valid guesses
        self.assertTrue(is_valid_guess('d', guessed_letters))
        self.assertTrue(is_valid_guess('e', guessed_letters))
        self.assertTrue(is_valid_guess('f', guessed_letters))

        # Invalid guesses
        self.assertFalse(is_valid_guess('abc', guessed_letters))
        self.assertFalse(is_valid_guess('1', guessed_letters))
        self.assertFalse(is_valid_guess('', guessed_letters))
        self.assertFalse(is_valid_guess(None, guessed_letters))
        self.assertFalse(is_valid_guess('a', guessed_letters))

        # Already guessed letters
        self.assertFalse(is_valid_guess('a', guessed_letters))
        self.assertFalse(is_valid_guess('b', guessed_letters))
        self.assertFalse(is_valid_guess('c', guessed_letters))

    def test_valid_names(self):
        self.assertEqual(is_name("John"), "John")
        self.assertEqual(is_name("Jane_Smith"), "Jane_Smith")
        self.assertEqual(is_name("M4x"), "M4x")
        self.assertEqual(is_name("test-name"), "test-name")
         
    def test_invalid_names(self):
        self.assertFalse(is_name("1")) 
        self.assertFalse(is_name("")) 
        self.assertFalse(is_name("a" * 21))
        self.assertFalse(is_name("invalid name"))
        self.assertFalse(is_name("$user"))
      
if __name__ == '__main__':
    unittest.main()
