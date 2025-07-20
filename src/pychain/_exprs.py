import ast
import inspect
import uuid
from collections.abc import Callable, Iterable, Iterator
from functools import partial, reduce
from itertools import dropwhile, product, starmap, takewhile
from random import Random
from typing import Any, Self, TypeGuard, override

import cytoolz.dicttoolz as dcz
import cytoolz.itertoolz as itz

from . import funcs as fn
from ._protocols import (
    INLINEABLE_BUILTINS,
    CheckFunc,
    CompileResult,
    ProcessFunc,
    Scope,
    TransformFunc,
)


class BaseExpr[P, R]:
    def __init__(
        self,
        pipeline: list[Callable[..., Any]] | None = None,
        node: ast.expr | None = None,
    ) -> None:
        self._node: ast.expr = (
            node if node is not None else ast.Name(id="arg", ctx=ast.Load())
        )
        self._scope: dict[str, Any] = {}
        self.__pychain_expr__ = True
        self._pipeline = pipeline if pipeline is not None else []

    def __repr__(self):
        return f"class {self.__class__.__name__}(pipeline:\n{self._pipeline.__repr__()})\n)"

    def compose(self, *fns: ProcessFunc[R]):
        for op in fns:
            self._pipeline.append(op)
        return self

    def collect(self) -> fn.Func[P, R]:
        return collect_pipeline(self._pipeline)

    def to_ast(self, func_scope: Scope) -> ast.expr:
        func_scope.update(self._scope)
        return self._node

    def _new_node(self, node: ast.expr, scope: Scope) -> Self:
        new_instance = self.__class__(node=node)
        new_instance._scope = scope
        return new_instance

    def _new_scope(self) -> Scope:
        return self._scope.copy()

    def _binary_op(self, other: Any, op: ast.operator) -> Self:
        new_scope: Scope = self._new_scope()
        right_node = _value_to_ast(other, new_scope)
        new_node = ast.BinOp(left=self._node, op=op, right=right_node)
        return self._new_node(new_node, new_scope)

    def _reflected_binary_op(self, other: Any, op: ast.operator) -> Self:
        new_scope: Scope = self._new_scope()
        left_node = _value_to_ast(other, new_scope)
        new_node = ast.BinOp(left=left_node, op=op, right=self._node)
        return self._new_node(new_node, new_scope)

    def _compare_op(self, other: Any, op: ast.cmpop) -> Self:
        new_scope = self._new_scope()
        right_node = _value_to_ast(other, new_scope)
        new_node = ast.Compare(left=self._node, ops=[op], comparators=[right_node])
        return self._new_node(new_node, new_scope)

    def _logical_op(self, other: Any, op: ast.boolop) -> Self:
        new_scope = self._new_scope()
        right_node = _value_to_ast(other, new_scope)
        if isinstance(self._node, ast.BoolOp) and isinstance(self._node.op, type(op)):
            new_node = ast.BoolOp(op=op, values=[*self._node.values, right_node])
        else:
            new_node = ast.BoolOp(op=op, values=[self._node, right_node])
        return self._new_node(new_node, new_scope)

    def __getattr__(self, name: str) -> Self:
        new_node = ast.Attribute(value=self._node, attr=name, ctx=ast.Load())
        return self.__class__(node=new_node)

    def __call__(self, *args: Any, **kwargs: Any) -> Self:
        new_scope: Scope = self._new_scope()
        ast_args = [_value_to_ast(arg, new_scope) for arg in args]
        ast_kwargs = [
            ast.keyword(arg=k, value=_value_to_ast(v, new_scope))
            for k, v in kwargs.items()
        ]

        new_node = ast.Call(func=self._node, args=ast_args, keywords=ast_kwargs)
        return self._new_node(new_node, new_scope)

    def __getitem__(self, key: Any) -> Self:
        new_scope = self._new_scope()
        slice_node = _value_to_ast(key, new_scope)
        new_node = ast.Subscript(value=self._node, slice=slice_node, ctx=ast.Load())
        return self._new_node(new_node, new_scope)

    def __add__(self, other: Any) -> Self:
        return self._binary_op(other, ast.Add())

    def __sub__(self, other: Any) -> Self:
        return self._binary_op(other, ast.Sub())

    def __mul__(self, other: Any) -> Self:
        return self._binary_op(other, ast.Mult())

    def __truediv__(self, other: Any) -> Self:
        return self._binary_op(other, ast.Div())

    def __radd__(self, other: Any) -> Self:
        return self._reflected_binary_op(other, ast.Add())

    def __rsub__(self, other: Any) -> Self:
        return self._reflected_binary_op(other, ast.Sub())

    def __rmul__(self, other: Any) -> Self:
        return self._reflected_binary_op(other, ast.Mult())

    def __rtruediv__(self, other: Any) -> Self:
        return self._reflected_binary_op(other, ast.Div())

    def __mod__(self, other: Any) -> Self:
        return self._binary_op(other, ast.Mod())

    def __pow__(self, other: Any) -> Self:
        return self._binary_op(other, ast.Pow())

    def __matmul__(self, other: Any) -> Self:
        return self._binary_op(other, ast.MatMult())

    def __rmod__(self, other: Any) -> Self:
        return self._reflected_binary_op(other, ast.Mod())

    def __rpow__(self, other: Any) -> Self:
        return self._reflected_binary_op(other, ast.Pow())

    def __rmatmul__(self, other: Any) -> Self:
        return self._reflected_binary_op(other, ast.MatMult())

    def __and__(self, other: Any) -> Self:
        return self._logical_op(other, ast.And())

    def __or__(self, other: Any) -> Self:
        return self._logical_op(other, ast.Or())

    def __xor__(self, other: Any) -> Self:
        return self._binary_op(other, ast.BitXor())

    def __lshift__(self, other: Any) -> Self:
        return self._binary_op(other, ast.LShift())

    def __rshift__(self, other: Any) -> Self:
        return self._binary_op(other, ast.RShift())

    def __rand__(self, other: Any) -> Self:
        return self._reflected_binary_op(other, ast.BitAnd())

    def __ror__(self, other: Any) -> Self:
        return self._reflected_binary_op(other, ast.BitOr())

    def __rxor__(self, other: Any) -> Self:
        return self._reflected_binary_op(other, ast.BitXor())

    def __rlshift__(self, other: Any) -> Self:
        return self._reflected_binary_op(other, ast.LShift())

    def __rrshift__(self, other: Any) -> Self:
        return self._reflected_binary_op(other, ast.RShift())

    def __lt__(self, other: Any) -> Self:  # <
        return self._compare_op(other, ast.Lt())

    def __le__(self, other: Any) -> Self:
        return self._compare_op(other, ast.LtE())

    def __gt__(self, other: Any) -> Self:
        return self._compare_op(other, ast.Gt())

    def __ge__(self, other: Any) -> Self:
        return self._compare_op(other, ast.GtE())

    @override
    def __eq__(self, other: Any) -> Self:  # type: ignore[override]
        return self._compare_op(other, ast.Eq())

    @override
    def __ne__(self, other: Any) -> Self:  # type: ignore[override]
        return self._compare_op(other, ast.NotEq())

