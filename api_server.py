#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quotex Pro Trader — LIVE DATA CORE WITH STREAM PRINTING
✅ Exact Dictionary Format Printing (Matches Your Screenshot)
✅ 100% Headless Cloud Compatible (Render Ready)
✅ Updated Real-Time Connection Pipelines
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

# SSL Layer Configuration
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
cert_path = certifi.where()
os.environ['SSL_CERT_FILE'] = cert_path
os.environ['WEBSOCKET_CLIENT_CA_BUNDLE'] = cert_path

# Render Env Flag Check
IS_RENDER = os.environ.get('RENDER') is not None or os.environ.get('PORT') is not None

if not IS_RENDER:
    try: import eel
    except ImportError: eel = None
else:
    eel = None
    print("☁️ [SYSTEM] Render Environment Detected. Activating Silent Backend Worker...")

try:
    from pyquotex.stable_api import Quotex
    from pyquotex.utils.processor import process_candles
except ImportError as e:
    print(f"\n❌ Dependency Error: {e}")
    sys.exit(1)

CONSOLE_LEVEL = 1

def log(msg: str, level: int = 1):
    if level <= CONSOLE_LEVEL:
        print(msg)

# Threading Loops Setup
ASYNC_LOOP = asyncio.new_event_loop()
def start_async_loop():
    asyncio.set_event_loop(ASYNC_LOOP)
    ASYNC_LOOP.run_forever()

threading.Thread(target=start_async_loop, daemon=True, name="AsyncCore").start()

# =====================================================================
# 📊 ALL SUPPORTED PAIRS DIRECTORY
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
TIMEFRAMES = {"1m": 60, "5m": 300, "15m": 900, "1h": 3600}

CLIENT: Optional[Quotex] = None
CURRENT_ASSET = "AUD/CAD (OTC)"
CURRENT_TIMEFRAME = "1m"
CURRENT_CANDLE: Dict[str, Dict[str, dict]] = {}
SERVER_TIME_OFFSET = 0
REALTIME_RUNNING = False

def configure_backend_tunnel():
    """রেন্ডার ক্লাউড প্রক্সি টানেলিং অ্যাডাপ্টার"""
    if os.environ.get('PROXY_URL'):
        os.environ['HTTPS_PROXY'] = os.environ.get('PROXY_URL', '')
        os.environ['HTTP_PROXY'] = os.environ.get('PROXY_URL', '')

def update_and_print_candle(asset: str, frame: str, price: float, ts_sec: int):
    """
    ক্যান্ডেল ডাটা আপডেট করে এবং স্ক্রিনশটের মতো ডিকশনারি ফরম্যাটে 
    কনসোল টার্মিনালে বা রেন্ডার লগে প্রিন্ট করে।
    """
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
    
    # 🎯 তোমার স্ক্রিনশটের মতো এক্সাক্ট ফরম্যাটে প্রতি টিক-এ ডাটা প্রিন্ট হবে
    if frame == CURRENT_TIMEFRAME:
        print(f"📊 Live Stream [{asset}]: {CURRENT_CANDLE[asset][frame]}")

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
                        update_and_print_candle(asset_display, frame, price, ts_sec)
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
                print(f"🔑 [CONNECTING] Authenticating Node Session (Attempt {attempt}/5)...")
                check, reason = await CLIENT.connect()
                if check:
                    await CLIENT.change_account("PRACTICE")
                    print("✅ [SUCCESS] Cloud Engine Core Connected to Quotex Official API!")
                    return True, ""
            except Exception as e:
                print(f"⚠️ [RETRYING] Handshake processing hold: {e}")
            await asyncio.sleep(3)
        return False, "Handshake Tunnel Reset Timeout"
    except Exception as e:
        return False, str(e)

def run_cloud_worker():
    email = os.environ.get("QUOTEX_EMAIL", "qtrader874@gmail.com")
    password = os.environ.get("QUOTEX_PASSWORD", "@quotextrader123")
    
    future = asyncio.run_coroutine_threadsafe(connect_to_quotex(email, password), ASYNC_LOOP)
    success, reason = future.result()
    if success:
        internal = DISPLAY_TO_INTERNAL.get(CURRENT_ASSET)
        asyncio.run_coroutine_threadsafe(CLIENT.start_realtime_price(internal, 60), ASYNC_LOOP)
        asyncio.run_coroutine_threadsafe(realtime_price_loop(CURRENT_ASSET), ASYNC_LOOP)
        while True:
            time.sleep(1)
    else:
        print(f"❌ Deploy Failed: {reason}")

if __name__ == '__main__':
    if IS_RENDER:
        run_cloud_worker()
    else:
        print("💻 Running Local Machine Worker...")
        # Local পিসিতে টেস্ট করার জন্য ডাইরেক্ট ওয়ার্কার ট্রিগার
        run_cloud_worker()
