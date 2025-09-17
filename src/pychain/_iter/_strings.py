from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import TYPE_CHECKING

from .._core import iter_factory

if TYPE_CHECKING:
    from .._core import Iter


@dataclass(slots=True)
class StringNameSpace:
    _parent: Iterable[str]

    def upper(self) -> Iter[str]:
        """
        Return a copy of the string with all the cased characters converted to uppercase.

            >>> from pychain import Iter
            >>> Iter(["hello", "World"]).string.upper().to_list()
            ['HELLO', 'WORLD']
        """
        return iter_factory(s.upper() for s in self._parent)

    def lower(self) -> Iter[str]:
        """
        Return a copy of the string with all the cased characters converted to lowercase.

            >>> from pychain import Iter
            >>> Iter(["HELLO", "World"]).string.lower().to_list()
            ['hello', 'world']
        """
        return iter_factory(s.lower() for s in self._parent)

    def title(self) -> Iter[str]:
        """
        Return a titlecased version of the string.

        Words start with uppercase characters and all remaining cased characters are lowercase.

            >>> from pychain import Iter
            >>> Iter(["hello world", "another title"]).string.title().to_list()
            ['Hello World', 'Another Title']
        """
        return iter_factory(s.title() for s in self._parent)

    def strip(self, chars: str | None = None) -> Iter[str]:
        """
        Return a copy of the string with leading and trailing characters removed.

        The chars argument is a string specifying the set of characters to be removed.
        If omitted or None, the chars argument defaults to removing whitespace.

            >>> from pychain import Iter
            >>> Iter(["  hello  ", " world "]).string.strip().to_list()
            ['hello', 'world']
            >>> Iter(["__init__", "_main_"]).string.strip("_").to_list()
            ['init', 'main']
        """
        return iter_factory(s.strip(chars) for s in self._parent)

    def split(self, sep: str | None = None, maxsplit: int = -1) -> Iter[list[str]]:
        """
        Return a list of the words in the string, using sep as the delimiter string.

        If maxsplit is given, at most maxsplit splits are done.
        If sep is not specified or None, any whitespace string is a separator.

            >>> from pychain import Iter
            >>> Iter(["a-b-c", "d-e"]).string.split("-").to_list()
            [['a', 'b', 'c'], ['d', 'e']]
        """
        return iter_factory(s.split(sep, maxsplit) for s in self._parent)

    def capitalize(self) -> Iter[str]:
        """
        Return a capitalized version of the string.

        More specifically, make the first character have upper case and the rest lower case.

            >>> from pychain import Iter
            >>> Iter(["hello", "WORLD"]).string.capitalize().to_list()
            ['Hello', 'World']
        """
        return iter_factory(s.capitalize() for s in self._parent)

    def casefold(self) -> Iter[str]:
        """
        Return a casefolded copy of the string.

        Casefolded strings may be used for caseless matching.

            >>> from pychain import Iter
            >>> Iter(["ß", "MASSE"]).string.casefold().to_list()
            ['ss', 'masse']
        """
        return iter_factory(s.casefold() for s in self._parent)

    def swapcase(self) -> Iter[str]:
        """
        Return a copy of the string with uppercase characters converted to lowercase and vice versa.

            >>> from pychain import Iter
            >>> Iter(["hELLo", "wORLd"]).string.swapcase().to_list()
            ['HellO', 'WorlD']
        """
        return iter_factory(s.swapcase() for s in self._parent)

    def center(self, width: int, fillchar: str = " ") -> Iter[str]:
        """
        Return a centered string of length width.

        Padding is done using the specified fill character (default is a space).

            >>> from pychain import Iter
            >>> Iter(["py", "chain"]).string.center(10, "-").to_list()
            ['----py----', '--chain---']
        """
        return iter_factory(s.center(width, fillchar) for s in self._parent)

    def ljust(self, width: int, fillchar: str = " ") -> Iter[str]:
        """
        Return a left-justified string of length width.

        Padding is done using the specified fill character (default is a space).

            >>> from pychain import Iter
            >>> Iter(["py", "chain"]).string.ljust(10, "-").to_list()
            ['py--------', 'chain-----']
        """
        return iter_factory(s.ljust(width, fillchar) for s in self._parent)

    def rjust(self, width: int, fillchar: str = " ") -> Iter[str]:
        """
        Return a right-justified string of length width.

        Padding is done using the specified fill character (default is a space).

            >>> from pychain import Iter
            >>> Iter(["py", "chain"]).string.rjust(10, "-").to_list()
            ['--------py', '-----chain']
        """
        return iter_factory(s.rjust(width, fillchar) for s in self._parent)

    def zfill(self, width: int) -> Iter[str]:
        """
        Pad a numeric string with zeros on the left, to fill a field of the given width.

        The string is never truncated.

            >>> from pychain import Iter
            >>> Iter(["42", "-42"]).string.zfill(5).to_list()
            ['00042', '-0042']
        """
        return iter_factory(s.zfill(width) for s in self._parent)

    def lstrip(self, chars: str | None = None) -> Iter[str]:
        """
        Return a copy of the string with leading characters removed.

        The chars argument is a string specifying the set of characters to be removed.
        If omitted or None, the chars argument defaults to removing whitespace.

            >>> from pychain import Iter
            >>> Iter(["  hello", " world  "]).string.lstrip().to_list()
            ['hello', 'world  ']
            >>> Iter(["__init__", "_main_"]).string.lstrip("_").to_list()
            ['init__', 'main_']
        """
        return iter_factory(s.lstrip(chars) for s in self._parent)

    def rstrip(self, chars: str | None = None) -> Iter[str]:
        """
        Return a copy of the string with trailing characters removed.

        The chars argument is a string specifying the set of characters to be removed.
        If omitted or None, the chars argument defaults to removing whitespace.

            >>> from pychain import Iter
            >>> Iter(["  hello  ", " world "]).string.rstrip().to_list()
            ['  hello', ' world']
            >>> Iter(["__init__", "_main_"]).string.rstrip("_").to_list()
            ['__init', '_main']
        """
        return iter_factory(s.rstrip(chars) for s in self._parent)

    def partition(self, sep: str) -> Iter[tuple[str, str, str]]:
        """
        Split the string at the first occurrence of sep.

        The return value is a 3-tuple containing the part before the separator,
        the separator itself, and the part after the separator.

        If the separator is not found, the return value is a 3-tuple
        containing the string itself, followed by two empty strings.

            >>> from pychain import Iter
            >>> Iter(["a-b-c", "d-e"]).string.partition("-").to_list()
            [('a', '-', 'b-c'), ('d', '-', 'e')]
        """
        return iter_factory(s.partition(sep) for s in self._parent)

    def rpartition(self, sep: str) -> Iter[tuple[str, str, str]]:
        """
        Split the string at the last occurrence of sep.

        The return value is a 3-tuple containing the part before the separator,
        the separator itself, and the part after the separator.

        If the separator is not found, the return value is a 3-tuple
        containing two empty strings, followed by the string itself.

            >>> from pychain import Iter
            >>> Iter(["a-b-c", "d-e"]).string.rpartition("-").to_list()
            [('a-b', '-', 'c'), ('d', '-', 'e')]
        """
        return iter_factory(s.rpartition(sep) for s in self._parent)

    def rsplit(self, sep: str | None = None, maxsplit: int = -1) -> Iter[list[str]]:
        """
        Return a list of the words in the string, using sep as the delimiter string.

        If maxsplit is given, at most maxsplit splits are done, the rightmost ones.
        If sep is not specified or None, any whitespace string is a separator.

            >>> from pychain import Iter
            >>> Iter(["a-b-c", "d-e-f"]).string.rsplit("-", 1).to_list()
            [['a-b', 'c'], ['d-e', 'f']]
        """
        return iter_factory(s.rsplit(sep, maxsplit) for s in self._parent)

    def splitlines(self, keepends: bool = False) -> Iter[list[str]]:
        """
        Return a list of the lines in the string, breaking at line boundaries.

        Line breaks are not included in the resulting list unless keepends is given and true.

            >>> from pychain import Iter
            >>> Iter(["a\\nb", "c\\nd"]).string.splitlines().to_list()
            [['a', 'b'], ['c', 'd']]
        """
        return iter_factory(s.splitlines(keepends) for s in self._parent)

    def removeprefix(self, prefix: str) -> Iter[str]:
        """
        If the string starts with the prefix string, return string[len(prefix):].

        Otherwise, return a copy of the original string.

            >>> from pychain import Iter
            >>> Iter(["__main__", "prefix_val"]).string.removeprefix("__").to_list()
            ['main__', 'prefix_val']
        """
        return iter_factory(s.removeprefix(prefix) for s in self._parent)

    def removesuffix(self, suffix: str) -> Iter[str]:
        """
        If the string ends with the suffix string and that suffix is not empty, return string[:-len(suffix)].

        Otherwise, return a copy of the original string.

            >>> from pychain import Iter
            >>> Iter(["__main__", "val_suffix"]).string.removesuffix("__").to_list()
            ['__main', 'val_suffix']
        """
        return iter_factory(s.removesuffix(suffix) for s in self._parent)

    def replace(self, old: str, new: str, count: int = -1) -> Iter[str]:
        """
        Return a copy with all occurrences of substring old replaced by new.

        If the optional argument count is given, only the first count occurrences are replaced.

            >>> from pychain import Iter
            >>> Iter(["a-b-c", "d-e-f"]).string.replace("-", "_").to_list()
            ['a_b_c', 'd_e_f']
        """
        return iter_factory(s.replace(old, new, count) for s in self._parent)

    def count(self, sub: str) -> Iter[int]:
        """
        Return the number of non-overlapping occurrences of substring sub in the string.

            >>> from pychain import Iter
            >>> Iter(["hello", "world"]).string.count("l").to_list()
            [2, 1]
        """
        return iter_factory(s.count(sub) for s in self._parent)

    def endswith(self, suffix: str | tuple[str, ...]) -> Iter[bool]:
        """
        Return True if the string ends with the specified suffix, otherwise return False.

        suffix can also be a tuple of suffixes to look for.

            >>> from pychain import Iter
            >>> Iter(["main.py", "test.txt"]).string.endswith(".py").to_list()
            [True, False]
        """
        return iter_factory(s.endswith(suffix) for s in self._parent)

    def startswith(self, prefix: str | tuple[str, ...]) -> Iter[bool]:
        """
        Return True if the string starts with the specified prefix, otherwise return False.

        prefix can also be a tuple of prefixes to look for.

            >>> from pychain import Iter
            >>> Iter(["main.py", "test.txt"]).string.startswith("main").to_list()
            [True, False]
        """
        return iter_factory(s.startswith(prefix) for s in self._parent)

    def find(self, sub: str) -> Iter[int]:
        """
        Return the lowest index in the string where substring sub is found.

        Return -1 if sub is not found.

            >>> from pychain import Iter
            >>> Iter(["hello", "world"]).string.find("l").to_list()
            [2, 3]
        """
        return iter_factory(s.find(sub) for s in self._parent)

    def isalnum(self) -> Iter[bool]:
        """
        Return True if all characters in the string are alphanumeric and there is at least one character, False otherwise.

            >>> from pychain import Iter
            >>> Iter(["ab1", "ab-1"]).string.isalnum().to_list()
            [True, False]
        """
        return iter_factory(s.isalnum() for s in self._parent)

    def isalpha(self) -> Iter[bool]:
        """
        Return True if all characters in the string are alphabetic and there is at least one character, False otherwise.

            >>> from pychain import Iter
            >>> Iter(["abc", "ab1"]).string.isalpha().to_list()
            [True, False]
        """
        return iter_factory(s.isalpha() for s in self._parent)

    def isascii(self) -> Iter[bool]:
        """
        Return True if the string is empty or all characters in the string are ASCII, False otherwise.

            >>> from pychain import Iter
            >>> Iter(["abc", "à"]).string.isascii().to_list()
            [True, False]
        """
        return iter_factory(s.isascii() for s in self._parent)

    def isdecimal(self) -> Iter[bool]:
        """
        Return True if all characters in the string are decimal characters and there is at least one character, False otherwise.

            >>> from pychain import Iter
            >>> Iter(["123", "1.23"]).string.isdecimal().to_list()
            [True, False]
        """
        return iter_factory(s.isdecimal() for s in self._parent)

    def isdigit(self) -> Iter[bool]:
        """
        Return True if all characters in the string are digits and there is at least one character, False otherwise.

            >>> from pychain import Iter
            >>> Iter(["123", "1.23"]).string.isdigit().to_list()
            [True, False]
        """
        return iter_factory(s.isdigit() for s in self._parent)

    def isidentifier(self) -> Iter[bool]:
        """
        Return True if the string is a valid identifier according to the language definition.

            >>> from pychain import Iter
            >>> Iter(["my_var", "1var"]).string.isidentifier().to_list()
            [True, False]
        """
        return iter_factory(s.isidentifier() for s in self._parent)

    def islower(self) -> Iter[bool]:
        """
        Return True if all cased characters in the string are lowercase and there is at least one cased character, False otherwise.

            >>> from pychain import Iter
            >>> Iter(["hello", "Hello"]).string.islower().to_list()
            [True, False]
        """
        return iter_factory(s.islower() for s in self._parent)

    def isnumeric(self) -> Iter[bool]:
        """
        Return True if all characters in the string are numeric characters, and there is at least one character, False otherwise.

            >>> from pychain import Iter
            >>> Iter(["123", "1.23"]).string.isnumeric().to_list()
            [True, False]
        """
        return iter_factory(s.isnumeric() for s in self._parent)

    def isprintable(self) -> Iter[bool]:
        """
        Return True if all characters in the string are printable or the string is empty, False otherwise.

            >>> from pychain import Iter
            >>> Iter(["hello", "hello\\n"]).string.isprintable().to_list()
            [True, False]
        """
        return iter_factory(s.isprintable() for s in self._parent)

    def isspace(self) -> Iter[bool]:
        """
        Return True if there are only whitespace characters in the string and there is at least one character, False otherwise.

            >>> from pychain import Iter
            >>> Iter(["  ", " a "]).string.isspace().to_list()
            [True, False]
        """
        return iter_factory(s.isspace() for s in self._parent)

    def istitle(self) -> Iter[bool]:
        """
        Return True if the string is a titlecased string and there is at least one character, False otherwise.

            >>> from pychain import Iter
            >>> Iter(["Hello World", "Hello world"]).string.istitle().to_list()
            [True, False]
        """
        return iter_factory(s.istitle() for s in self._parent)

    def isupper(self) -> Iter[bool]:
        """
        Return True if all cased characters in the string are uppercase and there is at least one cased character, False otherwise.

            >>> from pychain import Iter
            >>> Iter(["HELLO", "Hello"]).string.isupper().to_list()
            [True, False]
        """
        return iter_factory(s.isupper() for s in self._parent)
