This documents contains excerpts from the PEP8 style guide, PEP484 type hints guide and the Google style guide docstring conventions. When in doubt, refer to them for details.

_"One of Guido's [the creator of Python] key insights is that code is read much more often than it is written. The guidelines provided here are intended to improve the readability of code and make it consistent across the wide spectrum of Python code. As PEP 20 says, 'Readability counts'."_

# Naming

* Class names should normally use the CapWords convention.
* Function names should be lowercase, with words separated by underscores as necessary to improve readability.
* Variable names follow the same convention as function names.
* Use leading underscore to indicate "internal use"
* Use trailing underscore to avoid conflicts with Python keywords

# Docstrings

* All modules should normally have docstrings, and all functions and classes exported by a module should also have docstrings.
* One-liners are for really obvious cases. They should not include method signatures.
* The docstring for a function or method should summarize its behavior and document its arguments, return value(s), side effects, exceptions raised, and restrictions on when it can be called (all if applicable). 

```python
def square_root(n):
    """Calculate the square root of a number.

    Args:
        n: the number to get the square root of.
    Returns:
        the square root of n.
    Raises:
        TypeError: if n is not a number.
        ValueError: if n is negative.

    """
``` 

# Comments
* Use inline comments sparingly. Don't explain the obvious.
* Block comments are useful when you have to write several lines of code to perform a single action, such as importing data from a file or updating a database entry. 


# Blankspace

* Surround top-level function and class definitions with two blank lines.
* Method definitions inside a class are surrounded by a single blank line.
* Use blank lines in functions, sparingly, to indicate logical sections.

# Spaces

* Always surround these binary operators with a single space on either side: assignment (=), augmented assignment (+=, -= etc.), comparisons (==, <, >, !=, <>, <=, >=, in, not in, is, is not), Booleans (and, or, not).
* Don't use spaces around the = sign when used to indicate a keyword argument, or when used to indicate a default value for an unannotated function parameter:
* When combining an argument annotation with a default value, however, do use spaces around the = sign: 
```python
# Correct:
def complex(real, imag=0.0):
    return magic(r=real, i=imag)

# Correct:
def complex(sep: AnyStr = None): 
    return magic(r=real, i=imag)
```

```python
# Wrong:
def complex(real, imag = 0.0):
    return magic(r = real, i = imag)
```

# Other recommendations

* Always refer to these conventions for new code and big refactorings.
* If you find minor deviations somewhere, feel free to fix them.
* If you find major deviations, remain consistent with the surrounding code.
* Docstrings are especially important in userland code since they can be used to generate documentation files.
* Type hints should always be used in userland, especially for public methods.

# References

* Style guide: https://www.python.org/dev/peps/pep-0008
* Type hints: https://www.python.org/dev/peps/pep-0484/
* Docstrings: https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings
