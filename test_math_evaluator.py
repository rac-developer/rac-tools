import unittest
from math_evaluator import evaluate_expression

class TestMathEvaluator(unittest.TestCase):
    def test_basic_arithmetic(self):
        self.assertEqual(evaluate_expression("2 + 2"), "4")
        self.assertEqual(evaluate_expression("10 - 3 * 2"), "4")
        self.assertEqual(evaluate_expression("(5 + 5) * 3"), "30")
        self.assertEqual(evaluate_expression("10 / 4"), "2.5")

    def test_exponents_and_modulo(self):
        self.assertEqual(evaluate_expression("2 ** 3"), "8")
        self.assertEqual(evaluate_expression("2 ^ 3"), "8")
        self.assertEqual(evaluate_expression("10 % 3"), "1")

    def test_functions_and_constants(self):
        self.assertEqual(evaluate_expression("sqrt(16)"), "4")
        self.assertEqual(evaluate_expression("abs(-42)"), "42")
        self.assertEqual(evaluate_expression("round(pi, 2)"), "3.14")

    def test_percentages(self):
        self.assertEqual(evaluate_expression("100 + 20%"), "120")
        self.assertEqual(evaluate_expression("100 - 20%"), "80")
        self.assertEqual(evaluate_expression("500 + 15%"), "575")
        self.assertEqual(evaluate_expression("200 - 15%"), "170")
        self.assertEqual(evaluate_expression("20% of 500"), "100")
        self.assertEqual(evaluate_expression("20% de 500"), "100")
        self.assertEqual(evaluate_expression("15% de 80"), "12")
        self.assertEqual(evaluate_expression("50 * 20%"), "10")
        self.assertEqual(evaluate_expression("20% * 500"), "100")
        self.assertEqual(evaluate_expression("50 / 10%"), "500")
        self.assertEqual(evaluate_expression("25%"), "0.25")
        self.assertEqual(evaluate_expression("100 + 10% + 10%"), "121")
        self.assertEqual(evaluate_expression("¿cuánto es el 15% de 80?"), "12")

    def test_invalid_or_unsafe(self):
        self.assertIsNone(evaluate_expression("2 +"))
        self.assertIsNone(evaluate_expression("__import__('os').system('dir')"))
        self.assertIsNone(evaluate_expression("invalid_var"))
        self.assertIsNone(evaluate_expression("1 / 0"))
        self.assertIsNone(evaluate_expression("Hello World"))

if __name__ == "__main__":
    unittest.main()
