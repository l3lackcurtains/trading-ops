"""
_yfdata.py — Yahoo Finance data adapter backed by yahooquery.

Merges yahooquery's 5 quote endpoints into a single `info` dict, transposes
its statement DataFrames into rows=line-items / cols=dates-desc shape, and
normalizes history bars to capitalized columns.

API:
    from _yfdata import Ticker
    t = Ticker("CRCL")
    t.info                    # merged dict
    t.history(period, interval, auto_adjust=False)  # OHLCV DataFrame
    t.quarterly_income_stmt   # rows=line items, cols=dates desc
    t.income_stmt             # annual
    t.balance_sheet           # annual
    t.news                    # list[dict] or [] on failure
"""

import math
from datetime import datetime


def _safe_payload(yq, attr, symbol):
    """Pull a yahooquery dict-of-dicts endpoint and return the per-symbol payload,
    or {} if missing / errored. yahooquery returns {symbol: <error string>} when an
    endpoint fails — guard against that."""
    try:
        data = getattr(yq, attr)
    except Exception:
        return {}
    if not isinstance(data, dict):
        return {}
    payload = data.get(symbol)
    if not isinstance(payload, dict):
        return {}
    return payload


class Ticker:
    """Yahoo data adapter — single Ticker entry point for quote / history / statements / news."""

    def __init__(self, symbol):
        from yahooquery import Ticker as _YQ
        self.symbol = symbol.upper()
        self._yq = _YQ(self.symbol, asynchronous=False)
        self._info_cache = None

    # ---------- info dict ----------

    @property
    def info(self):
        if self._info_cache is not None:
            return self._info_cache

        merged = {"symbol": self.symbol}

        # Merge endpoints in priority order — later writes don't overwrite truthy values
        # from earlier endpoints unless explicitly aliased below.
        for endpoint in (
            "price",            # marketCap, regularMarketPrice, longName, exchange
            "summary_detail",   # forwardPE, priceToSalesTrailing12Months, fiftyTwoWeekHigh/Low, averageVolume, dividendYield, payoutRatio, fiftyDayAverage, twoHundredDayAverage
            "financial_data",   # currentPrice, grossMargins, operatingMargins, profitMargins, returnOnEquity, returnOnAssets, revenueGrowth, earningsGrowth, debtToEquity, currentRatio, quickRatio, totalCash, totalDebt, freeCashflow, ebitda, recommendationMean, targetMeanPrice, numberOfAnalystOpinions
            "key_stats",        # pegRatio, priceToBook, bookValue, sharesOutstanding, floatShares, enterpriseValue, heldPercentInsiders, heldPercentInstitutions, sharesShort, shortRatio, shortPercentOfFloat, dateShortInterest, earningsQuarterlyGrowth, trailingEps, forwardEps
            "summary_profile",  # sector, industry, longBusinessSummary
        ):
            payload = _safe_payload(self._yq, endpoint, self.symbol)
            for k, v in payload.items():
                # don't overwrite an already-truthy value with a falsy duplicate
                if merged.get(k) in (None, "", 0) or k not in merged:
                    merged[k] = v

        # ---- yfinance-friendly aliases ----
        # currentPrice (yfinance staple) — fall back chain
        if not merged.get("currentPrice"):
            merged["currentPrice"] = (
                merged.get("regularMarketPrice")
                or merged.get("ask")
                or merged.get("previousClose")
            )

        # next earnings date — yfinance exposes via info["nextEarningsDate"];
        # yahooquery surfaces it via calendar_events.earnings.earningsDate (list)
        ce = _safe_payload(self._yq, "calendar_events", self.symbol)
        if isinstance(ce.get("earnings"), dict):
            dates = ce["earnings"].get("earningsDate") or []
            if dates:
                # format like "2026-05-11 08:30:S" — keep raw string; caller parses what it needs
                merged["nextEarningsDate"] = dates[0]
                # also record the BMO/AMC suffix if present
                tail = dates[0].rsplit(":", 1)[-1] if ":" in dates[0] else ""
                if tail in ("S", "BMO"):
                    merged["nextEarningsTiming"] = "BMO"
                elif tail in ("A", "AMC"):
                    merged["nextEarningsTiming"] = "AMC"

        self._info_cache = merged
        return merged

    # ---------- price history ----------

    def history(self, period="1y", interval="1d", auto_adjust=False):
        import pandas as pd
        try:
            df = self._yq.history(period=period, interval=interval, adj_ohlc=auto_adjust)
        except Exception:
            return pd.DataFrame()
        if df is None or not hasattr(df, "shape") or df.empty:
            return pd.DataFrame()

        # yahooquery returns multi-index (symbol, date) — drop the symbol level
        if hasattr(df.index, "names") and "symbol" in (df.index.names or []):
            df = df.droplevel("symbol")

        # Normalize column names to yfinance shape
        df = df.rename(columns={
            "open": "Open",
            "high": "High",
            "low": "Low",
            "close": "Close",
            "volume": "Volume",
            "adjclose": "Adj Close",
        })

        # Ensure DatetimeIndex
        if not isinstance(df.index, pd.DatetimeIndex):
            try:
                df.index = pd.to_datetime(df.index)
            except Exception:
                pass

        return df

    # ---------- financial statements ----------

    @property
    def quarterly_income_stmt(self):
        return self._statement_to_yf("income_statement", "q")

    @property
    def income_stmt(self):
        return self._statement_to_yf("income_statement", "a")

    @property
    def balance_sheet(self):
        return self._statement_to_yf("balance_sheet", "a")

    @property
    def quarterly_balance_sheet(self):
        return self._statement_to_yf("balance_sheet", "q")

    def _statement_to_yf(self, method_name, frequency):
        """Reshape yahooquery's wide statement DataFrame (rows=periods,
        cols=line items) into yfinance's tall shape (rows=line items,
        cols=periods desc)."""
        import pandas as pd
        try:
            method = getattr(self._yq, method_name)
            df = method(frequency=frequency)
        except Exception:
            return pd.DataFrame()
        if df is None or not hasattr(df, "shape") or df.empty:
            return pd.DataFrame()
        if not hasattr(df, "columns") or "asOfDate" not in df.columns:
            return pd.DataFrame()

        try:
            # yahooquery returns a single-level Index named 'symbol' OR a
            # MultiIndex with 'symbol' as one level. Reset cleanly to a plain
            # range index so we can pivot purely off `asOfDate`.
            if hasattr(df.index, "names") and "symbol" in (df.index.names or []):
                df = df.reset_index(drop=True)

            # yahooquery returns a `periodType` column even when `frequency=`
            # is specified — quarterly calls return `3M` AND `TTM` rows, annual
            # calls return `12M` AND `TTM` rows. Filter to the requested cadence
            # so we don't accidentally treat a TTM aggregate as a quarter (or
            # an annual) value. `frequency='q'` -> keep `3M`; `'a'` -> keep `12M`.
            if "periodType" in df.columns:
                want = "3M" if frequency == "q" else "12M"
                df = df[df["periodType"] == want]
                df = df.drop(columns=["periodType"])

            # Drop other helper / non-numeric columns before pivoting
            drop_cols = [c for c in ("currencyCode",) if c in df.columns]
            if drop_cols:
                df = df.drop(columns=drop_cols)

            if "asOfDate" not in df.columns or df.empty:
                return pd.DataFrame()

            # If duplicate `asOfDate` rows still remain (e.g., a restated period),
            # keep the row with the most non-null fields.
            if df["asOfDate"].duplicated().any():
                df = df.assign(_nn=df.drop(columns=["asOfDate"]).notna().sum(axis=1))
                df = df.sort_values("_nn", ascending=False)
                df = df.drop_duplicates(subset=["asOfDate"], keep="first")
                df = df.drop(columns=["_nn"])

            df = df.set_index("asOfDate")
            df = df.dropna(how="all")

            # yfinance convention: most-recent period first
            df = df.sort_index(ascending=False)

            # Transpose: rows = line items, columns = periods (yfinance shape)
            return df.T
        except Exception:
            return pd.DataFrame()

    # ---------- news ----------

    @property
    def news(self):
        """yahooquery's news endpoint is unreliable (often returns ['error']);
        return [] when malformed so callers don't crash. Format is best-effort."""
        try:
            attr = getattr(self._yq, "news", None)
            raw = attr() if callable(attr) else attr
        except Exception:
            return []
        if not isinstance(raw, list):
            return []
        out = []
        for item in raw:
            if not isinstance(item, dict):
                continue
            out.append(item)
        return out
