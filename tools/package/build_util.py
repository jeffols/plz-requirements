import ast
import astor

from yapf.yapflib.yapf_api import FormatCode


class BuildSpec:
    def __init__(self, source=None):
        self.clear()
        if source:
            self.populate_from_source(source)

    def clear(self):
        self._tree = ast.parse("")
        self._package = None
        self._function_defs = []
        self._exps = []
        self._pips = {}
        self._tests = {}

    def _get_ast_type(self, _type):
        return list(filter(lambda part: _type == type(part), self._tree.body))

    def populate_from_source(self, source):
        if hasattr(source, 'read'):
            source = source.read()
        self._tree = ast.parse(source)
        self._function_defs = {}
        for function_def in self._get_ast_type(ast.FunctionDef):
            item = BuildFunctionDef(function_def)
            self._function_defs[item.name] = item
        self._exprs = self._get_ast_type(ast.Expr)
        self._pips = {}
        for expr in self._exprs:
            if "pip_library" == expr.value.func.id:
                item = BuildPipLibrary(expr)
                self._pips[item.name] = item
            elif "python_wheel" == expr.value.func.id:
                item = BuildPythonWheel(expr)
                self._pips[item.name] = item
            elif "package" == expr.value.func.id:
                assert None == self._package  # should only be one
                self._package = BuildPackage(expr)
            elif "python_test" == expr.value.func.id:
                item = BuildPythonTest(expr)
                self._tests[item.name] = item
            else:
                print(f"unknown expr type {expr.value.func.id}")
        return self

    def add_pip_able(self, pip_able):
        self._pips[pip_able.name] = pip_able

    def add_function_def(self, function_def):
        self._function_defs[function_def.name] = function_def

    def output(self):
        source = ""
        if self._package:
            source = astor.to_source(self._package.ast)
        if self._function_defs:
            source += '\n'.join([
                astor.to_source(self._function_defs[name].ast)
                for name in sorted(self._function_defs)
            ])
        if self._pips:
            source += '\n'.join([
                FormatCode(astor.to_source(self._pips[name].ast), style_config="./yapf.cfg")[0] 
                for name in sorted(self._pips)
                ])
        source += "\n"
        if self._tests:
            source += '\n'.join([
                astor.to_source(self._tests[name].ast)
                for name in sorted(self._tests)
            ])
        return source


class BuildItem:
    def __init__(self, ast_item):
        self.ast = ast_item

    @classmethod
    def from_Expr(cls, ast_item):
        return cls(ast_item)

    @classmethod
    def from_source(cls, source):
        tree = ast.parse(source)
        assert 1 == len(tree.body)
        return cls(tree.body[0])


class BuildExpr(BuildItem):
    def __init__(self, ast_expr):
        super().__init__(ast_expr)
        assert self.LABEL == ast_expr.value.func.id
        self._expr = ast_expr
        self._keywords = {}
        for keyword in ast_expr.value.keywords:
            self._keywords[keyword.arg] = keyword.value

    @property
    def name(self):
        assert ast.Str == type(self._keywords.get('name'))
        return self._keywords.get('name').s


class BuildPipAble(BuildExpr):
    def __repr__(self):
        return f'{self.__class__.__name__}(name="{self.name}", version="{self.version}")'

    @property
    def name(self):
        field = 'package_name' if 'package_name' in self._keywords else 'name'
        assert ast.Str == type(self._keywords.get(field))
        return self._keywords.get(field).s

    @property
    def version(self):
        assert ast.Str == type(self._keywords.get('version'))
        return self._keywords.get('version').s

    @property
    def outs(self):
        return self._keywords.get('outs')

    @property
    def deps(self):
        return self._keywords.get('deps')


class BuildPipLibrary(BuildPipAble):
    LABEL = "pip_library"


class BuildPythonWheel(BuildPipAble):
    LABEL = "python_wheel"


class BuildPythonTest(BuildExpr):
    LABEL = "python_test"


class BuildPackage(BuildExpr):
    LABEL = "package"


class BuildFunctionDef(BuildItem):
    def __init__(self, ast_function_def):
        super().__init__(ast_function_def)
        self._function_def = ast_function_def

    @property
    def name(self):
        return self._function_def.name

    def __repr__(self):
        return astor.to_source(self._function_def)

