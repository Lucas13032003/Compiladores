import builtins
from dataclasses import dataclass
from operator import add, ge, gt, le, lt, mul, neg, not_, sub, truediv
from typing import TYPE_CHECKING, Any, Union
from types import FunctionType, BuiltinFunctionType

from .ctx import Ctx

# Bloco de importação especial para evitar dependência circular
if TYPE_CHECKING:
    from .ast import Block, Stmt, Value

__all__ = [
    "add",
    "eq",
    "ge",
    "gt",
    "le",
    "lt",
    "mul",
    "ne",
    "neg",
    "not_",
    "print",
    "show",
    "sub",
    "truthy",
    "truediv",
]


class LoxInstance:
    """
    Classe base para todos os objetos Lox.
    """


@dataclass
class LoxFunction:
    """Representa uma função Lox que pode ser chamada."""
    name: str
    params: list[str]
    body: "Block"  # Usamos "Block" como string para evitar erro de importação
    closure: Ctx

    def __call__(self, *args: "Value") -> "Value":
        # Permite que LoxFunction seja chamada como uma função Python normal
        return self.call(list(args))

    def call(self, args: list["Value"]) -> "Value":
        # 1. Verifica o número de argumentos
        if len(args) != len(self.params):
            raise TypeError(
                f"Expected {len(self.params)} arguments but got {len(args)}."
            )

        # 2. Cria o escopo de execução da função (usando o closure como pai)
        ctx = Ctx(scope={}, parent=self.closure)

        # 3. Associa os argumentos aos parâmetros no novo escopo
        for param_name, arg_value in zip(self.params, args):
            # AQUI ESTÁ A ALTERAÇÃO: Trocamos 'define' por 'var_def',
            # que é o nome do método que já existe na tua classe Ctx.
            ctx.var_def(param_name, arg_value)

        # 4. Executa o corpo e lida com o 'return'
        try:
            self.body.eval(ctx)
        except LoxReturn as ret:
            return ret.value

        # 5. Retorno implícito de 'nil'
        return None


class LoxReturn(Exception):
    """
    Exceção para retornar de uma função Lox.
    """
    def __init__(self, value):
        self.value = value
        super().__init__()


class LoxError(Exception):
    """
    Exceção para erros de execução Lox.
    """


# Funções de runtime que já tinhas (todas mantidas)
nan = float("nan")
inf = float("inf")

def print(value: "Value"):
    """Imprime um valor lox."""
    builtins.print(show(value))

def show(value: Any) -> str:
    """Converte valor lox para string."""
    if value is None:
        return "nil"
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, float):
        # Remove .0 from integers
        return str(value).removesuffix(".0")
    if isinstance(value, LoxFunction):
        return f"<fn {value.name}>"
    if isinstance(value, (FunctionType, BuiltinFunctionType)):
        return "<native fn>"
    if isinstance(value, LoxInstance):
        return f"{value.__class__.__name__} instance"
    if isinstance(value, type):
        return value.__name__
    return str(value)

def show_repr(value: "Value") -> str:
    """Mostra um valor lox, mas coloca aspas em strings."""
    if isinstance(value, str):
        return f'"{value}"'
    return show(value)

def truthy(value: Any) -> bool:
    """Converts Lox value to boolean according to Lox semantics."""
    if value is None or value is False:
        return False
    return True

def check_number(value: Any, op: str) -> None:
    """Checks if value is a number, raises LoxError if not."""
    if not isinstance(value, (int, float)):
        raise LoxError(f"Operands must be numbers for {op}.")

def add(left: Any, right: Any) -> Any:
    """Implements Lox's addition (numbers and strings)."""
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return left + right
    if isinstance(left, str) and isinstance(right, str):
        return left + right
    raise LoxError("Operands must be numbers or strings for +.")

def sub(left: Any, right: Any) -> float:
    """Implements Lox's subtraction."""
    check_number(left, "-")
    check_number(right, "-")
    return left - right

def mul(left: Any, right: Any) -> float:
    """Implements Lox's multiplication."""
    check_number(left, "*")
    check_number(right, "*")
    return left * right

def truediv(left: Any, right: Any) -> float:
    """Implements Lox's division."""
    check_number(left, "/")
    check_number(right, "/")
    if right == 0:
        raise LoxError("Division by zero.")
    return left / right

def gt(left: Any, right: Any) -> bool:
    """Implements Lox's greater than."""
    check_number(left, ">")
    check_number(right, ">")
    return left > right

def lt(left: Any, right: Any) -> bool:
    """Implements Lox's less than."""
    check_number(left, "<")
    check_number(right, "<")
    return left < right

def ge(left: Any, right: Any) -> bool:
    """Implements Lox's greater than or equal."""
    check_number(left, ">=")
    check_number(right, ">=")
    return left >= right

def le(left: Any, right: Any) -> bool:
    """Implements Lox's less than or equal."""
    check_number(left, "<=")
    check_number(right, "<=")
    return left <= right

def eq(left: Any, right: Any) -> bool:
    """Implements Lox's strict equality."""
    if type(left) != type(right):
        return False
    return left == right

def ne(left: Any, right: Any) -> bool:
    """Implements Lox's strict inequality."""
    return not eq(left, right)

def not_(value: Any) -> bool:
    """Implements Lox's logical not."""
    return not truthy(value)