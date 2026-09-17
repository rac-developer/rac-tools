import ast
import math
import operator

class SafeMathEvaluator(ast.NodeVisitor):
    """
    Safely evaluates math expressions using Python AST.
    Prevents execution of arbitrary code, function calls (except whitelisted math functions),
    or variable access.
    """

    ALLOWED_OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.BitXor: operator.pow,  # Support '^' as power operator for user convenience
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    ALLOWED_FUNCTIONS = {
        "sqrt": math.sqrt,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "abs": abs,
        "log": math.log,
        "exp": math.exp,
        "round": round,
        "floor": math.floor,
        "ceil": math.ceil,
    }

    ALLOWED_CONSTANTS = {
        "pi": math.pi,
        "e": math.e,
        "tau": math.tau,
    }

    def visit(self, node):
        method_name = f"visit_{node.__class__.__name__}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def visit_Expression(self, node):
        return self.visit(node.body)

    def visit_Num(self, node):
        return node.n

    def visit_Constant(self, node):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Constant value is not numeric")

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        op_type = type(node.op)

        if op_type in self.ALLOWED_OPERATORS:
            if op_type in (ast.Div, ast.FloorDiv, ast.Mod) and right == 0:
                raise ZeroDivisionError("Division by zero")
            return self.ALLOWED_OPERATORS[op_type](left, right)
        raise ValueError(f"Operator {node.op} not supported")

    def visit_UnaryOp(self, node):
        operand = self.visit(node.operand)
        op_type = type(node.op)
        if op_type in self.ALLOWED_OPERATORS:
            return self.ALLOWED_OPERATORS[op_type](operand)
        raise ValueError(f"Unary operator {node.op} not supported")

    def visit_Name(self, node):
        if node.id.lower() in self.ALLOWED_CONSTANTS:
            return self.ALLOWED_CONSTANTS[node.id.lower()]
        raise ValueError(f"Unknown variable: {node.id}")

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            func_name = node.func.id.lower()
            if func_name in self.ALLOWED_FUNCTIONS:
                args = [self.visit(arg) for arg in node.args]
                return self.ALLOWED_FUNCTIONS[func_name](*args)
        raise ValueError("Unsupported function call")

    def generic_visit(self, node):
        raise ValueError(f"AST Node {node.__class__.__name__} is not allowed")


import re

def normalize_percentage_expression(text: str) -> str:
    """
    Normalizes percentage operations and conversational math queries into standard arithmetic.
    Supports:
    - Additive percentage (e.g. 100 + 20% -> 120)
    - Subtractive percentage / discounts (e.g. 100 - 20% -> 80)
    - Multiplicative and divisive percentages (e.g. 50 * 20% -> 10, 50 / 10% -> 500)
    - "X% of Y" / "X% de Y" (e.g. 20% of 500 -> 100)
    - Standalone percentages (e.g. 25% -> 0.25)
    - Preserves modulo when used between numbers without trailing % (e.g. 10 % 3 -> 1)
    """
    cleaned = text.strip().lstrip("¿?").rstrip("¿?").strip()
    if not cleaned:
        return ""

    # Remove optional conversational question prefixes
    cleaned = re.sub(
        r"^(?:cuanto\s+es(?:\s+el)?|cuánto\s+es(?:\s+el)?|what\s+is(?:\s+the)?|calc|calcula(?:\s+el)?)\s+",
        "",
        cleaned,
        flags=re.IGNORECASE
    )
    cleaned = re.sub(r"\b(?:el|the)\s+(\d)", r"\1", cleaned, flags=re.IGNORECASE)

    # Replace display multiplication/division symbols
    cleaned = cleaned.replace("×", "*").replace("÷", "/")

    # 1. Handle "X% of Y" or "X% de Y" -> ((X / 100) * Y)
    cleaned = re.sub(
        r"(\d+(?:\.\d+)?)\s*%\s*(?:of|de)\s*(\(?\s*[\d\.]+\s*\)?)",
        r"((\1 / 100) * \2)",
        cleaned,
        flags=re.IGNORECASE
    )

    # 2. Handle additive and subtractive percentages: X + Y% -> ((X) * (1 + (Y) / 100))
    pattern = re.compile(r"([+-])\s*(\d+(?:\.\d+)?)\s*%(?!\s*\d)")
    while True:
        m = pattern.search(cleaned)
        if not m:
            break
        op_idx = m.start(1)
        op = m.group(1)
        pct = m.group(2)
        end_idx = m.end()

        left_str = cleaned[:op_idx].rstrip()
        if not left_str:
            break

        if left_str.endswith(")"):
            depth = 0
            start_idx = len(left_str) - 1
            for i in range(len(left_str) - 1, -1, -1):
                if left_str[i] == ")":
                    depth += 1
                elif left_str[i] == "(":
                    depth -= 1
                    if depth == 0:
                        start_idx = i
                        break
            left_operand = left_str[start_idx:]
            prefix = left_str[:start_idx]
        else:
            m_left = re.search(r"(\b\d+(?:\.\d+)?)$", left_str)
            if m_left:
                left_operand = m_left.group(1)
                prefix = left_str[:m_left.start(1)]
            else:
                break

        sign = "+" if op == "+" else "-"
        replacement = f"(({left_operand}) * (1 {sign} ({pct}) / 100))"
        cleaned = prefix + replacement + cleaned[end_idx:]

    # 3. Handle standalone or trailing % (e.g. "25%", "50 * 20%", "(10 + 5)%") where % is NOT followed by digits
    cleaned = re.sub(r"(\d+(?:\.\d+)?)\s*%(?!\s*\d)", r"(\1 / 100)", cleaned)

    return cleaned


def evaluate_expression(text: str):
    """
    Evaluates a string as a mathematical expression if valid.
    Returns string formatted as result or None if invalid.
    """
    cleaned = text.strip()
    if not cleaned:
        return None

    norm = normalize_percentage_expression(cleaned)
    if not norm:
        return None

    # Require at least one math symbol, function call, or percentage to avoid treating plain numbers as math
    has_operator = any(op in cleaned for op in ["+", "-", "*", "/", "%", "^", "**", "(", ")"])
    has_func = any(fn in cleaned.lower() for fn in SafeMathEvaluator.ALLOWED_FUNCTIONS.keys())
    has_pct_word = any(w in cleaned.lower() for w in ["%", " de ", " of "])

    if not (has_operator or has_func or has_pct_word):
        return None

    try:
        parsed = ast.parse(norm, mode="eval")
        evaluator = SafeMathEvaluator()
        result = evaluator.visit(parsed)

        # Normalize float precision issues (e.g. 121.00000000000001 -> 121)
        if isinstance(result, float):
            result = round(result, 9)

        # Format integer vs float cleanly
        if isinstance(result, float) and result.is_integer():
            result = int(result)
        elif isinstance(result, float):
            result = round(result, 6)

        return str(result)
    except Exception:
        return None
