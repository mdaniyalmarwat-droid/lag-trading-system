import ccxt
import pandas as pd
import numpy as np

# ----------------------------------
# SETUP EXCHANGE
# ----------------------------------

exchange = ccxt.binance()

def get_timestamp(date_str):
    return exchange.parse8601(date_str.replace(" ", "T") + ":00Z")

def fetch_data(symbol, timeframe, start, end):
    since = get_timestamp(start)
    end_ts = get_timestamp(end)

    all_candles = []

    while since < end_ts:
        candles = exchange.fetch_ohlcv(symbol, timeframe, since=since, limit=1000)
        if not candles:
            break
        all_candles.extend(candles)
        since = candles[-1][0] + 1

    df = pd.DataFrame(all_candles, columns=["ts","open","high","low","close","volume"])
    df = df[df["ts"] <= end_ts]
    df["return"] = df["close"].pct_change()
    return df


# ==================================
# STEP 1 — BTC MOVE
# ==================================

print("\n=== BTC MOVE ANALYSIS ===")

btc_timeframe = input("Enter BTC timeframe (5m / 15m / 1h): ")
btc_start = input("Enter BTC start time (YYYY-MM-DD HH:MM): ")
btc_end = input("Enter BTC end time (YYYY-MM-DD HH:MM): ")

btc = fetch_data("BTC/USDT", btc_timeframe, btc_start, btc_end)

btc_return = (btc["close"].iloc[-1] - btc["close"].iloc[0]) / btc["close"].iloc[0]

if btc_return > 0.01:
    btc_message = "BTC made a STRONG bullish impulse."
elif btc_return < -0.01:
    btc_message = "BTC made a STRONG bearish impulse."
else:
    btc_message = "BTC move is weak. No strong impulse detected."

print("\nResult:")
print(btc_message)


# ==================================
# STEP 2 — ALT ANALYSIS
# ==================================

print("\n=== ALT COIN ANALYSIS ===")

alt_symbol = input("Enter ALT symbol (example: ETH/USDT): ")
alt_timeframe = input("Enter ALT timeframe (must match BTC): ")
alt_start = input("Enter ALT start time (same as BTC): ")
alt_end = input("Enter ALT end time (same as BTC): ")

alt = fetch_data(alt_symbol, alt_timeframe, alt_start, alt_end)

alt_return = (alt["close"].iloc[-1] - alt["close"].iloc[0]) / alt["close"].iloc[0]
alt_vol = alt["return"].std()

S = (alt_return - btc_return) / alt_vol

# ----------------------------------
# CLASSIFICATION
# ----------------------------------

if btc_return > 0:
    direction = "bullish"
else:
    direction = "bearish"

if S < -1:
    decision = "High probability catch-up trade."
elif -1 <= S < -0.5:
    decision = "Moderate lag. Possible trade."
elif -0.5 <= S <= 0.5:
    decision = "No clear edge. Skip."
elif 0.5 < S <= 1:
    decision = "Already moved. Weak setup."
else:
    decision = "Overextended. Avoid."

# ----------------------------------
# FINAL OUTPUT
# ----------------------------------

print("\n----------------------------------")
print(f"BTC direction: {direction}")
print(f"{alt_symbol} analyzed.")
print(decision)
print("----------------------------------")
