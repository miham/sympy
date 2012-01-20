from basic import Basic
from expr import Expr
from evalf import EvalfMixin
from sympify import _sympify

__all__ = (
 'Rel', 'Eq', 'Ne', 'Lt', 'Le', 'Gt', 'Ge',
 'Relational', 'Equality', 'Unequality', 'StrictLessThan', 'LessThan',
 'StrictGreaterThan', 'GreaterThan',
)


def Rel(a, b, op):
    """
    A handy wrapper around the Relational class.
    Rel(a,b, op)

    Examples
    ========

    >>> from sympy import Rel
    >>> from sympy.abc import x, y
    >>> Rel(y, x+x**2, '==')
    y == x**2 + x

    """
    return Relational(a,b,op)

def Eq(a, b=0):
    """
    A handy wrapper around the Relational class.
    Eq(a,b)

    Examples
    ========

    >>> from sympy import Eq
    >>> from sympy.abc import x, y
    >>> Eq(y, x+x**2)
    y == x**2 + x

    """
    return Relational(a,b,'==')

def Ne(a, b):
    """
    A handy wrapper around the Relational class.
    Ne(a,b)

    Examples
    ========

    >>> from sympy import Ne
    >>> from sympy.abc import x, y
    >>> Ne(y, x+x**2)
    y != x**2 + x

    """
    return Relational(a,b,'!=')

def Lt(a, b):
    """
    A handy wrapper around the Relational class.
    Lt(a,b)

    Examples
    ========

    >>> from sympy import Lt
    >>> from sympy.abc import x, y
    >>> Lt(y, x+x**2)
    y < x**2 + x

    """
    return Relational(a,b,'<')

def Le(a, b):
    """
    A handy wrapper around the Relational class.
    Le(a,b)

    Examples
    ========

    >>> from sympy import Le
    >>> from sympy.abc import x, y
    >>> Le(y, x+x**2)
    y <= x**2 + x

    """
    return Relational(a,b,'<=')

def Gt(a, b):
    """
    A handy wrapper around the Relational class.
    Gt(a,b)

    Examples
    ========

    >>> from sympy import Gt
    >>> from sympy.abc import x, y
    >>> Gt(y, x + x**2)
    y > x**2 + x

    """
    return Relational(a,b,'>')

def Ge(a, b):
    """
    A handy wrapper around the Relational class.
    Ge(a,b)

    Examples
    ========

    >>> from sympy import Ge
    >>> from sympy.abc import x, y
    >>> Ge(y, x + x**2)
    y >= x**2 + x

    """
    return Relational(a,b,'>=')

class Relational(Expr, EvalfMixin):

    __slots__ = []

    is_Relational = True

    # ValidRelationOperator - Defined below, because the necessary classes
    #   have not yet been defined

    def __new__(cls, lhs, rhs, rop=None, **assumptions):
        lhs = _sympify(lhs)
        rhs = _sympify(rhs)
        if cls is not Relational:
            rop_cls = cls
        else:
            try:
                rop_cls = Relational.ValidRelationOperator[ rop ]
            except KeyError:
                msg = "Invalid relational operator symbol: '%r'"
                raise ValueError(msg % repr(rop))
        if lhs.is_number and rhs.is_number and lhs.is_real and rhs.is_real:
            # Just becase something is a number, doesn't mean you can evalf it.
            Nlhs = lhs.evalf()
            if Nlhs.is_Number:
                # S.Zero.evalf() returns S.Zero, so test Number instead of Float
                Nrhs = rhs.evalf()
                if Nrhs.is_Number:
                    return rop_cls._eval_relation(Nlhs, Nrhs)

        obj = Expr.__new__(rop_cls, lhs, rhs, **assumptions)
        return obj

    @property
    def lhs(self):
        return self._args[0]

    @property
    def rhs(self):
        return self._args[1]

    def _eval_subs(self, old, new):
        if self == old:
            return new
        return self.__class__(self.lhs._eval_subs(old, new), self.rhs._eval_subs(old, new))

    def _eval_evalf(self, prec):
        return self.func(*[s._evalf(prec) for s in self.args])

    def doit(self, **hints):
        lhs = self.lhs
        rhs = self.rhs
        if hints.get('deep', True):
            lhs = lhs.doit(**hints)
            rhs = rhs.doit(**hints)
        return self._eval_relation_doit(lhs, rhs)

    @classmethod
    def _eval_relation_doit(cls, lhs, rhs):
        return cls._eval_relation(lhs, rhs)

