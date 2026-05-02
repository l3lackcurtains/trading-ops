#!/usr/bin/env python3
"""
fetch_ohlc.py — local OHLCV + indicator pre-compute via Yahoo Finance.

Generic data layer: pulls multi-timeframe OHLCV, computes a configurable EMA
cluster, ATR, RSI, VWAP family (session / weekly / monthly / quarterly /
anchored, with 1σ + 2σ bands), and a Volume Profile (POC, VAH, VAL,
HVN / LVN). Output is markdown by default, JSON optional.

The VWAP and Volume Profile reads are the operational backbone of the
framework's technical-read step. See `docs/vwap.md` and
`docs/volume-profile.md` for methodology.

Usage:
    fetch_ohlc.py <TICKER> [--timeframes W,D,4H,1H] [--emas 20,50,200]
                          [--bars 400] [--anchor YYYY-MM-DD]
                          [--vp-bins 24] [--vp-value-area 0.70]
                          [--no-vwap] [--no-vp]
                          [--out <path>] [--json]
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
import yfinance as yf


YF_INTERVAL_MAP = {
    "M": "1mo",
    "W": "1wk",
    "D": "1d",
    "4H": "60m",  # yfinance has no native 4H — caller can resample if needed
    "1H": "60m",
    "30m": "30m",
    "15m": "15m",
    "5m": "5m",
}

INTRADAY_INTERVALS = {"60m", "30m", "15m", "5m"}

DEFAULT_TIMEFRAMES = ["W", "D", "4H", "1H"]
DEFAULT_EMAS = [20, 50, 200]
DEFAULT_BARS = 400
DEFAULT_VP_BINS = 24
DEFAULT_VP_VALUE_AREA = 0.70


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class BarSummary:
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    range_pct: float
    body_pct: float
    upper_wick_pct: float
    lower_wick_pct: float
    direction: str  # "up" / "down" / "doji"


@dataclass
class VWAPReport:
    """VWAP family on a single timeframe.

    Variants computed depend on the timeframe:
      - intraday (60m/30m/15m/5m): session, weekly, monthly, quarterly, anchored
      - daily / weekly / monthly: weekly, monthly, quarterly, anchored
    """
    session: float | None = None  # latest session VWAP (intraday only)
    weekly: float | None = None
    monthly: float | None = None
    quarterly: float | None = None
    anchored: float | None = None
    anchor_date: str | None = None
    band_1sigma_upper: float | None = None
    band_1sigma_lower: float | None = None
    band_2sigma_upper: float | None = None
    band_2sigma_lower: float | None = None
    dist_pct: float | None = None  # close vs primary VWAP, %
    primary: str | None = None  # which variant is "primary" for this TF
    slope: str | None = None  # "rising" / "flat" / "falling"


@dataclass
class VolumeProfileReport:
    bins: int
    value_area_pct: float
    period_bars: int
    period_low: float
    period_high: float
    poc: float | None = None
    vah: float | None = None  # Value Area High
    val: float | None = None  # Value Area Low
    total_volume: float = 0.0
    current_position: str | None = None  # "above VAH" / "in value" / "below VAL"
    hvn: list[float] = field(default_factory=list)  # top high-volume nodes
    lvn: list[float] = field(default_factory=list)  # top low-volume gaps
    histogram_ascii: str | None = None  # small visual


@dataclass
class TimeframeReport:
    timeframe: str
    yf_interval: str
    bars_returned: int
    last_bar: BarSummary | None
    emas: dict[int, float]
    atr14: float | None
    rsi14: float | None
    vol_avg20: float | None
    vol_ratio: float | None  # last bar volume / 20-period avg
    vwap: VWAPReport | None = None
    volume_profile: VolumeProfileReport | None = None


# ---------------------------------------------------------------------------
# Data fetch
# ---------------------------------------------------------------------------


def fetch_ohlcv(ticker: str, interval: str, bars: int) -> pd.DataFrame:
    period = _period_for(interval, bars)
    df = yf.download(
        ticker,
        period=period,
        interval=interval,
        auto_adjust=False,
        progress=False,
        threads=False,
    )
    if df.empty:
        return df
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0] for c in df.columns]
    df = df.tail(bars)
    return df


def _period_for(interval: str, bars: int) -> str:
    if interval in ("1mo",):
        return "max"
    if interval in ("1wk",):
        return "max"
    if interval in ("1d",):
        return "5y" if bars <= 1250 else "max"
    if interval in ("60m", "30m", "15m"):
        return "730d"
    if interval in ("5m",):
        return "60d"
    return "max"


# ---------------------------------------------------------------------------
# Indicator helpers
# ---------------------------------------------------------------------------


def _typical_price(df: pd.DataFrame) -> pd.Series:
    return (df["High"] + df["Low"] + df["Close"]) / 3.0


def compute_emas(df: pd.DataFrame, lengths: Iterable[int]) -> dict[int, float]:
    out: dict[int, float] = {}
    if df.empty:
        return out
    close = df["Close"]
    for n in lengths:
        if len(close) < n:
            continue
        out[n] = float(close.ewm(span=n, adjust=False).mean().iloc[-1])
    return out


def compute_atr(df: pd.DataFrame, period: int = 14) -> float | None:
    if len(df) < period + 1:
        return None
    high = df["High"]
    low = df["Low"]
    close_prev = df["Close"].shift(1)
    tr = pd.concat(
        [(high - low), (high - close_prev).abs(), (low - close_prev).abs()],
        axis=1,
    ).max(axis=1)
    return float(tr.rolling(period).mean().iloc[-1])


def compute_rsi(df: pd.DataFrame, period: int = 14) -> float | None:
    if len(df) < period + 1:
        return None
    close = df["Close"]
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss.replace(0, pd.NA)
    rsi = 100 - (100 / (1 + rs))
    val = rsi.iloc[-1]
    return None if pd.isna(val) else float(val)


# ---------------------------------------------------------------------------
# VWAP
# ---------------------------------------------------------------------------


def _vwap_series(tp: pd.Series, vol: pd.Series) -> pd.Series:
    """Cumulative VWAP over a (sub-)series. Caller pre-slices/groups."""
    pv = tp * vol
    cum_pv = pv.cumsum()
    cum_v = vol.cumsum().replace(0, np.nan)
    return cum_pv / cum_v


def _vwap_with_bands(tp: pd.Series, vol: pd.Series) -> tuple[pd.Series, pd.Series]:
    """Returns (vwap, sigma) — sigma is volume-weighted std of (tp - vwap)."""
    vwap = _vwap_series(tp, vol)
    diff_sq = (tp - vwap) ** 2
    cum_v = vol.cumsum().replace(0, np.nan)
    var = (diff_sq * vol).cumsum() / cum_v
    sigma = np.sqrt(var)
    return vwap, sigma


def _grouped_vwap(df: pd.DataFrame, freq: str) -> pd.Series:
    """VWAP that resets at each freq boundary (e.g. 'W', 'M', 'Q', 'D')."""
    tp = _typical_price(df)
    vol = df["Volume"].astype(float)
    grouper = df.index.to_period(freq)
    parts: list[pd.Series] = []
    for _, idx in pd.Series(grouper).groupby(grouper).groups.items():
        sub_tp = tp.iloc[idx]
        sub_vol = vol.iloc[idx]
        parts.append(_vwap_series(sub_tp, sub_vol))
    if not parts:
        return pd.Series(dtype=float, index=df.index)
    return pd.concat(parts).sort_index()


def _slope(series: pd.Series, lookback: int = 5) -> str:
    s = series.dropna()
    if len(s) < lookback + 1:
        return "flat"
    recent = s.iloc[-1]
    prior = s.iloc[-lookback - 1]
    if prior == 0 or pd.isna(prior):
        return "flat"
    pct = (recent - prior) / abs(prior) * 100
    if pct > 0.10:
        return "rising"
    if pct < -0.10:
        return "falling"
    return "flat"


def compute_vwap_report(
    df: pd.DataFrame,
    interval: str,
    anchor: str | None,
) -> VWAPReport | None:
    if df.empty or "Volume" not in df.columns:
        return None
    if df["Volume"].sum() <= 0:
        return None

    tp = _typical_price(df)
    vol = df["Volume"].astype(float)
    close = float(df["Close"].iloc[-1])
    report = VWAPReport()

    # Session VWAP (intraday only — resets each calendar day)
    if interval in INTRADAY_INTERVALS:
        try:
            grouper = df.index.normalize() if hasattr(df.index, "normalize") else df.index
            today = grouper[-1]
            mask = grouper == today
            sess_tp = tp[mask]
            sess_vol = vol[mask]
            sess_vwap, sess_sigma = _vwap_with_bands(sess_tp, sess_vol)
            if len(sess_vwap) and not pd.isna(sess_vwap.iloc[-1]):
                report.session = float(sess_vwap.iloc[-1])
                if not pd.isna(sess_sigma.iloc[-1]):
                    s1 = float(sess_sigma.iloc[-1])
                    report.band_1sigma_upper = report.session + s1
                    report.band_1sigma_lower = report.session - s1
                    report.band_2sigma_upper = report.session + 2 * s1
                    report.band_2sigma_lower = report.session - 2 * s1
                report.slope = _slope(sess_vwap)
                report.primary = "session"
                report.dist_pct = round(
                    (close - report.session) / report.session * 100, 2
                )
        except (AttributeError, TypeError, IndexError):
            pass

    # Weekly / Monthly / Quarterly resets — applies to all timeframes that span
    # multiple weeks/months
    try:
        wk = _grouped_vwap(df, "W")
        if len(wk) and not pd.isna(wk.iloc[-1]):
            report.weekly = float(wk.iloc[-1])
    except Exception:
        pass
    try:
        mo = _grouped_vwap(df, "M")
        if len(mo) and not pd.isna(mo.iloc[-1]):
            report.monthly = float(mo.iloc[-1])
    except Exception:
        pass
    try:
        qt = _grouped_vwap(df, "Q")
        if len(qt) and not pd.isna(qt.iloc[-1]):
            report.quarterly = float(qt.iloc[-1])
    except Exception:
        pass

    # Anchored VWAP
    if anchor:
        try:
            anchor_ts = pd.Timestamp(anchor)
            if df.index.tz is not None and anchor_ts.tz is None:
                anchor_ts = anchor_ts.tz_localize(df.index.tz)
            sub = df.loc[df.index >= anchor_ts]
            if not sub.empty:
                a_tp = _typical_price(sub)
                a_vol = sub["Volume"].astype(float)
                a_vwap, a_sigma = _vwap_with_bands(a_tp, a_vol)
                if len(a_vwap) and not pd.isna(a_vwap.iloc[-1]):
                    report.anchored = float(a_vwap.iloc[-1])
                    report.anchor_date = anchor
                    # If no session bands set, use anchored bands
                    if report.band_1sigma_upper is None and not pd.isna(a_sigma.iloc[-1]):
                        s1 = float(a_sigma.iloc[-1])
                        report.band_1sigma_upper = report.anchored + s1
                        report.band_1sigma_lower = report.anchored - s1
                        report.band_2sigma_upper = report.anchored + 2 * s1
                        report.band_2sigma_lower = report.anchored - 2 * s1
                    if report.primary is None:
                        report.primary = "anchored"
                        report.slope = _slope(a_vwap)
                        report.dist_pct = round(
                            (close - report.anchored) / report.anchored * 100, 2
                        )
        except Exception:
            pass

    # Pick primary if not yet set — prefer monthly for D, quarterly for W/M
    if report.primary is None:
        if interval == "1d" and report.monthly is not None:
            report.primary = "monthly"
            report.dist_pct = round(
                (close - report.monthly) / report.monthly * 100, 2
            )
            try:
                report.slope = _slope(_grouped_vwap(df, "M"))
            except Exception:
                pass
        elif interval in ("1wk", "1mo") and report.quarterly is not None:
            report.primary = "quarterly"
            report.dist_pct = round(
                (close - report.quarterly) / report.quarterly * 100, 2
            )
            try:
                report.slope = _slope(_grouped_vwap(df, "Q"))
            except Exception:
                pass
        elif report.weekly is not None:
            report.primary = "weekly"
            report.dist_pct = round(
                (close - report.weekly) / report.weekly * 100, 2
            )

    return report


# ---------------------------------------------------------------------------
# Volume Profile
# ---------------------------------------------------------------------------


def compute_volume_profile(
    df: pd.DataFrame,
    bins: int = DEFAULT_VP_BINS,
    value_area: float = DEFAULT_VP_VALUE_AREA,
) -> VolumeProfileReport | None:
    if df.empty or "Volume" not in df.columns or df["Volume"].sum() <= 0:
        return None

    period_low = float(df["Low"].min())
    period_high = float(df["High"].max())
    if period_high <= period_low:
        return None

    edges = np.linspace(period_low, period_high, bins + 1)
    centers = (edges[:-1] + edges[1:]) / 2

    # Distribute each bar's volume across the bins it spans, weighted by the
    # fraction of the bar's range overlapping each bin. This is more accurate
    # than assigning all volume to the typical price bin.
    hist = np.zeros(bins, dtype=float)
    lows = df["Low"].to_numpy()
    highs = df["High"].to_numpy()
    vols = df["Volume"].astype(float).to_numpy()

    for lo, hi, v in zip(lows, highs, vols):
        if v <= 0 or hi <= lo:
            # zero volume or zero range — assign to nearest bin
            mid = (lo + hi) / 2
            idx = int(np.clip(np.searchsorted(edges, mid) - 1, 0, bins - 1))
            hist[idx] += v
            continue
        # Find overlapping bins
        first = int(np.clip(np.searchsorted(edges, lo, side="right") - 1, 0, bins - 1))
        last = int(np.clip(np.searchsorted(edges, hi, side="left") - 1, 0, bins - 1))
        for i in range(first, last + 1):
            bin_lo = edges[i]
            bin_hi = edges[i + 1]
            overlap = max(0.0, min(hi, bin_hi) - max(lo, bin_lo))
            if (hi - lo) > 0:
                hist[i] += v * (overlap / (hi - lo))

    total_vol = float(hist.sum())
    if total_vol <= 0:
        return None

    poc_idx = int(np.argmax(hist))
    poc = float(centers[poc_idx])

    # Value Area: expand from POC, picking the larger neighbor each step,
    # until accumulated volume >= value_area * total
    target = value_area * total_vol
    accum = float(hist[poc_idx])
    lo_idx = poc_idx
    hi_idx = poc_idx
    while accum < target and (lo_idx > 0 or hi_idx < bins - 1):
        next_lo = hist[lo_idx - 1] if lo_idx > 0 else -1
        next_hi = hist[hi_idx + 1] if hi_idx < bins - 1 else -1
        if next_lo >= next_hi:
            lo_idx -= 1
            accum += float(hist[lo_idx])
        else:
            hi_idx += 1
            accum += float(hist[hi_idx])

    val = float(edges[lo_idx])
    vah = float(edges[hi_idx + 1])
    close = float(df["Close"].iloc[-1])
    if close > vah:
        position = "above VAH"
    elif close < val:
        position = "below VAL"
    else:
        position = "in value"

    # HVN / LVN — local maxima and minima excluding POC itself
    hvn_levels: list[float] = []
    lvn_levels: list[float] = []
    for i in range(1, bins - 1):
        if i == poc_idx:
            continue
        if hist[i] > hist[i - 1] and hist[i] > hist[i + 1] and hist[i] > total_vol / bins * 1.3:
            hvn_levels.append(float(centers[i]))
        if hist[i] < hist[i - 1] and hist[i] < hist[i + 1] and hist[i] < total_vol / bins * 0.4:
            lvn_levels.append(float(centers[i]))
    # Top 3 HVN by volume, top 3 LVN by inverse-volume gap
    hvn_levels = sorted(hvn_levels, key=lambda p: -hist[int(np.searchsorted(edges, p) - 1)])[:3]
    lvn_levels = sorted(lvn_levels, key=lambda p: hist[int(np.searchsorted(edges, p) - 1)])[:3]

    # ASCII histogram (small)
    max_h = float(hist.max()) or 1.0
    width = 24
    rows = []
    for i in reversed(range(bins)):
        bar_len = int(round(hist[i] / max_h * width))
        marker = "  "
        if i == poc_idx:
            marker = ">>"
        elif i == lo_idx:
            marker = "L "
        elif i == hi_idx:
            marker = "H "
        rows.append(f"{centers[i]:>10.4g} {marker}|{'#' * bar_len}")
    histogram_ascii = "\n".join(rows)

    return VolumeProfileReport(
        bins=bins,
        value_area_pct=value_area,
        period_bars=len(df),
        period_low=period_low,
        period_high=period_high,
        poc=poc,
        vah=vah,
        val=val,
        total_volume=total_vol,
        current_position=position,
        hvn=hvn_levels,
        lvn=lvn_levels,
        histogram_ascii=histogram_ascii,
    )


# ---------------------------------------------------------------------------
# Bar summary
# ---------------------------------------------------------------------------


def summarize_last_bar(df: pd.DataFrame) -> BarSummary | None:
    if df.empty:
        return None
    last = df.iloc[-1]
    o = float(last["Open"])
    h = float(last["High"])
    l = float(last["Low"])
    c = float(last["Close"])
    v = float(last.get("Volume", 0) or 0)
    rng = h - l
    body = abs(c - o)
    upper = h - max(o, c)
    lower = min(o, c) - l
    rng_pct = (rng / o * 100) if o else 0.0
    direction = "up" if c > o else "down" if c < o else "doji"
    return BarSummary(
        timestamp=str(last.name),
        open=o, high=h, low=l, close=c, volume=v,
        range_pct=round(rng_pct, 2),
        body_pct=round((body / rng * 100) if rng else 0, 1),
        upper_wick_pct=round((upper / rng * 100) if rng else 0, 1),
        lower_wick_pct=round((lower / rng * 100) if rng else 0, 1),
        direction=direction,
    )


# ---------------------------------------------------------------------------
# Per-timeframe report
# ---------------------------------------------------------------------------


def build_report(
    ticker: str,
    tf: str,
    emas: list[int],
    bars: int,
    anchor: str | None,
    vp_bins: int,
    vp_value_area: float,
    do_vwap: bool,
    do_vp: bool,
) -> TimeframeReport:
    interval = YF_INTERVAL_MAP[tf]
    df = fetch_ohlcv(ticker, interval, bars)
    last = summarize_last_bar(df)
    vol_avg20 = float(df["Volume"].rolling(20).mean().iloc[-1]) if len(df) >= 20 else None
    vol_ratio = (last.volume / vol_avg20) if (last and vol_avg20) else None

    vwap = compute_vwap_report(df, interval, anchor) if do_vwap else None
    vp = compute_volume_profile(df, vp_bins, vp_value_area) if do_vp else None

    return TimeframeReport(
        timeframe=tf,
        yf_interval=interval,
        bars_returned=len(df),
        last_bar=last,
        emas=compute_emas(df, emas),
        atr14=compute_atr(df, 14),
        rsi14=compute_rsi(df, 14),
        vol_avg20=vol_avg20,
        vol_ratio=round(vol_ratio, 2) if vol_ratio else None,
        vwap=vwap,
        volume_profile=vp,
    )


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------


def _format_vwap(v: VWAPReport) -> list[str]:
    parts = []
    if v.session is not None:
        parts.append(f"session {v.session:.4g}")
    if v.weekly is not None:
        parts.append(f"weekly {v.weekly:.4g}")
    if v.monthly is not None:
        parts.append(f"monthly {v.monthly:.4g}")
    if v.quarterly is not None:
        parts.append(f"quarterly {v.quarterly:.4g}")
    if v.anchored is not None:
        parts.append(f"anchored({v.anchor_date}) {v.anchored:.4g}")
    lines = []
    if parts:
        lines.append(f"- **VWAP**: {' · '.join(parts)}")
    if v.band_1sigma_upper is not None:
        lines.append(
            f"  - bands: 1σ [{v.band_1sigma_lower:.4g} – {v.band_1sigma_upper:.4g}] · "
            f"2σ [{v.band_2sigma_lower:.4g} – {v.band_2sigma_upper:.4g}]"
        )
    if v.primary and v.dist_pct is not None:
        slope = f", {v.slope}" if v.slope else ""
        sign = "+" if v.dist_pct >= 0 else ""
        lines.append(
            f"  - close vs {v.primary} VWAP: {sign}{v.dist_pct}%{slope}"
        )
    return lines


def _format_vp(vp: VolumeProfileReport) -> list[str]:
    lines = [
        f"- **Volume Profile** ({vp.bins} bins · {vp.value_area_pct*100:.0f}% VA · "
        f"{vp.period_bars} bars · range {vp.period_low:.4g} – {vp.period_high:.4g}):"
    ]
    if vp.poc is not None:
        lines.append(
            f"  - POC {vp.poc:.4g} · VAH {vp.vah:.4g} · VAL {vp.val:.4g} · "
            f"position: **{vp.current_position}**"
        )
    if vp.hvn:
        lines.append(f"  - HVN: {' · '.join(f'{p:.4g}' for p in vp.hvn)}")
    if vp.lvn:
        lines.append(f"  - LVN: {' · '.join(f'{p:.4g}' for p in vp.lvn)}")
    return lines


def render_markdown(ticker: str, reports: list[TimeframeReport], show_vp_ascii: bool) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines: list[str] = [f"# {ticker} — OHLC + indicators ({now})", ""]
    for r in reports:
        lines.append(f"## {r.timeframe}  ({r.yf_interval} — {r.bars_returned} bars)")
        lines.append("")
        if r.last_bar:
            b = r.last_bar
            lines.append(
                f"- **Last bar** [{b.timestamp}]: O {b.open:.4g} · H {b.high:.4g} · "
                f"L {b.low:.4g} · C {b.close:.4g} · V {b.volume:,.0f}"
            )
            lines.append(
                f"- **Character**: {b.direction} · range {b.range_pct}% · "
                f"body {b.body_pct}% · upper-wick {b.upper_wick_pct}% · "
                f"lower-wick {b.lower_wick_pct}%"
            )
        if r.emas:
            ema_str = " · ".join(f"EMA{n} {v:.4g}" for n, v in sorted(r.emas.items()))
            lines.append(f"- **EMAs**: {ema_str}")
        ind_parts = []
        if r.atr14 is not None:
            ind_parts.append(f"ATR(14) {r.atr14:.4g}")
        if r.rsi14 is not None:
            ind_parts.append(f"RSI(14) {r.rsi14:.1f}")
        if r.vol_ratio is not None:
            ind_parts.append(f"vol×20avg {r.vol_ratio}×")
        if ind_parts:
            lines.append(f"- **Indicators**: {' · '.join(ind_parts)}")
        if r.vwap is not None:
            lines.extend(_format_vwap(r.vwap))
        if r.volume_profile is not None:
            lines.extend(_format_vp(r.volume_profile))
            if show_vp_ascii and r.volume_profile.histogram_ascii:
                lines.append("")
                lines.append("```text")
                lines.append(r.volume_profile.histogram_ascii)
                lines.append("```")
        lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("ticker")
    p.add_argument("--timeframes", default=",".join(DEFAULT_TIMEFRAMES),
                   help=f"Comma-separated, e.g. W,D,4H,1H (default: {','.join(DEFAULT_TIMEFRAMES)})")
    p.add_argument("--emas", default=",".join(str(n) for n in DEFAULT_EMAS),
                   help=f"Comma-separated EMA lengths (default: {','.join(str(n) for n in DEFAULT_EMAS)})")
    p.add_argument("--bars", type=int, default=DEFAULT_BARS,
                   help=f"Bars to fetch per timeframe (default: {DEFAULT_BARS})")
    p.add_argument("--anchor", default=None,
                   help="Anchored VWAP from this date (YYYY-MM-DD)")
    p.add_argument("--vp-bins", type=int, default=DEFAULT_VP_BINS,
                   help=f"Volume Profile bins (default: {DEFAULT_VP_BINS})")
    p.add_argument("--vp-value-area", type=float, default=DEFAULT_VP_VALUE_AREA,
                   help=f"Value Area fraction (default: {DEFAULT_VP_VALUE_AREA})")
    p.add_argument("--no-vwap", action="store_true", help="Skip VWAP computation")
    p.add_argument("--no-vp", action="store_true", help="Skip Volume Profile computation")
    p.add_argument("--vp-ascii", action="store_true",
                   help="Include ASCII histogram of the Volume Profile")
    p.add_argument("--out", help="Optional output markdown path")
    p.add_argument("--json", action="store_true", help="Emit JSON instead of markdown")
    args = p.parse_args(argv)

    ticker = args.ticker.upper()
    timeframes = [tf.strip() for tf in args.timeframes.split(",") if tf.strip()]
    emas = [int(n) for n in args.emas.split(",") if n.strip()]

    unknown = [tf for tf in timeframes if tf not in YF_INTERVAL_MAP]
    if unknown:
        print(f"Unknown timeframe(s): {unknown}. Allowed: {list(YF_INTERVAL_MAP)}",
              file=sys.stderr)
        return 2

    reports = [
        build_report(
            ticker, tf, emas, args.bars,
            args.anchor, args.vp_bins, args.vp_value_area,
            do_vwap=not args.no_vwap, do_vp=not args.no_vp,
        )
        for tf in timeframes
    ]

    if args.json:
        out = {"ticker": ticker, "reports": [asdict(r) for r in reports]}
        print(json.dumps(out, indent=2, default=str))
        return 0

    md = render_markdown(ticker, reports, show_vp_ascii=args.vp_ascii)
    if args.out:
        Path(args.out).write_text(md)
    else:
        print(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
