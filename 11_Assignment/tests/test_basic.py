"""Basic tests for ManualAIze application."""

import pytest

from manualaize import __version__


def test_version():
    """Test that the version is defined."""
    assert __version__ == "0.1.0"


def test_import_manualaize():
    """Test that the manualaize package can be imported."""
    import manualaize

    assert manualaize is not None


def test_openai_import():
    """Test that OpenAI can be imported."""
    try:
        import openai

        assert openai is not None
    except ImportError:
        pytest.fail("OpenAI package not available")


def test_pandas_import():
    """Test that pandas can be imported."""
    try:
        import pandas as pd

        assert pd is not None
    except ImportError:
        pytest.fail("Pandas package not available")


def test_numpy_import():
    """Test that numpy can be imported."""
    try:
        import numpy as np

        assert np is not None
    except ImportError:
        pytest.fail("NumPy package not available")