class Equality(Relational):

    rel_op = '=='

    __slots__ = []

    is_Equality = True

    @classmethod
    def _eval_relation(cls, lhs, rhs):
        return lhs == rhs

    @classmethod
    def _eval_relation_doit(cls, lhs, rhs):
        return Eq(lhs, rhs)

    def __nonzero__(self):
        return self.lhs.compare(self.rhs)==0

class Unequality(Relational):

    rel_op = '!='

    __slots__ = []

    @classmethod
    def _eval_relation(cls, lhs, rhs):
        return lhs != rhs

    @classmethod
    def _eval_relation_doit(cls, lhs, rhs):
        return Ne(lhs, rhs)

    def __nonzero__(self):
        return self.lhs.compare(self.rhs)!=0

class _Greater(Relational):
    """\
Not intended for general use; _Greater is only used so that GreaterThan and
StrictGreaterThan may subclass it for the .gts and .lts properties.
"""
    __slots__ = ()

    @property
    def gts(self):
        return self._args[0]

    @property
    def lts(self):
        return self._args[1]

class _Less(Relational):
    """\

Not intended for general use; _Less is only used so that LessThan and
StrictLessThan may subclass it for the .gts and .lts properties.
"""
    __slots__ = ()

    @property
    def gts(self):
        return self._args[1]

    @property
    def lts(self):
        return self._args[0]