class Expr[P, R](BaseExpr[P, R]):
    def _do[T](self, f: Callable[[R], T]) -> "Expr[P, T]":
        return Expr(pipeline=self._pipeline + [f])

    def into_partial[T](self, f: Callable[[P], T], *args: Any, **kwargs: Any):
        return self._do(partial(f, *args, **kwargs))

    def do(self, f: ProcessFunc[R]) -> "Expr[P, R]":
        return self._do(f)

    def into[T](self, obj: Callable[[R], T]) -> "Expr[P, T]":
        return self._do(obj)

    def into_str(self, txt: str) -> "Expr[P, str]":
        return self._do(partial(str.format, txt))

    def into_expr[T](self, obj: T) -> "Expr[P, T]":
        return self._do(obj)  # type: ignore

class Iter[VP, VR](BaseExpr[Iterable[VP], VR]):
    def _do[T](self, f: Callable[[Iterable[VR]], T]) -> "Iter[VP, T]":
        return Iter(pipeline=self._pipeline + [f])

    def into[T](self, obj: Callable[[Iterable[VR]], T]) -> "Iter[VP, T]":
        return self._do(obj)

    def map_compose(self, fns: Iterable[ProcessFunc[VR]]) -> "Iter[VP, VR]":
        mapping_func = collect_pipeline(list(fns))
        return self._do(partial(map, mapping_func))  # type: ignore

    def agg[T](self, f: Callable[[Iterable[VR]], T]) -> "Expr[Iterable[VP], T]":
        return Expr(self._pipeline + [f])

    def is_distinct(self):
        return self._do(itz.isdistinct)

    def is_all(self):
        return self._do(all)

    def is_any(self):
        return self._do(any)

    def to_dict(self):
        return self._do(fn.iter_to_dict)

    def group_by[K](
        self, on: TransformFunc[VR, K]
    ) -> "Struct[VP, K, VR, Iterable[VR]]":
        return Struct([self._do(partial(itz.groupby, on)).collect().extract()])

    def into_frequencies(self) -> "Struct[VP, int, VR, int]":
        return Struct([self._do(itz.frequencies).collect().extract()])

    def reduce_by[K](
        self, key: TransformFunc[VR, K], binop: Callable[[VR, VR], VR]
    ) -> "Iter[VP, dict[K, VR]]":
        return self._do(partial(itz.reduceby, key=key, binop=binop))

    def map[T](self, f: TransformFunc[VR, T] | T) -> "Iter[VP, T]":
        return self._do(f=partial(map, f))  # type: ignore

    def filter(self, f: CheckFunc[VR] | bool) -> "Iter[VP, VR]":
        return self._do(f=partial(filter, f))  # type: ignore

    def flat_map(self, f: TransformFunc[VR, Iterable[VR]]):
        return self._do(f=partial(fn.flat_map, func=f))

    def starmap(self, f: TransformFunc[VR, VR]):
        return self._do(f=partial(starmap, f))  # type: ignore

    def take_while(self, predicate: CheckFunc[VR]) -> "Iter[VP, VR]":
        return self._do(f=partial(takewhile, predicate))  # type: ignore

    def drop_while(self, predicate: CheckFunc[VR]) -> "Iter[VP, VR]":
        return self._do(f=partial(dropwhile, predicate))  # type: ignore

    def interpose(self, element: VR):
        return self._do(f=partial(itz.interpose, element))

    def top_n(self, n: int, key: Callable[[VR], Any] | None = None):
        return self._do(f=partial(itz.topk, n, key=key))

    def random_sample(self, probability: float, state: Random | int | None = None):
        return self._do(f=partial(itz.random_sample, probability, random_state=state))

    def accumulate(self, f: Callable[[VR, VR], VR]):
        return self._do(f=partial(itz.accumulate, f))

    def reduce[V](self, f: Callable[[VR, VR], VR]):
        return self._do(f=partial(reduce, f))

    def insert_left(self, value: VR):
        return self._do(f=partial(itz.cons, value))

    def peekn(self, n: int, note: str | None = None):
        return self._do(f=partial(fn.peekn, n=n, note=note))

    def peek(self, note: str | None = None):
        return self._do(f=partial(fn.peek, note=note))

    def head(self, n: int):
        return self._do(f=partial(itz.take, n))

    def tail(self, n: int):
        return self._do(f=partial(itz.tail, n))

    def drop_first(self, n: int):
        return self._do(f=partial(itz.drop, n))

    def every(self, index: int):
        return self._do(f=partial(itz.take_nth, index))

    def repeat(self, n: int):
        return self._do(f=partial(fn.repeat, n=n))

    def unique(self):
        return self._do(f=itz.unique)

    def tap(self, func: Callable[[VR], None]):
        return self._do(f=partial(fn.tap, func=func))

    def enumerate(self) -> "Iter[VP, enumerate[VR]]":
        return self._do(f=enumerate)

    def flatten(self) -> "Iter[VP, Any]":
        return self._do(f=itz.concat)

    def partition(
        self, n: int, pad: VR | None = None
    ) -> "Iter[VP, Iterator[tuple[VR, ...]]]":
        return self._do(f=partial(itz.partition, n, pad=pad))

    def partition_all(self, n: int) -> "Iter[VP, Iterator[tuple[VR, ...]]]":
        return self._do(f=partial(itz.partition_all, n))

    def rolling(self, length: int):
        return self._do(f=partial(itz.sliding_window, length))

    def cross_join(self, other: Iterable[Any]):
        return self._do(partial(product, other))

    def diff(
        self,
        others: Iterable[Iterable[VR]],
        default: Any | None = None,
        key: ProcessFunc[VR] | None = None,
    ):
        return self._do(f=partial(fn.diff, others=others, key=key))

    def zip_with(
        self, others: Iterable[Iterable[VR]], strict: bool = False
    ) -> "Iter[VP, zip[tuple[Any, ...]]]":
        return self._do(f=partial(fn.zip_with, others=others, strict=strict))

    def merge_sorted(
        self, others: Iterable[Iterable[VR]], sort_on: Callable[[VR], Any] | None = None
    ):
        return self._do(f=partial(fn.merge_sorted, others=others, sort_on=sort_on))

    def interleave(self, *others: Iterable[VR]):
        return self._do(f=partial(fn.interleave, others=others))

    def concat(self, *others: Iterable[VR]):
        return self._do(f=partial(fn.concat, others=others))

    def first(self) -> "Expr[Iterable[VP], VR]":
        return self.agg(itz.first)

    def second(self) -> "Expr[Iterable[VP], VR]":
        return self.agg(itz.second)

    def last(self) -> "Expr[Iterable[VP], VR]":
        return self.agg(itz.last)

    def length(self) -> "Expr[Iterable[VP], int]":
        return self.agg(itz.count)

    def at_index(self, index: int):
        return self.agg(partial(itz.nth, index))


