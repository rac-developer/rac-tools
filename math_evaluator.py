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


def evaluate_expression(text: str):
    """
    Evaluates a string as a mathematical expression if valid.
    Returns string formatted as '= <result>' or None if invalid.
    """
    cleaned = text.strip()
    if not cleaned:
        return None

    # Replace display multiplication/division symbols
    cleaned = cleaned.replace("×", "*").replace("÷", "/")
    
    # Require at least one math symbol or function call to avoid treating pure plain numbers as math queries
    has_operator = any(op in cleaned for op in ["+", "-", "*", "/", "%", "^", "**", "(", ")"])
    has_func = any(fn in cleaned.lower() for fn in SafeMathEvaluator.ALLOWED_FUNCTIONS.keys())

    if not (has_operator or has_func):
        return None

    try:
        parsed = ast.parse(cleaned, mode="eval")
        evaluator = SafeMathEvaluator()
        result = evaluator.visit(parsed)

        # Format integer vs float cleanly
        if isinstance(result, float) and result.is_integer():
            result = int(result)
        elif isinstance(result, float):
            result = round(result, 6)

        return str(result)
    except Exception:
        return None