class GreaterThan(_Greater):
    """\
The *Than classes represent inequal relationships, where the left-hand side is
generally bigger or smaller than the right-hand side.  For example, the
GreaterThan class represents an inequal relationship where the left-hand side is
at least as big as the right side, if not bigger.  In mathematical notation:

    lhs >= rhs

In total, there are four *Than classes, to represent the four inequalities:

GreaterThan       (>=)
LessThan          (<=)
StrictGreaterThan (>)
StrictLessThan    (<)

In addition to the normal .lhs and .rhs of Relations, *Than inequality objects
also have the .lts and .gts properties, which represent the "less than side" and
"greater than side" of the operator.  Use of .lts and .gts in an algorithm
rather than .lhs, .rhs, and an assumption of inequality direction, will make
more explicit the intent of a certain section of code, and will make it
similarly more robust to client code changes:

    >>> from sympy import GreaterThan, StrictGreaterThan
    >>> from sympy import LessThan,    StrictLessThan
    >>> from sympy import And, Ge, Gt, Le, Lt, Rel, S
    >>> from sympy.abc import x, y, z
    >>> from sympy.core.relational import Relational
    >>> e = Ge(x, 1)
    >>> print( e )
    x >= 1
    >>> print "%s >= %s is the same as %s <= %s" % (e.gts, e.lts, e.lts, e.gts)
    x >= 1 is the same as 1 <= x

One generally does not instantiate these classes directly, but uses various
convenience methods:

    >>> e1 = Ge( x, 2 )      # Ge is a convenience wrapper
    >>> print e1
    x >= 2

    >>> Ge( x, 2 )
    x >= 2
    >>> Gt( x, 2 )
    x > 2
    >>> Le( x, 2 )
    x <= 2
    >>> Lt( x, 2 )
    x < 2

Another option is to use the Python inequality operators (>=, >, <=, <)
directly.  Their main advantage over the Ge, Gt, Le, and Lt counterparts, is
that one can write a more "mathematical looking" statement rather than littering
the math with oddball function calls.  However there are certain (minor) caveats
of which to be aware (search for 'gotcha', below).

    >>> e2 = x >= 2
    >>> print e2
    x >= 2
    >>> print "e1: %s,    e2: %s" % (e1, e2)
    e1: x >= 2,    e2: x >= 2
    >>> e1 == e2
    True

However, it is also perfectly valid to instantiate a *Than class less succinctly
and less conviently:

    >>> Rel(x, 1, '>=')
    x >= 1
    >>> Relational(x, 1, '>=')
    x >= 1
    >>> GreaterThan(x, 1)
    x >= 1

    >>> Rel(x, 1, '>')
    x > 1
    >>> Relational(x, 1, '>')
    x > 1
    >>> StrictGreaterThan(x, 1)
    x > 1

    >>> Rel(x, 1, '<=')
    x <= 1
    >>> Relational(x, 1, '<=')
    x <= 1
    >>> LessThan(x, 1)
    x <= 1

    >>> Rel(x, 1, '<')
    x < 1
    >>> Relational(x, 1, '<')
    x < 1
    >>> StrictLessThan(x, 1)
    x < 1


The *Than inequality classes smartly compare equivalent:

    >>> e3 = Le( 2, x )
    >>> print "e2: %s,   e3: %s" % (e2, e3)
    e2: x >= 2,   e3: 2 <= x
    >>> e2 == e3
    True

    >>> print "e: %s,   e3: %s" % (e, e3)
    e: x >= 1,   e3: 2 <= x
    >>> e == e3
    False
    >>> e != e3
    True

SymPy allows nesting of inequalities[1], so to compare whole inequality
expressions, use .compare():

    >>> e4 = Le( x, 4 )
    >>> print "e3: %s,   e4: %s" % (e3, e4)
    e3: 2 <= x,   e4: x <= 4
    >>> print "Nested inequality: %s" % (e3 > e4)
    Nested inequality: (2 <= x) > (x <= 4)

When comparing lhs to rhs (lhs.compare(rhs)), a value of -1 means that lhs is
less than rhs.  A value of 0 means they're equivalent, and a value of 1 means
lhs is greater than rhs.

    >>> print "To compare, use .compare(): %d" % (e3.compare(e4))
    To compare, use .compare(): -1

    >>> e5 = x <= 4
    >>> e4.compare(e5)
    0

There are a couple of "gotchas" when using Python's operators.

The first enters the mix when comparing against a literal number as the lhs
argument.  Due to the order that Python decides to parse a statement, it may not
immediately find two objects comparable.  For example to evaluate the statement
(1 < x), Python will first recognize the number 1 as a native number, and then
that x is *not* a native number.  At this point, because Python numbers have no
__lt__ methods, it will instead call the reflective operation:

x > 1

this is equivalent to x.__gt__( 1 ).  Unfortunately, there is no way available
to SymPy to recognize this has happened, so the statement (1 < x) will turn
silently into (x > 1).  (Note that the position of the literal as an lhs or rhs
is only dependent on the specific implementation of Python.  On another parser,
this could easily turn (x > 1) into (1 < x).  This is another reason to use S()
and the .lts/.gts over .lhs/.rhs, as appropriate.)

    >>> e1 = x >  1
    >>> e2 = x >= 1
    >>> e3 = x <  1
    >>> e4 = x <= 1
    >>> e5 = 1 >  x
    >>> e6 = 1 >= x
    >>> e7 = 1 <  x
    >>> e8 = 1 <= x
    >>> print "%s     %s\\n"*4 % (e1, e2, e3, e4, e5, e6, e7, e8)
    x > 1     x >= 1
    x < 1     x <= 1
    x < 1     x <= 1
    x > 1     x >= 1

If the order of the statement is important (for visual output to the console,
perhaps), one can work around this annoyance in a couple ways: (1) "Sympify" the
literal before comparison, (2) use one of the wrappers, or (3) use the less
succinct methods described above:

    >>> e1 = S(1) >  x
    >>> e2 = S(1) >= x
    >>> e3 = S(1) <  x
    >>> e4 = S(1) <= x
    >>> e5 = Gt(1, x)
    >>> e6 = Ge(1, x)
    >>> e7 = Lt(1, x)
    >>> e8 = Le(1, x)
    >>> print "%s     %s\\n"*4 % (e1, e2, e3, e4, e5, e6, e7, e8)
    1 > x     1 >= x
    1 < x     1 <= x
    1 > x     1 >= x
    1 < x     1 <= x

The other gotcha is with chained inequalities.  Occasionally, one may be tempted
to write statements like:

e = x < y < z  # silent error!
e

Due to an implementation detail or decision of Python[2], there is no way for
SymPy to reliably create that as a chained inequality.  To create a chained
inequality, the only method currently available is to make use of And:

    >>> e = And(x < y, y < z)
    >>> type( e )
    And
    >>> e
    And(x < y, y < z)

Note that this is different than chaining an equality directly via use of
parenthesis (this is currently an open bug in SymPy):

    >>> e = (x < y) < z
    >>> type( e )
    <class 'sympy.core.relational.StrictLessThan'>
    >>> e
    (x < y) < z

Any code that explicitly relies on this latter behavior will not be robust as
this is not correct and will be corrected at some point.  For the time being
(circa Jan 2012), use And to create chained inequalities.

[1] As currently implemented, this is actually a bug.  For more information,
see these two bug reports:

"Separate boolean and symbolic relationals"
http://code.google.com/p/sympy/issues/detail?id=1887

"It right 0 < x < 1 ?"
http://code.google.com/p/sympy/issues/detail?id=2960

[2] This implementation detail is that Python provides no reliable method to
determine that a chained inequality is being built.  For that, SymPy would at
least need Python to allow code to override __and__, which it currently does
not.  See issue 2960, referenced in the previous footnote.

"""

    rel_op = '>='

    __slots__ = ()

    def __hash__ ( self ):   # because __eq__ is overridden as well
        return super(GreaterThan, self).__hash__()

    @classmethod
    def _eval_relation(cls, lhs, rhs):
        return lhs >= rhs

    def __nonzero__(self):
        return self.lhs.compare( self.rhs ) >= 0

    def __eq__ ( self, other ):
        if isinstance(other, GreaterThan):
            ot = other._hashable_content()
        elif isinstance(other, LessThan):
            ot = tuple(reversed( other._hashable_content() ))
        else:
            return False

        st = self._hashable_content()

        return st == ot