class Struct[KP, VP, KR, VR](BaseExpr[dict[KP, VP], dict[KR, VR]]):
    def _do[KT, VT](
        self, f: Callable[[dict[KR, VR]], dict[KT, VT]]
    ) -> "Struct[KP, VP, KR, VT]":
        return Struct(self._pipeline + [f])

    def map_keys[T](self, f: TransformFunc[KR, T]) -> "Struct[KP, VP, T, VR]":
        return self._do(f=partial(dcz.keymap, f))  # type: ignore

    def map_values[T](self, f: TransformFunc[VR, T]) -> "Struct[KP, VP, KR, T]":
        return self._do(f=partial(dcz.valmap, f))  # type: ignore

    def select(self, predicate: CheckFunc[KR]):
        return self._do(f=partial(dcz.keyfilter, predicate))

    def filter(self, predicate: CheckFunc[VR]):
        return self._do(f=partial(dcz.valfilter, predicate))

    def filter_items(
        self,
        predicate: CheckFunc[tuple[KR, VR]],
    ):
        return self._do(partial(dcz.itemfilter, predicate))

    def map_items[KT, VT](
        self,
        f: TransformFunc[tuple[KR, VR], tuple[KT, VT]],
    ):
        return self._do(partial(dcz.itemmap, f))

    def with_key(self, key: KR, value: VR):
        return self._do(f=partial(dcz.assoc, key=key, value=value))

    def with_nested_key(self, keys: Iterable[KR] | KR, value: VR):
        return self._do(f=partial(dcz.assoc_in, keys=keys, value=value))

    def flatten_keys(self) -> "Struct[KP, VP, str, VR]":
        return self._do(f=fn.flatten_recursive)  # type: ignore

    def update_in(self, *keys: KR, f: ProcessFunc[VR]):
        return self._do(f=partial(dcz.update_in, keys=keys, func=f))

    def merge(self, *others: dict[KR, VR]):
        return self._do(f=partial(fn.merge, others=others))

    def merge_with(self, f: Callable[[Iterable[VR]], VR], *others: dict[KR, VR]):
        return self._do(f=partial(dcz.merge_with, f, *others))

    def drop(self, *keys: KR):
        return self._do(f=partial(fn.drop, keys=keys))


