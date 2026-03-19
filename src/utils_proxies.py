"""
Proxy utilities for TechJobs_Scraper_Colombia.

This module provides functions to fetch and validate free proxies,
rotating through them to avoid rate limiting and IP bans.

Features:
- Fetch proxies from multiple free proxy sources
- Async validation with timeout
- Proxy rotation support
"""

import re

import requests

from src.logger import logger

PROXY_TEST_URL = "https://httpbin.org/ip"
VALIDATION_TIMEOUT = 5


def fetch_free_proxy_list() -> list[dict[str, str]]:
    """Fetch free proxies from free-proxy-list.net.

    Returns:
        List of dictionaries with proxy details (ip, port, protocol).
    """
    proxies: list[dict[str, str]] = []

    try:
        response = requests.get(
            "https://free-proxy-list.net/",
            timeout=15,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
        )
        response.raise_for_status()

        html = response.text

        table_match = re.search(r"<tbody>(.*?)</tbody>", html, re.DOTALL | re.IGNORECASE)
        if not table_match:
            return proxies

        table_content = table_match.group(1)

        row_pattern = re.compile(
            r"<tr><td>([^<]+)</td><td>([^<]+)</td><td>([^<]*)</td><td>([^<]*)</td><td>([^<]*)</td><td>([^<]*)</td><td>([^<]*)</td></tr>",
            re.DOTALL,
        )

        for match in row_pattern.finditer(table_content):
            ip = match.group(1).strip()
            port = match.group(2).strip()
            http_type = match.group(3).strip().lower()
            https = match.group(4).strip().lower()

            protocol = "https" if http_type == "yes" or https == "yes" else "http"

            proxies.append(
                {
                    "ip": ip,
                    "port": port,
                    "protocol": protocol,
                    "url": f"{protocol}://{ip}:{port}",
                }
            )

    except Exception as e:
        logger.error(f"Error fetching free proxy list: {e}")

    return proxies


def fetch_proxies_from_api() -> list[dict[str, str]]:
    """Fetch proxies from proxy API services.

    Returns:
        List of dictionaries with proxy details.
    """
    proxies: list[dict[str, str]] = []

    apis = [
        "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=5000&country=CO",
        "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=5000",
    ]

    for api_url in apis:
        try:
            response = requests.get(api_url, timeout=15)
            response.raise_for_status()

            for line in response.text.strip().split("\n"):
                line = line.strip()
                if ":" in line:
                    parts = line.split(":")
                    if len(parts) >= 2:
                        proxies.append(
                            {
                                "ip": parts[0],
                                "port": parts[1],
                                "protocol": "http",
                                "url": f"http://{line}",
                            }
                        )

        except Exception as e:
            logger.error(f"Error fetching from API {api_url}: {e}")

    return proxies


def validate_proxy_sync(proxy_url: str, timeout: int = VALIDATION_TIMEOUT) -> bool:
    """Validate a proxy synchronously.

    Args:
        proxy_url: Full proxy URL (e.g., 'http://ip:port').
        timeout: Timeout in seconds for the request.

    Returns:
        True if proxy works, False otherwise.
    """
    try:
        session = requests.Session()
        session.proxies = {"http": proxy_url, "https": proxy_url}
        session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "*/*",
            }
        )

        response = session.get(PROXY_TEST_URL, timeout=timeout)

        if response.status_code == 200:
            return True

    except Exception:
        pass

    return False


def fetch_and_validate_free_proxies(
    max_proxies: int = 10,
    timeout: int = VALIDATION_TIMEOUT,
) -> list[str]:
    """Fetch and validate free proxies.

    This function scrapes free proxy lists, then validates each proxy
    by attempting to connect to a test URL. Only working proxies are returned.

    Args:
        max_proxies: Maximum number of working proxies to return.
        timeout: Timeout in seconds for validation requests.

    Returns:
        List of validated proxy URLs.

    Example:
        >>> proxies = fetch_and_validate_free_proxies(max_proxies=5)
        >>> print(f"Found {len(proxies)} working proxies")
    """
    logger.info("Fetching free proxies...")

    all_proxies: list[dict[str, str]] = []

    all_proxies.extend(fetch_free_proxy_list())
    all_proxies.extend(fetch_proxies_from_api())

    unique_urls = list({p["url"] for p in all_proxies})

    logger.info(f"Found {len(unique_urls)} unique proxies to validate...")

    validated: list[str] = []

    for proxy_url in unique_urls[:50]:
        if len(validated) >= max_proxies:
            break

        if validate_proxy_sync(proxy_url, timeout):
            logger.debug(f"Working proxy: {proxy_url}")
            validated.append(proxy_url)
        else:
            logger.debug(f"Failed proxy: {proxy_url}")

    logger.info(f"Validation complete: {len(validated)}/{len(unique_urls[:50])} proxies working")

    return validated


def get_working_proxies() -> list[str]:
    """Get a list of working free proxies.

    Returns:
        List of validated proxy URLs, or empty list if none work.
    """
    return fetch_and_validate_free_proxies(max_proxies=10, timeout=VALIDATION_TIMEOUT)
