from .common import StaticTestBase, type_mismatch


class NativeDecoratorTests(StaticTestBase):
    def test_native_no_lib(self):
        codestr = """
        from __static__ import native, int64

        @native
        def something(i: int64) -> int64:
            return 1
        """
        self.type_error(
            codestr, "@native decorator must specify the library to be loaded"
        )

    def test_native_kwarg(self):
        codestr = """
        from __static__ import native, int64

        @native(x=1)
        def something(i: int64) -> int64:
            return 1
        """
        self.type_error(codestr, "@native decorator takes no keyword arguments")

    def test_native_stararg(self):
        codestr = """
        from __static__ import native, int64

        a = (1, 2)

        @native(*a)
        def something(i: int64) -> int64:
            return 1
        """
        self.type_error(codestr, "@native decorator takes no starred arguments")

    def test_native_multiple_arg(self):
        codestr = """
        from __static__ import native, int64

        @native("so.so", 1)
        def something(i: int64) -> int64:
            return 1
        """
        self.type_error(
            codestr,
            "@native decorator accepts a single parameter, the path to .so file",
        )

    def test_native_decorate_class(self):
        codestr = """
        from __static__ import native

        @native("so.so")
        class Hi:
            pass
        """
        self.type_error(codestr, "Cannot decorate a class with @native")

    def test_native_decorate_method(self):
        codestr = """
        from __static__ import native

        class Hi:
            @native("so.so")
            def fn(self):
                pass
        """
        self.type_error(codestr, "Cannot decorate a method with @native")

    def test_native_some_function_body(self):
        codestr = """
        from __static__ import native, int64

        @native("so.so")
        def something(i: int64) -> int64:
            return 1
        """

        self.type_error(
            codestr,
            "@native callables cannot contain a function body, only 'pass' is allowed",
        )

    def test_native_valid_usage_in_nonstatic_module(self):
        codestr = """
        from __static__ import native, int64

        @native("so.so")
        def something(j: int64) -> int64:
            pass
        """

        with self.in_strict_module(codestr) as mod:
            with self.assertRaisesRegex(
                RuntimeError,
                "native callable 'something' can only be called from static modules",
            ):
                mod.something(1)

    def test_native_usage_with_kwarg(self):
        binding_codestr = """
        from __static__ import native, int64, box, unbox

        @native("libc.so.6")
        def abs(i: int64, j: int64 = 4) -> int64:
            pass
        """
        self.type_error(binding_codestr, "@native callables cannot contain kwargs")

    def test_native_usage_with_posonly_arg(self):
        binding_codestr = """
        from __static__ import native, int64, box, unbox

        @native("libc.so.6")
        def abs(i: int64, /) -> int64:
            pass
        """
        self.type_error(
            binding_codestr, "@native callables cannot contain pos-only args"
        )

    def test_native_usage_with_kwonly_arg(self):
        binding_codestr = """
        from __static__ import native, int64, box, unbox

        @native("libc.so.6")
        def abs(i: int64, *, j: int64 = 33) -> int64:
            pass
        """
        self.type_error(
            binding_codestr, "@native callables cannot contain kw-only args"
        )

    def test_native_call_with_pyobject(self):
        binding_codestr = """
        from __static__ import native, int64, box, unbox

        @native("libc.so.6")
        def abs(i: int64) -> int64:
            pass

        def invoke_abs(i: int) -> int:
            res = abs(i)
            return box(res)
        """
        self.type_error(
            binding_codestr,
            "type mismatch: int received for positional arg 'i', expected int64",
        )

    def test_decorate_already_decorated_fn(self):
        codestr = """
        from __static__ import native
        from typing import final

        @native("so.so")
        @final
        def fn(self):
            pass
        """
        self.type_error(
            codestr, "@native decorator cannot be used with other decorators"
        )

    def test_decorate_native_fn(self):
        codestr = """
        from __static__ import native
        from typing import final

        @final
        @native("so.so")
        def fn():
            pass
        """
        self.type_error(
            codestr, "@native decorator cannot be used with other decorators"
        )
