#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quotex Pro Trader — 3000 CANDLE HISTORICAL DATA STREAMER (ALL PAIRS FIXED)
✅ 100% Fixed and Complete Assets Categories Map
✅ Fetch & Print 3000 Historical Candles Array (Matches Your JSON Screenshot)
✅ Seamless Transition to Real-Time Live Candle Updates
✅ 100% Headless Cloud Compatible (Render/Worker Ready)
"""
import asyncio
import threading
import time
import json
import os
import sys
import certifi
import urllib3
from pathlib import Path
from queue import Queue
from typing import Optional, Dict, List, Tuple

# SSL Layer & Bypass Configuration
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
cert_path = certifi.where()
os.environ['SSL_CERT_FILE'] = cert_path
os.environ['WEBSOCKET_CLIENT_CA_BUNDLE'] = cert_path

# Cloud Environment Check (Headless Node Detection)
IS_RENDER = os.environ.get('RENDER') is not None or os.environ.get('PORT') is not None

try:
    from pyquotex.stable_api import Quotex
    from pyquotex.utils.processor import process_candles
except ImportError as e:
    print(f"\n❌ Dependency Error: {e}")
    sys.exit(1)

# Core Async Loop Engine
ASYNC_LOOP = asyncio.new_event_loop()
def start_async_loop():
    asyncio.set_event_loop(ASYNC_LOOP)
    ASYNC_LOOP.run_forever()

threading.Thread(target=start_async_loop, daemon=True, name="AsyncCore").start()

# =====================================================================
# 📊 ALL SUPPORTED PAIRS DIRECTORY (FIXED & FULLY MAPPED)
# =====================================================================
ASSET_DISPLAY_MAP = {
    # 🌍 Forex & OTC Pairs
    "AUDCAD": "AUD/CAD", "AUDCAD_otc": "AUD/CAD (OTC)", "AUDCHF": "AUD/CHF", "AUDCHF_otc": "AUD/CHF (OTC)",
    "AUDJPY": "AUD/JPY", "AUDJPY_otc": "AUD/JPY (OTC)", "AUDNZD_otc": "AUD/NZD (OTC)", "AUDUSD": "AUD/USD",
    "AUDUSD_otc": "AUD/USD (OTC)", "CADJPY": "CAD/JPY", "CADJPY_otc": "CAD/JPY (OTC)", "CADCHF_otc": "CAD/CHF (OTC)",
    "CHFJPY": "CHF/JPY", "CHFJPY_otc": "CHF/JPY (OTC)", "EURAUD": "EUR/AUD", "EURAUD_otc": "EUR/AUD (OTC)",
    "EURCAD": "EUR/CAD", "EURCAD_otc": "EUR/CAD (OTC)", "EURCHF": "EUR/CHF", "EURCHF_otc": "EUR/CHF (OTC)",
    "EURGBP": "EUR/GBP", "EURGBP_otc": "EUR/GBP (OTC)", "EURJPY": "EUR/JPY", "EURJPY_otc": "EUR/JPY (OTC)",
    "EURNZD_otc": "EUR/NZD (OTC)", "EURSGD_otc": "EUR/SGD (OTC)", "EURUSD": "EUR/USD", "EURUSD_otc": "EUR/USD (OTC)",
    "GBPAUD": "GBP/AUD", "GBPAUD_otc": "GBP/AUD (OTC)", "GBPCAD": "GBP/CAD", "GBPCAD_otc": "GBP/CAD (OTC)",
    "GBPCHF": "GBP/CHF", "GBPCHF_otc": "GBP/CHF (OTC)", "GBPJPY": "GBP/JPY", "GBPJPY_otc": "GBP/JPY (OTC)",
    "GBPNZD_otc": "GBP/NZD (OTC)", "GBPUSD": "GBP/USD", "GBPUSD_otc": "GBP/USD (OTC)", "NZDCAD_otc": "NZD/CAD (OTC)",
    "NZDCHF_otc": "NZD/CHF (OTC)", "NZDJPY_otc": "NZD/JPY (OTC)", "NZDUSD_otc": "NZD/USD (OTC)", "USDCAD": "USD/CAD",
    "USDCAD_otc": "USD/CAD (OTC)", "USDCHF": "USD/CHF", "USDCHF_otc": "USD/CHF (OTC)", "USDJPY": "USD/JPY",
    "USDJPY_otc": "USD/JPY (OTC)", "USDARS_otc": "USD/ARS (OTC)", "USDBDT_otc": "USD/BDT (OTC)", "USDCOP_otc": "USD/COP (OTC)",
    "USDDZD_otc": "USD/DZD (OTC)", "USDEGP_otc": "USD/EGP (OTC)", "USDIDR_otc": "USD/IDR (OTC)", "USDINR_otc": "USD/INR (OTC)",
    "USDMXN_otc": "USD/MXN (OTC)", "USDNGN_otc": "USD/NGN (OTC)", "USDPHP_otc": "USD/PHP (OTC)", "USDPKR_otc": "USD/PKR (OTC)",
    "USDTRY_otc": "USD/TRY (OTC)", "USDZAR_otc": "USD/ZAR (OTC)",

    # 🪙 Crypto Pairs
    "ADAUSD_otc": "Cardano (OTC)", "APTUSD_otc": "Aptos (OTC)", "ARBUSD_otc": "Arbitrum (OTC)", "ATOUSD_otc": "ATO (OTC)",
    "AVAUSD_otc": "Avalanche (OTC)", "AXSUSD_otc": "Axie Infinity (OTC)", "BCHUSD_otc": "Bitcoin Cash (OTC)",
    "BNBUSD_otc": "Binance Coin (OTC)", "BONUSD_otc": "Bonk (OTC)", "BTCUSD_otc": "Bitcoin (OTC)", "DASUSD_otc": "Dash (OTC)",
    "DOGUSD_otc": "Dogecoin (OTC)", "DOTUSD_otc": "Polkadot (OTC)", "ETCUSD_otc": "Ethereum Classic (OTC)",
    "ETHUSD_otc": "Ethereum (OTC)", "FLOUSD_otc": "Floki (OTC)", "GALUSD_otc": "Gala (OTC)", "HMSUSD_otc": "Hamster Kombat (OTC)",
    "LINUSD_otc": "Chainlink (OTC)", "LTCUSD_otc": "Litecoin (OTC)", "MELUSD_otc": "Melania Meme (OTC)",
    "SHIBUSD_otc": "Shiba Inu (OTC)", "SOLUSD_otc": "Solana (OTC)", "TIAUSD_otc": "Celestia (OTC)", "TONUSD_otc": "Toncoin (OTC)",
    "TRUUSD_otc": "TrueFi (OTC)", "TRXUSD_otc": "TRON (OTC)", "WIFUSD_otc": "Dogwifhat (OTC)", "XRPUSD_otc": "Ripple (OTC)",
    "ZECUSD_otc": "Zcash (OTC)",

    # 🪵 Commodities Pairs
    "XAUUSD": "Gold", "XAUUSD_otc": "Gold (OTC)", "XAGUSD": "Silver", "XAGUSD_otc": "Silver (OTC)",
    "UKBrent_otc": "UK Brent (OTC)", "USCrude_otc": "US Crude (OTC)",

    # 📈 Stocks Pairs
    "AXP_otc": "American Express (OTC)", "BA_otc": "Boeing Company (OTC)", "FB_otc": "Facebook (OTC)",
    "INTC_otc": "Intel (OTC)", "JNJ_otc": "Johnson & Johnson (OTC)", "MCD_otc": "McDonald's (OTC)",
    "MSFT_otc": "Microsoft (OTC)", "PFE_otc": "Pfizer Inc (OTC)", "PEPUSD_otc": "PepsiCo (OTC)",

    # 📊 Indices Pairs
    "DJIUSD": "Dow Jones", "NDXUSD": "NASDAQ 100", "F40EUR": "CAC 40", "FTSGBP": "FTSE 100",
    "HSIHKD": "Hong Kong 50", "IBXEUR": "IBEX 35", "JPXJPY": "Nikkei 225", "CHIA50": "China A50",
    "STXEUR": "EURO STOXX 50"
}

DISPLAY_TO_INTERNAL = {v: k for k, v in ASSET_DISPLAY_MAP.items()}

# UI ক্যাটাগরি ম্যাপিং জেনারেটর (১০০% নিখুঁত ফিক্সড মেথড)
ASSET_CATEGORIES = {
    "🌍 Forex & OTC": [
        "AUD/CAD", "AUD/CAD (OTC)", "AUD/CHF", "AUD/CHF (OTC)", "AUD/JPY", "AUD/JPY (OTC)", "AUD/NZD (OTC)", 
        "AUD/USD", "AUD/USD (OTC)", "CAD/JPY", "CAD/JPY (OTC)", "CAD/CHF (OTC)", "CHF/JPY", "CHF/JPY (OTC)", 
        "EUR/AUD", "EUR/AUD (OTC)", "EUR/CAD", "EUR/CAD (OTC)", "EUR/CHF", "EUR/CHF (OTC)", "EUR/GBP", 
        "EUR/GBP (OTC)", "EUR/JPY", "EUR/JPY (OTC)", "EUR/NZD (OTC)", "EUR/SGD (OTC)", "EUR/USD", 
        "EUR/USD (OTC)", "GBP/AUD", "GBP/AUD (OTC)", "GBP/CAD", "GBP/CAD (OTC)", "GBP/CHF", "GBP/CHF (OTC)", 
        "GBP/JPY", "GBP/JPY (OTC)", "GBP/NZD (OTC)", "GBP/USD", "GBP/USD (OTC)", "NZD/CAD (OTC)", 
        "NZD/CHF (OTC)", "NZD/JPY (OTC)", "NZD/USD (OTC)", "USD/CAD", "USD/CAD (OTC)", "USD/CHF", 
        "USD/CHF (OTC)", "USD/JPY", "USD/JPY (OTC)", "USD/ARS (OTC)", "USD/BDT (OTC)", "USD/COP (OTC)", 
        "USD/DZD (OTC)", "USD/EGP (OTC)", "USD/IDR (OTC)", "USD/INR (OTC)", "USD/MXN (OTC)", "USD/NGN (OTC)", 
        "USD/PHP (OTC)", "USD/PKR (OTC)", "USD/TRY (OTC)", "USD/ZAR (OTC)"
    ],
    "🪙 Crypto Pairs": [
        "Cardano (OTC)", "Aptos (OTC)", "Arbitrum (OTC)", "ATO (OTC)", "Avalanche (OTC)", "Axie Infinity (OTC)", 
        "Bitcoin Cash (OTC)", "Binance Coin (OTC)", "Bonk (OTC)", "Bitcoin (OTC)", "Dash (OTC)", "Dogecoin (OTC)", 
        "Polkadot (OTC)", "Ethereum Classic (OTC)", "Ethereum (OTC)", "Floki (OTC)", "Gala (OTC)", "Hamster Kombat (OTC)", 
        "Chainlink (OTC)", "Litecoin (OTC)", "Melania Meme (OTC)", "Shiba Inu (OTC)", "Solana (OTC)", "Celestia (OTC)", 
        "Toncoin (OTC)", "TrueFi (OTC)", "TRON (OTC)", "Dogwifhat (OTC)", "Ripple (OTC)", "Zcash (OTC)"
    ],
    "🪵 Commodities": ["Gold", "Gold (OTC)", "Silver", "Silver (OTC)", "UK Brent (OTC)", "US Crude (OTC)"],
    "📈 Stocks Pairs": [
        "American Express (OTC)", "Boeing Company (OTC)", "Facebook (OTC)", "Intel (OTC)", "Johnson & Johnson (OTC)", 
        "McDonald's (OTC)", "Microsoft (OTC)", "Pfizer Inc (OTC)", "PepsiCo (OTC)"
    ],
    "📊 Indices Pairs": [
        "Dow Jones", "NASDAQ 100", "CAC 40", "FTSE 100", "Hong Kong 50", "IBEX 35", "Nikkei 225", "China A50", "EURO STOXX 50"
    ]
}

TIMEFRAMES = {
    "5s": 5, "10s": 10, "15s": 15, "30s": 30, "1m": 60, "2m": 120, "3m": 180, "5m": 300, "15m": 900, "1h": 3600
}

CLIENT: Optional[Quotex] = None
CURRENT_ASSET = "AUD/CAD (OTC)"  # এখান থেকে ডিফোল্ট এসেট চেঞ্জ করতে পারো
CURRENT_TIMEFRAME = "1m"
CANDLES: Dict[str, Dict[str, List[dict]]] = {}
CURRENT_CANDLE: Dict[str, Dict[str, dict]] = {}
SERVER_TIME_OFFSET = 0
REALTIME_RUNNING = False

def configure_backend_tunnel():
    """রেন্ডার ক্লাউড প্রক্সি টানেলিং অ্যাডাপ্টার"""
    if os.environ.get('PROXY_URL'):
        os.environ['HTTPS_PROXY'] = os.environ.get('PROXY_URL', '')
        os.environ['HTTP_PROXY'] = os.environ.get('PROXY_URL', '')

def process_candle_data(raw_candles: List[dict], period: int) -> List[dict]:
    if not raw_candles: return []
    if raw_candles and not raw_candles[0].get("open"):
        try: return process_candles(raw_candles, period)
        except Exception: return []
    formatted = []
    for c in raw_candles:
        try:
            candle_time = int(float(c["time"]))
            aligned_time = (candle_time // period) * period
            formatted.append({
                "time": aligned_time, "open": float(c["open"]), "high": float(c["high"]),
                "low": float(c["low"]), "close": float(c["close"])
            })
        except Exception: continue
    formatted.sort(key=lambda x: x["time"])
    return formatted

# =====================================================================
# ⚡ 3000 CANDLES HISTORICAL LOADING ENGINE
# =====================================================================
async def load_3000_candles(asset_display: str, tf_name: str) -> List[dict]:
    """সরাসরি ব্রোকার API থেকে ৩০০০ হিস্টোরিক্যাল ক্যান্ডেল লোড করে জেসন এরে বানায়"""
    global CANDLES
    if not CLIENT or not CLIENT.api: return []
    internal = DISPLAY_TO_INTERNAL.get(asset_display, "AUDCAD_otc")
    period_sec = TIMEFRAMES.get(tf_name, 60)
    
    try:
        print(f"\n📥 Requesting 3000 Historical Candles Data for {asset_display}...")
        hist_data = await CLIENT.get_candles(
            asset=internal, 
            end_from_time=time.time(), 
            offset=3000 * period_sec, 
            period=period_sec
        )
        loaded = process_candle_data(hist_data, period_sec)
        
        if asset_display not in CANDLES: CANDLES[asset_display] = {}
        CANDLES[asset_display][tf_name] = loaded[-3000:]
        
        # জেসন ফরম্যাট আউটপুট প্রিন্ট
        print(f"\n📦 [HISTORICAL DATA ARRAY - {len(CANDLES[asset_display][tf_name])} CANDLES Loaded]:")
        print(json.dumps(CANDLES[asset_display][tf_name], indent=2))
        return CANDLES[asset_display][tf_name]
    except Exception as e:
        print(f"❌ Failed to parse historical array: {e}")
        return []

def update_and_stream_candle(asset: str, frame: str, price: float, ts_sec: int):
    global CURRENT_CANDLE
    duration = TIMEFRAMES.get(frame, 60)
    candle_start = (ts_sec // duration) * duration
    
    if asset not in CURRENT_CANDLE: CURRENT_CANDLE[asset] = {}
    curr = CURRENT_CANDLE[asset].get(frame, {})
    
    if not curr or curr.get("time") != candle_start:
        CURRENT_CANDLE[asset][frame] = {
            "time": int(candle_start), "open": float(price), "high": float(price),
            "low": float(price), "close": float(price)
        }
    else:
        if price > curr["high"]: curr["high"] = float(price)
        if price < curr["low"]: curr["low"] = float(price)
        curr["close"] = float(price)
    
    if frame == CURRENT_TIMEFRAME:
        print(f"⚡ [LIVE TICK] {asset} -> {CURRENT_CANDLE[asset][frame]}", end="\r")

async def realtime_price_loop(asset_display: str):
    global REALTIME_RUNNING, SERVER_TIME_OFFSET
    internal = DISPLAY_TO_INTERNAL.get(asset_display)
    if not internal or not CLIENT: return
    REALTIME_RUNNING = True
    while REALTIME_RUNNING:
        try:
            data = await CLIENT.get_realtime_price(internal)
            if data and len(data) > 0:
                latest = data[-1]
                price = float(latest.get("price", latest.get("close", 0)))
                timestamp = latest.get("time", time.time())
                if price > 0 and timestamp > 0:
                    ts_sec = int(float(timestamp))
                    SERVER_TIME_OFFSET = timestamp - time.time()
                    for frame in TIMEFRAMES:
                        update_and_stream_candle(asset_display, frame, price, ts_sec)
            await asyncio.sleep(0.1)
        except Exception:
            await asyncio.sleep(1)

async def connect_to_quotex(email: str, password: str) -> Tuple[bool, str]:
    global CLIENT
    configure_backend_tunnel()
    try:
        config_dir = Path.home() / ".pyquotex"
        config_dir.mkdir(parents=True, exist_ok=True)
        with open(config_dir / "credentials.json", 'w') as f:
            json.dump({"email": email, "password": password}, f)
            
        CLIENT = Quotex(email=email, password=password, host="qxbroker.com", lang="en")
        
        for attempt in range(1, 6):
            try:
                print(f"🔑 [CLOUD AUTH] Handshaking Safe Proxy Tunnel ({attempt}/5)...")
                check, reason = await CLIENT.connect()
                if check:
                    await CLIENT.change_account("PRACTICE")
                    print("✅ [CONNECTED] Authentication Token Synced with API Server.")
                    return True, ""
            except Exception as e:
                print(f"⚠️ [HOLD] Re-mapping websocket layer: {e}")
            await asyncio.sleep(3)
        return False, "Handshake Timeout"
    except Exception as e:
        return False, str(e)

def run_cloud_worker():
    # ডিফোল্ট লগইন প্র্যাকটিস অ্যাকাউন্ট ক্রেডেনশিয়ালস
    email = os.environ.get("QUOTEX_EMAIL", "qtrader874@gmail.com")
    password = os.environ.get("QUOTEX_PASSWORD", "@quotextrader123")
    
    future = asyncio.run_coroutine_threadsafe(connect_to_quotex(email, password), ASYNC_LOOP)
    success, reason = future.result()
    if success:
        # ১. প্রথমে ৩০০০ হিস্টোরিক্যাল ডাটা ব্লক তুলে প্রিন্ট করবে
        hist_future = asyncio.run_coroutine_threadsafe(load_3000_candles(CURRENT_ASSET, CURRENT_TIMEFRAME), ASYNC_LOOP)
        hist_future.result()
        
        # ২. হিস্টোরিক্যাল ডাটা শেষ হলে সাথে সাথে লাইভ টিক স্ট্রিমিং লুপে চলে যাবে
        internal = DISPLAY_TO_INTERNAL.get(CURRENT_ASSET)
        asyncio.run_coroutine_threadsafe(CLIENT.start_realtime_price(internal, 60), ASYNC_LOOP)
        asyncio.run_coroutine_threadsafe(realtime_price_loop(CURRENT_ASSET), ASYNC_LOOP)
        
        while True:
            time.sleep(1)
    else:
        print(f"❌ Deploy Failed: {reason}")

if __name__ == '__main__':
    run_cloud_worker()