# ----------- compile functions -----------


def is_obj_expr(val: Any) -> TypeGuard[BaseExpr[Any, Any]]:
    return getattr(val, "__pychain_expr__", False)


def _value_to_ast(value: Any, scope: Scope) -> ast.expr:
    match value:
        case str() | int() | float() | bool() | None:
            return ast.Constant(value=value)
        case BaseExpr():
            return value.to_ast(scope)
        case _:
            var_name = f"__arg_{str(uuid.uuid4()).replace('-', '')[:8]}"
            scope[var_name] = value
            return ast.Name(id=var_name, ctx=ast.Load())


def collect_pipeline[P](pipeline: list[Callable[[P], Any]]) -> fn.Func[P, Any]:
    try:
        compiled_func, source_code = collect_ast(pipeline)
    except Exception as e:
        print(f"Error collecting AST: {e}")
        compiled_func, source_code = collect_scope(pipeline)
    return fn.Func(compiled_func, source_code)


def collect_scope[P](_pipeline: list[Callable[[P], Any]]) -> CompileResult[P]:
    func_scope: Scope = {}
    func_name: str = _get_fn_name()
    nested_expr = "arg"
    for i, func in enumerate(_pipeline):
        scope_func_name: str = f"__func_{i}"
        func_scope[scope_func_name] = func
        nested_expr: str = f"{scope_func_name}({nested_expr})"
    code_lines: list[str] = [f"def {func_name}(arg):", f"    return {nested_expr}"]

    function_code: str = "\n".join(code_lines)
    exec(function_code, globals=func_scope)

    return func_scope[func_name], function_code


