"""
execution/delta_client.py
Signed HTTP client for the Delta Exchange REST API.
Handles authentication, retries, and error reporting.
"""

import hashlib
import hmac
import json
import logging
import time
from typing import Any

import requests

from config.settings import (
    DELTA_API_KEY,
    DELTA_API_SECRET,
    DELTA_BASE_URL,
    MAX_RETRIES,
    RETRY_DELAY_SECONDS,
)

logger = logging.getLogger(__name__)


class DeltaClient:
    """
    REST client for Delta Exchange.
    
    Handles:
    - HMAC-SHA256 request signing
    - Automatic retries with backoff
    - Structured error logging
    """

    def __init__(self) -> None:
        self.base_url = DELTA_BASE_URL.rstrip("/")
        self.api_key = DELTA_API_KEY
        self.api_secret = DELTA_API_SECRET
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    # ── Signing ───────────────────────────────────────────────────────────────

    def _sign(self, method: str, path: str, body: str, timestamp: str) -> str:
        """Generate HMAC-SHA256 signature per Delta Exchange spec."""
        message = method.upper() + timestamp + path + body
        return hmac.new(
            self.api_secret.encode("utf-8"),
            message.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def _auth_headers(self, method: str, path: str, body: str = "") -> dict:
        timestamp = str(int(time.time()))
        signature = self._sign(method, path, body, timestamp)
        return {
            "api-key": self.api_key,
            "timestamp": timestamp,
            "signature": signature,
        }

    # ── Request Helper ────────────────────────────────────────────────────────

    def _request(
        self,
        method: str,
        endpoint: str,
        params: dict | None = None,
        data: dict | None = None,
    ) -> dict[str, Any]:
        path = endpoint if endpoint.startswith("/") else f"/{endpoint}"
        url = self.base_url + path
        body_str = json.dumps(data) if data else ""
        headers = self._auth_headers(method, path, body_str)

        last_exc: Exception | None = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                resp = self.session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    data=body_str if body_str else None,
                    timeout=15,
                )
                resp.raise_for_status()
                result = resp.json()
                logger.debug(f"{method} {path} → {resp.status_code}")
                return result
            except requests.exceptions.RequestException as exc:
                last_exc = exc
                logger.warning(
                    f"Attempt {attempt}/{MAX_RETRIES} – {method} {path} failed: {exc}"
                )
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_DELAY_SECONDS * attempt)

        raise RuntimeError(f"API call {method} {path} failed: {last_exc}") from last_exc

    # ── Public API ────────────────────────────────────────────────────────────

    def get_products(self) -> list[dict]:
        """List all available products/markets."""
        result = self._request("GET", "/v2/products")
        return result.get("result", [])

    def get_wallet_balance(self) -> dict:
        """Fetch account wallet balances."""
        result = self._request("GET", "/v2/wallet/balances")
        return result.get("result", {})

    def get_position(self, product_id: int) -> dict | None:
        """
        Fetch open position for a product.
        Returns position dict or None if no open position.
        """
        result = self._request("GET", "/v2/positions", params={"product_id": product_id})
        positions = result.get("result", [])
        if not positions:
            return None
        for pos in positions:
            if pos.get("product_id") == product_id:
                size = float(pos.get("size", 0))
                if size != 0:
                    return pos
        return None

    def place_order(
        self,
        product_id: int,
        side: str,
        order_type: str,
        size: float,
        limit_price: float | None = None,
        reduce_only: bool = False,
        stop_loss: float | None = None,
        take_profit: float | None = None,
    ) -> dict:
        """
        Place an order on Delta Exchange.

        Args:
            product_id:  Delta product ID
            side:        'buy' or 'sell'
            order_type:  'limit_order' or 'market_order'
            size:        Number of contracts
            limit_price: Required for limit orders
            reduce_only: Close-only flag
            stop_loss:   Optional bracket SL price
            take_profit: Optional bracket TP price
        """
        payload: dict[str, Any] = {
            "product_id": product_id,
            "side": side,
            "order_type": order_type,
            "size": size,
            "reduce_only": reduce_only,
        }
        if limit_price is not None:
            payload["limit_price"] = str(limit_price)
        if stop_loss is not None:
            payload["bracket_stop_loss_price"] = str(stop_loss)
            payload["bracket_stop_loss_limit_price"] = str(stop_loss)
        if take_profit is not None:
            payload["bracket_take_profit_price"] = str(take_profit)
            payload["bracket_take_profit_limit_price"] = str(take_profit)

        logger.info(f"Placing order: {payload}")
        result = self._request("POST", "/v2/orders", data=payload)
        logger.info(f"Order result: {result}")
        return result

    def close_position(self, product_id: int, size: float, side: str) -> dict:
        """
        Close an existing position by placing a reduce-only market order.
        `side` should be opposite to the open position direction.
        """
        logger.info(f"Closing position for product_id={product_id} size={size} side={side}")
        return self.place_order(
            product_id=product_id,
            side=side,
            order_type="market_order",
            size=size,
            reduce_only=True,
        )

    def get_product_id(self, symbol: str) -> int | None:
        """Resolve symbol (e.g. 'BTCUSD') to Delta product_id."""
        products = self.get_products()
        for p in products:
            if p.get("symbol") == symbol:
                return p["id"]
        logger.warning(f"Product not found for symbol: {symbol}")
        return None
