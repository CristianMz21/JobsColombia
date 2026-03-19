"""Tests for the utils_proxies module."""

from src.utils_proxies import (
    fetch_and_validate_free_proxies,
    get_working_proxies,
    validate_proxy_sync,
)


class TestFetchAndValidateFreeProxies:
    """Tests for fetch_and_validate_free_proxies function."""

    def test_fetch_and_validate_free_proxies_returns_list(self):
        """Test that fetch_and_validate_free_proxies returns a list."""
        result = fetch_and_validate_free_proxies(max_proxies=1, timeout=2)
        assert isinstance(result, list)

    def test_fetch_and_validate_free_proxies_returns_strings(self):
        """Test that returns list of strings (proxy URLs)."""
        result = fetch_and_validate_free_proxies(max_proxies=1, timeout=2)
        for item in result:
            assert isinstance(item, str)


class TestValidateProxySync:
    """Tests for validate_proxy_sync function."""

    def test_validate_proxy_sync_with_invalid_proxy(self):
        """Test validation of invalid proxy returns False."""
        result = validate_proxy_sync("http://invalid.proxy:8080", timeout=2)
        assert result is False

    def test_validate_proxy_sync_empty_string(self):
        """Test validation of empty string returns False."""
        result = validate_proxy_sync("", timeout=1)
        assert result is False


class TestGetWorkingProxies:
    """Tests for get_working_proxies function."""

    def test_get_working_proxies_returns_list(self):
        """Test that get_working_proxies returns a list."""
        result = get_working_proxies()
        assert isinstance(result, list)

    def test_get_working_proxies_returns_strings(self):
        """Test that get_working_proxies returns list of strings."""
        result = get_working_proxies()
        for item in result:
            assert isinstance(item, str)