def collect_ast[P](_pipeline: list[Callable[[P], Any]]) -> CompileResult[P]:
    final_expr_ast = ast.Name(id="arg", ctx=ast.Load())
    func_scope: Scope = {}

    for i, func in enumerate(_pipeline):
        if is_obj_expr(func):
            final_expr_ast: ast.expr = func.to_ast(func_scope)
            continue
        if func in INLINEABLE_BUILTINS:
            final_expr_ast = _from_builtin(func, final_expr_ast)
            continue
        try:
            final_expr_ast = _get_final_ast(func, final_expr_ast)

        except (TypeError, OSError):
            final_expr_ast = _fallback(func_scope, func, i, final_expr_ast)
    return _finalize(final_expr_ast, func_scope)


def _extract_return_expression(func_source: str) -> ast.expr | None:
    tree: ast.Module = ast.parse(func_source)
    func_def: ast.stmt = tree.body[0]

    if not isinstance(func_def, ast.FunctionDef):
        raise ValueError("Provided source is not a function definition.")
    if len(func_def.body) > 1:
        raise ValueError(
            "Function is too complex to inline (contains multiple statements)."
        )
    return_stmt: ast.stmt = func_def.body[-1]
    if isinstance(return_stmt, ast.Return):
        return return_stmt.value
    raise ValueError("Function does not contain a simple return expression.")


def _from_builtin(func: Callable[..., Any], final_expr_ast: ast.expr) -> ast.Call:
    return ast.Call(
        func=ast.Name(id=func.__name__, ctx=ast.Load()),  # Utilise le vrai nom: 'float'
        args=[final_expr_ast],
        keywords=[],
    )


class InlineTransformer(ast.NodeTransformer):
    def __init__(self, arg_name: str, replacement_node: ast.AST) -> None:
        self.arg_name: str = arg_name
        self.replacement_node: ast.AST = replacement_node

    def visit_Name(self, node: ast.Name) -> Any:
        if node.id == self.arg_name:
            return self.replacement_node
        return node


def _create_func_ast(final_expr_ast: ast.expr, func_name: str) -> ast.Module:
    final_func_ast = ast.Module(
        body=[
            ast.FunctionDef(
                name=func_name,
                args=ast.arguments(
                    args=[ast.arg(arg="arg")],
                    posonlyargs=[],
                    kwonlyargs=[],
                    kw_defaults=[],
                    defaults=[],
                ),
                body=[ast.Return(value=final_expr_ast)],
                decorator_list=[],
            )
        ],
        type_ignores=[],
    )
    final_func_ast: ast.Module = ast.fix_missing_locations(final_func_ast)
    return final_func_ast


def _get_final_ast(func: Callable[..., Any], final_expr_ast: ast.expr) -> ast.Call:
    source = inspect.getsource(func)
    func_ast = ast.parse(source).body[0]

    if not isinstance(func_ast, ast.FunctionDef):
        raise TypeError("L'élément n'est pas une fonction standard.")
    current_arg_name: str = func_ast.args.args[0].arg
    return_expr_ast = _extract_return_expression(source)
    if return_expr_ast is None:
        raise ValueError("Aucune expression de return trouvée dans la fonction.")
    transformer = InlineTransformer(current_arg_name, final_expr_ast)
    return transformer.visit(return_expr_ast)


def _fallback(
    scope: dict[str, Any], func: Callable[..., Any], i: int, final_expr_ast: ast.expr
) -> ast.Call:
    scope_func_name: str = f"__func_{i}"
    scope[scope_func_name] = func
    return ast.Call(
        func=ast.Name(id=scope_func_name, ctx=ast.Load()),
        args=[final_expr_ast],
        keywords=[],
    )


def _finalize(
    final_expr_ast: ast.expr, func_scope: dict[str, Any]
) -> tuple[Callable[..., Any], str]:
    func_name: str = _get_fn_name()
    final_func_ast: ast.Module = _create_func_ast(final_expr_ast, func_name)
    source_code: str = ast.unparse(final_func_ast)
    code_obj = compile(final_func_ast, filename="<ast>", mode="exec")

    exec(code_obj, func_scope)
    return func_scope[func_name], source_code


def _get_fn_name() -> str:
    return f"generated_func_{str(uuid.uuid4()).replace('-', '')}"
