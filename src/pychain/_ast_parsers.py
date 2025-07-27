import ast
import hashlib
import inspect
import textwrap
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from typing import Any, Final, TypeGuard, get_args, get_type_hints


from ._protocols import (
    Names,
    Operation,
    SignaturesRegistery,
    check_func,
    Signature,
    CYTHON_TYPES,
)


def create_type_node(imports: set[str], type_obj: type) -> ast.expr | None:
    if mapped_str := CYTHON_TYPES.get(type_obj):
        if "." in mapped_str:
            parts = mapped_str.split(".")
            imports.add(f"import {parts[0]}")
            return ast.Attribute(
                value=ast.Name(id=parts[0], ctx=ast.Load()),
                attr=parts[1],
                ctx=ast.Load(),
            )
        else:
            return ast.Name(id=mapped_str, ctx=ast.Load())
    return None


@dataclass(slots=True, frozen=True)
class TypedLambda[P, R]:
    func: Callable[[P], R]
    p_type: type[P]
    r_type: type[R]
    _is_typed_lambda: Final[bool] = True

    def __call__(self, arg: P) -> R:
        return self.func(arg)


def is_typed_lambda(obj: Any) -> TypeGuard[TypedLambda[Any, Any]]:
    return getattr(obj, "_is_typed_lambda", False) is True


def _get_inspectable_func(obj: Any) -> Callable[..., Any]:
    seen_ids = {id(obj)}
    while True:
        if inspect.isfunction(obj) or inspect.ismethod(obj) or inspect.isclass(obj):
            return obj
        if is_typed_lambda(obj):
            obj = obj.func
        elif check_func(obj):
            obj = obj.func
        elif callable(obj):
            obj = obj.__call__
        else:
            raise TypeError("L'objet n'est pas inspectable.")
        if id(obj) in seen_ids:
            raise TypeError("Boucle de wrappers détectée.")
        seen_ids.add(id(obj))


@dataclass(slots=True)
class TypeTracker:
    p_type: Final[type]
    r_type: type
    inferred_signatures: SignaturesRegistery = field(
        default_factory=dict[int, Signature]
    )

    def update(self, op: Operation[Any, Any]) -> None:
        target_obj = op.args[0] if op.func in (map, filter) else op.func

        match target_obj:
            case tl if is_typed_lambda(tl):
                self._handle_typed_lambda(op, tl)

            case func if callable(func) and not isinstance(func, type):
                self._handle_regular_callable(op, func)

            case t if isinstance(t, type):
                element_type = get_args(self.r_type)
                new_type = t[element_type] if element_type else t  # type: ignore
                self._update(new_type)  # type: ignore

            case _:
                self._update(type(target_obj))  # type: ignore

    def _handle_typed_lambda(
        self, op: Operation[Any, Any], tl: TypedLambda[Any, Any]
    ) -> None:
        p_type = tl.p_type
        r_type = tl.r_type

        arg_name = get_first_arg_name(tl.func)
        params = {arg_name: p_type} if arg_name else {}
        self.inferred_signatures[id(tl.func)] = Signature(
            params=params, return_type=r_type
        )

        if op.func is map:
            self._update(Iterable[r_type])
        elif op.func is filter:
            pass
        else:
            self._update(r_type)

    def _handle_regular_callable(
        self, op: Operation[Any, Any], func: Callable[..., Any]
    ) -> None:
        if check_func(func):
            return_type = func.return_type
            arg_name = get_first_arg_name(func.func)
            if arg_name:
                self.inferred_signatures[id(func.func)] = Signature(
                    params={arg_name: func.param_type}, return_type=return_type
                )
        else:
            try:
                inspectable_func = _get_inspectable_func(func)
                hints = get_type_hints(inspectable_func)
                return_type = hints.get("return", object)
            except TypeError:
                return_type = object

        if op.func is map:
            self._update(Iterable[return_type])
        elif op.func is filter:
            pass
        else:
            self._update(return_type)

    def _update(self, new_type: type) -> None:
        if self.r_type != new_type:
            self.r_type = new_type


@dataclass(slots=True, frozen=True)
class NodeReplacer(ast.NodeTransformer):
    arg_name: str
    replacement_node: ast.AST

    def visit_Name(self, node: ast.Name) -> Any:
        return self.replacement_node if node.id == self.arg_name else node


@dataclass(slots=True)
class LambdaFinder(ast.NodeVisitor):
    found_lambda: ast.Lambda | None = None

    def visit_Lambda(self, node: ast.Lambda) -> None:
        if self.found_lambda is None:
            self.found_lambda = node


@dataclass(slots=True)
class FunctionDefFinder(ast.NodeVisitor):
    found_func: ast.FunctionDef | None = None

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        if self.found_func is None:
            self.found_func = node


def get_callable_ast(func: Callable[..., Any]) -> ast.Lambda | ast.FunctionDef | None:
    if is_typed_lambda(func):
        func = func.func

    try:
        raw_source = textwrap.dedent(inspect.getsource(func)).strip()
        source_to_parse = (
            f"{Names.DUMMY.value}{raw_source}"
            if raw_source.startswith((".", "["))
            else raw_source
        )
        tree = ast.parse(source_to_parse)

        lambda_finder = LambdaFinder()
        lambda_finder.visit(tree)
        if lambda_node := lambda_finder.found_lambda:
            return lambda_node

        func_def_finder = FunctionDefFinder()
        func_def_finder.visit(tree)
        return func_def_finder.found_func

    except (TypeError, OSError, SyntaxError):
        return None


def extract_return_expression(func_ast: ast.FunctionDef) -> ast.expr | None:
    if len(func_ast.body) == 1 and isinstance(stmt := func_ast.body[0], ast.Return):
        return stmt.value
    return None


def get_first_arg_name(func: Callable[..., Any]) -> str | None:
    if is_typed_lambda(func):
        func = func.func

    if node := get_callable_ast(func):
        if node.args.args:
            return node.args.args[0].arg
    return Names.ARG.value


def get_func_name(final_expr_ast: ast.expr):
    temp_body_source = ast.unparse(final_expr_ast)
    source_hash = hashlib.sha256(temp_body_source.encode()).hexdigest()[:16]
    return f"{Names.PC_FUNC_.value}{source_hash}"


def get_module_ast(func_name: str, final_expr_ast: ast.expr) -> ast.Module:
    func_args = ast.arguments(args=[ast.arg(arg=Names.ARG.value)], defaults=[])
    func_def = ast.FunctionDef(
        name=func_name,
        args=func_args,
        body=[ast.Return(value=final_expr_ast)],
        decorator_list=[],
    )
    return ast.fix_missing_locations(ast.Module(body=[func_def], type_ignores=[]))


def add_cfunc(func_def: ast.FunctionDef) -> str:
    decorator = ast.Name(id=Names.CFUNC.value, ctx=ast.Load())
    func_def.decorator_list.insert(0, decorator)
    ast.fix_missing_locations(func_def)
    return ast.unparse(func_def)


def match_node(node: ast.FunctionDef | ast.Lambda, name: str) -> ast.FunctionDef | None:
    func_def: ast.FunctionDef | None = None
    match node:
        case ast.Lambda() as lambda_node:
            func_def = lambda_to_func(lambda_node, name)
        case ast.FunctionDef() as func_def_node:
            func_def_node.name = name
            func_def = func_def_node
    return func_def


def lambda_to_func(lambda_node: ast.Lambda, name: str) -> ast.FunctionDef:
    return ast.FunctionDef(
        name=name,
        args=lambda_node.args,
        body=[ast.Return(value=lambda_node.body)],
        decorator_list=[],
    )