class LessThan(_Less):
    __doc__ = GreaterThan.__doc__
    __slots__ = ()

    rel_op = '<='

    def __hash__ ( self ):   # because __eq__ is overridden as well
        return super(LessThan, self).__hash__()

    @classmethod
    def _eval_relation(cls, lhs, rhs):
         return lhs <= rhs

    def __nonzero__(self):
        return self.lhs.compare( self.rhs ) <= 0

    def __eq__ ( self, other ):
        if isinstance(other, LessThan):
            ot = other._hashable_content()
        elif isinstance(other, GreaterThan):
            ot = tuple(reversed( other._hashable_content() ))
        else:
            return False

        st = self._hashable_content()

        return st == ot

class StrictGreaterThan(_Greater):
    __doc__ = GreaterThan.__doc__
    __slots__ = ()

    rel_op = '>'

    def __hash__ ( self ):   # because __eq__ is overridden as well
        return super(StrictGreaterThan, self).__hash__()

    @classmethod
    def _eval_relation(cls, lhs, rhs):
        return lhs > rhs

    def __nonzero__(self):
        return self.lhs.compare( self.rhs ) == 1

    def __eq__ ( self, other ):
        if isinstance(other, StrictGreaterThan):
            ot = other._hashable_content()
        elif isinstance(other, StrictLessThan):
            ot = tuple(reversed( other._hashable_content() ))
        else:
            return False

        st = self._hashable_content()

        return st == ot

class StrictLessThan(_Less):
    __doc__ = GreaterThan.__doc__
    __slots__ = ()

    rel_op = '<'

    def __hash__ ( self ):   # because __eq__ is overridden as well
        return super(StrictLessThan, self).__hash__()

    @classmethod
    def _eval_relation(cls, lhs, rhs):
        return lhs < rhs

    def __nonzero__(self):
        return self.lhs.compare( self.rhs ) == -1

    def __eq__ ( self, other ):
        if isinstance(other, StrictLessThan):
            ot = other._hashable_content()
        elif isinstance(other, StrictGreaterThan):
            ot = tuple(reversed( other._hashable_content() ))
        else:
            return False

        st = self._hashable_content()

        return st == ot

# A class-specific (not object-specific) data item used for a minor speedup.  It
# is defined here, rather than directly in the class, because the classes that
# it references have not been defined until now (e.g. StrictLessThan).
Relational.ValidRelationOperator = {
  None : Equality,
  '==' : Equality,
  'eq' : Equality,
  '!=' : Unequality,
  '<>' : Unequality,
  'ne' : Unequality,
  '>=' : GreaterThan,
  'ge' : GreaterThan,
  '<=' : LessThan,
  'le' : LessThan,
  '>'  : StrictGreaterThan,
  'gt' : StrictGreaterThan,
  '<'  : StrictLessThan,
  'lt' : StrictLessThan,
}
