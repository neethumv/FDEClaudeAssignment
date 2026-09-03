"""Test bootstrap: register the fake PySpark modules and expose HRAnalyticsPOC on sys.path."""

import os
import sys
import types

TESTS_DIR = os.path.dirname(__file__)
POC_DIR = os.path.dirname(TESTS_DIR)
if POC_DIR not in sys.path:
    sys.path.insert(0, POC_DIR)

import fake_spark  # noqa: E402

_pyspark = types.ModuleType("pyspark")
_pyspark_sql = types.ModuleType("pyspark.sql")
_pyspark_sql.functions = fake_spark.functions
_pyspark.sql = _pyspark_sql

sys.modules.setdefault("pyspark", _pyspark)
sys.modules.setdefault("pyspark.sql", _pyspark_sql)
sys.modules.setdefault("pyspark.sql.functions", fake_spark.functions)
