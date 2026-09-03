"""Minimal in-memory stand-in for the PySpark API surface used by the HR utilities.

Only the pieces exercised by validate_hr_tickets are implemented, with semantics
chosen to match Spark where it matters for this bug:
  * F.col(name) on a column that is not present raises AnalysisException at
    action time (mirrors Spark's [UNRESOLVED_COLUMN] error).
  * distinct() treats NULL (None) as a single distinct value.
"""


class AnalysisException(Exception):
    """Stand-in for pyspark.sql.utils.AnalysisException."""


class _Expr:
    def __init__(self, fn):
        self.fn = fn

    def _lift(self, other):
        return other.fn if isinstance(other, _Expr) else (lambda _row: other)

    def __eq__(self, other):
        other_fn = self._lift(other)
        return _Expr(lambda row: self.fn(row) == other_fn(row))

    def __lt__(self, other):
        other_fn = self._lift(other)

        def _lt(row):
            left, right = self.fn(row), other_fn(row)
            if left is None or right is None:
                return False
            return left < right

        return _Expr(_lt)

    def __and__(self, other):
        other_fn = self._lift(other)
        return _Expr(lambda row: bool(self.fn(row)) and bool(other_fn(row)))

    def __or__(self, other):
        other_fn = self._lift(other)
        return _Expr(lambda row: bool(self.fn(row)) or bool(other_fn(row)))

    def __invert__(self):
        return _Expr(lambda row: not bool(self.fn(row)))

    def isNull(self):
        return _Expr(lambda row: self.fn(row) is None)

    def isNotNull(self):
        return _Expr(lambda row: self.fn(row) is not None)

    def cast(self, _type):
        return _Expr(lambda row: None if self.fn(row) is None else str(self.fn(row)))

    def isin(self, values):
        allowed = list(values)
        return _Expr(lambda row: self.fn(row) in allowed)


class _Functions:
    @staticmethod
    def col(name):
        def _get(row):
            if name not in row:
                raise AnalysisException(
                    f"[UNRESOLVED_COLUMN.WITH_SUGGESTION] A column with name `{name}` "
                    f"cannot be resolved."
                )
            return row[name]

        return _Expr(_get)

    @staticmethod
    def trim(expr):
        return _Expr(lambda row: expr.fn(row).strip() if isinstance(expr.fn(row), str) else expr.fn(row))

    @staticmethod
    def lower(expr):
        return _Expr(lambda row: expr.fn(row).lower() if isinstance(expr.fn(row), str) else expr.fn(row))


functions = _Functions()


class FakeDataFrame:
    def __init__(self, rows, columns):
        self.rows = [dict(row) for row in rows]
        self.columns = list(columns)

    def count(self):
        return len(self.rows)

    def select(self, name):
        return FakeDataFrame([{name: row.get(name)} for row in self.rows], [name])

    def distinct(self):
        seen = set()
        unique_rows = []
        for row in self.rows:
            key = tuple(row.get(column) for column in self.columns)
            if key not in seen:
                seen.add(key)
                unique_rows.append(row)
        return FakeDataFrame(unique_rows, self.columns)

    def filter(self, expr):
        return FakeDataFrame([row for row in self.rows if bool(expr.fn(row))], self.columns)
