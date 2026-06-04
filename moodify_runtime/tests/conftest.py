"""Pytest configuration for moodify_runtime tests."""


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: tests that run real audio DSP processing (5-60s each)")
