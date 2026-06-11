#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quotex Pro Trader — CLEAN CONSOLE VERSION
✅ 100% Real Live PyQuotex Data Integration
🔒 Async-Safe Global VPN/Proxy Engine (No Loop Crashes)
❌ NO Random or Mock Data Fallbacks
"""
import asyncio
import threading
import time
import json
import os
import sys
import eel
import certifi
from pathlib import Path
from queue import Queue
from typing import Optional, Dict, List, Tuple

# =====================================================================
# 🌐 VPN / PROXY CONFIGURATION (Quotex Bypass System)
# =====================================================================
USE_VPN_PROXY = True
PROXY_TYPE = "socks5"      # অপশন: "socks5" অথবা "http"
PROXY_IP = "127.0.0.1"     # তোমার লোকাল VPN/Proxy আইপি
PROXY_PORT = "1080"        # তোমার VPN/Proxy ক্লায়েন্টের পোর্ট (যেমন: 1080, 2080, 7890, 8080)

if USE_VPN_PROXY:
    # asyncio-safe ট্রাফিকের জন্য এনভায়রনমেন্ট ভ্যারিয়েবল সেটআপ
    proxy_url = f"{PROXY_TYPE}://{PROXY_IP}:{PROXY_PORT}"
    
    os.environ['HTTP_PROXY'] = proxy_url
    os.environ['HTTPS_PROXY'] = proxy_url
    os.environ['ALL_PROXY'] = proxy_url
    os.environ['http_proxy'] = proxy_url
    os.environ['https_proxy'] = proxy_url
    os.environ['all_proxy'] = proxy_url
    
    # SSL ভেরিফিকেশন প্রক্সির মধ্য দিয়ে পাস করানোর জন্য সেটিংস
    os.environ['CURL_CA_BUNDLE'] = certifi.where()
    print(f"🔒 Async-Safe VPN/Proxy Tunnel Configured: {proxy_url}")

# ✅ SSL Setup (Official CA Bundle setup for secure websocket)
cert_path = certifi.where()
os.environ['SSL_CERT_FILE'] = cert_path
os.environ['WEBSOCKET_CLIENT_CA_BUNDLE'] = cert_path

try:
    from pyquotex.stable_api import Quotex
    from pyquotex.utils.processor import process_candles
    from pyquotex.config import credentials
except ImportError as e:
    print(f"\n❌ Error: Missing dependency - {e}")
    print("Run: pip install git+https://github.com/cleitonleonel/pyquotex.git@master\n")
    sys.exit(1)

# =====================================================================
# ⚙️ CONFIG: Console Verbosity Level
# =====================================================================
CONSOLE_LEVEL = 1

def log(msg: str, level: int = 1):
    """Print only if level <= CONSOLE_LEVEL"""
    if level <= CONSOLE_LEVEL:
        print(msg)

# =====================================================================
# Async Loop Manager (Handles core websocket connections in background)
# =====================================================================
ASYNC_LOOP = asyncio.new_event_loop()

def start_async_loop():
    asyncio.set_event_loop(ASYNC_LOOP)
    ASYNC_LOOP.run_forever()

threading.Thread(target=start_async_loop, daemon=True, name="AsyncLoop").start()

# =====================================================================
# UI Update Queue (Thread-safe Eel interface buffer)
# =====================================================================
UI_QUEUE = Queue()

def ui_loop():
    while True:
        try:
            payload = UI_QUEUE.get()
            if payload is None:
                break
            eel.updateChart(payload)()
            UI_QUEUE.task_done()
        except Exception as e:
            if CONSOLE_LEVEL >= 2:
                print(f"[UI Loop Error]: {e}")

threading.Thread(target=ui_loop, daemon=True, name="UIUpdater").start()

# =====================================================================
# Global Application State
# =====================================================================
LAST_TICK_TIME = time.time()
ASSET_DISPLAY_MAP: Dict[str, str] = {}

# ✅ Complete Asset Mapping Directory
forex_assets = {
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
}
ASSET_DISPLAY_MAP.update(forex_assets)

crypto_assets = {
    "ADAUSD_otc": "Cardano (OTC)", "APTUSD_otc": "Aptos (OTC)", "ARBUSD_otc": "Arbitrum (OTC)", "ATOUSD_otc": "ATO (OTC)",
    "AVAUSD_otc": "Avalanche (OTC)", "AXSUSD_otc": "Axie Infinity (OTC)", "BCHUSD_otc": "Bitcoin Cash (OTC)",
    "BNBUSD_otc": "Binance Coin (OTC)", "BONUSD_otc": "Bonk (OTC)", "BTCUSD_otc": "Bitcoin (OTC)", "DASUSD_otc": "Dash (OTC)",
    "DOGUSD_otc": "Dogecoin (OTC)", "DOTUSD_otc": "Polkadot (OTC)", "ETCUSD_otc": "Ethereum Classic (OTC)",
    "ETHUSD_otc": "Ethereum (OTC)", "FLOUSD_otc": "Floki (OTC)", "GALUSD_otc": "Gala (OTC)", "HMSUSD_otc": "Hamster Kombat (OTC)",
    "LINUSD_otc": "Chainlink (OTC)", "LTCUSD_otc": "Litecoin (OTC)", "MELUSD_otc": "Melania Meme (OTC)",
    "SHIBUSD_otc": "Shiba Inu (OTC)", "SOLUSD_otc": "Solana (OTC)", "TIAUSD_otc": "Celestia (OTC)", "TONUSD_otc": "Toncoin (OTC)",
    "TRUUSD_otc": "TrueFi (OTC)", "TRXUSD_otc": "TRON (OTC)", "WIFUSD_otc": "Dogwifhat (OTC)", "XRPUSD_otc": "Ripple (OTC)",
    "ZECUSD_otc": "Zcash (OTC)",
}
ASSET_DISPLAY_MAP.update(crypto_assets)

commodities_assets = {
    "XAUUSD": "Gold", "XAUUSD_otc": "Gold (OTC)", "XAGUSD": "Silver", "XAGUSD_otc": "Silver (OTC)",
    "UKBrent_otc": "UK Brent (OTC)", "USCrude_otc": "US Crude (OTC)",
}
ASSET_DISPLAY_MAP.update(commodities_assets)

stocks_assets = {
    "AXP_otc": "American Express (OTC)", "BA_otc": "Boeing Company (OTC)", "FB_otc": "Facebook (OTC)",
    "INTC_otc": "Intel (OTC)", "JNJ_otc": "Johnson & Johnson (OTC)", "MCD_otc": "McDonald's (OTC)",
    "MSFT_otc": "Microsoft (OTC)", "PFE_otc": "Pfizer Inc (OTC)", "PEPUSD_otc": "PepsiCo (OTC)",
}
ASSET_DISPLAY_MAP.update(stocks_assets)

indices_assets = {
    "DJIUSD": "Dow Jones", "NDXUSD": "NASDAQ 100", "F40EUR": "CAC 40", "FTSGBP": "FTSE 100",
    "HSIHKD": "Hong Kong 50", "IBXEUR": "IBEX 35", "JPXJPY": "Nikkei 225", "CHIA50": "China A50",
    "STXEUR": "EURO STOXX 50",
}
ASSET_DISPLAY_MAP.update(indices_assets)

DISPLAY_TO_INTERNAL = {v: k for k, v in ASSET_DISPLAY_MAP.items()}
ASSET_CATEGORIES = {
    "💱 Forex": list(forex_assets.values()),
    "₿ Crypto": list(crypto_assets.values()),
    "🛢️ Commodities": list(commodities_assets.values()),
    "🏦 Stocks": list(stocks_assets.values()),
    "📊 Indices": list(indices_assets.values()),
}
TIMEFRAMES = {
    "5s": 5, "10s": 10, "15s": 15, "30s": 30,
    "1m": 60, "2m": 120, "3m": 180, "5m": 300,
    "10m": 600, "15m": 900, "30m": 1800,
    "1h": 3600, "4h": 14400
}

CLIENT: Optional[Quotex] = None
CURRENT_ASSET = "AUD/CAD (OTC)"
CURRENT_TIMEFRAME = "1m"

# =====================================================================
# 🛠️ Verification Helpers & Watchdogs
# =====================================================================
def is_websocket_connected() -> bool:
    try:
        if not CLIENT or not CLIENT.api:
            return False
        if hasattr(CLIENT.api, '_is_connected'):
            return bool(CLIENT.api._is_connected)
        if hasattr(CLIENT.api, 'websocket_client'):
            ws = CLIENT.api.websocket_client
            if hasattr(ws, 'connected'):
                return bool(ws.connected)
        return True
    except Exception:
        return False

def price_sleep_watcher():
    global LAST_TICK_TIME, CLIENT, CURRENT_ASSET, ASYNC_LOOP
    while True:
        time.sleep(20)
        diff = time.time() - LAST_TICK_TIME
        if diff > 60:
            log(f"♻️ Stream idle {int(diff)}s — attempting proxy web-socket recovery", level=1)
            try:
                if CLIENT and CURRENT_ASSET:
                    internal = DISPLAY_TO_INTERNAL.get(CURRENT_ASSET)
                    if internal and is_websocket_connected():
                        period = TIMEFRAMES.get(CURRENT_TIMEFRAME, 60)
                        asyncio.run_coroutine_threadsafe(
                            CLIENT.start_realtime_price(internal, period),
                            ASYNC_LOOP
                        )
                        LAST_TICK_TIME = time.time()
            except Exception as e:
                print(f"❌ Real-time tunnel recovery failed: {e}")

threading.Thread(target=price_sleep_watcher, daemon=True, name="PriceWatcher").start()

def safe_stop_realtime_price(asset: str):
    if CLIENT and CLIENT.api:
        try:
            asyncio.run_coroutine_threadsafe(
                CLIENT.stop_realtime_price(asset),
                ASYNC_LOOP
            )
        except Exception as e:
            print(f"⚠️ Failed to unsubscribe stream for {asset}: {e}")

def process_candle_data(raw_data: list, period_sec: int) -> list:
    formatted = []
    if not raw_data:
        return formatted
    for candle in raw_data:
        try:
            ts = int(candle.get("time", 0))
            formatted.append({
                "time": ts,
                "open": float(candle.get("open", 0)),
                "high": float(candle.get("high", 0)),
                "low": float(candle.get("low", 0)),
                "close": float(candle.get("close", 0))
            })
        except (ValueError, KeyError, TypeError):
            continue
    formatted.sort(key=lambda x: x["time"])
    return formatted

# =====================================================================
# 📡 Strict Real-time Socket Event Dispatcher (100% Real, No Random)
# =====================================================================
async def realtime_price_listener():
    global CLIENT, CURRENT_ASSET, CURRENT_TIMEFRAME, LAST_TICK_TIME
    while True:
        await asyncio.sleep(0.1)
        if not CLIENT or not CLIENT.api or not is_websocket_connected():
            continue
            
        internal_asset = DISPLAY_TO_INTERNAL.get(CURRENT_ASSET)
        if not internal_asset:
            continue
            
        try:
            if hasattr(CLIENT.api, 'realtime_price') and internal_asset in CLIENT.api.realtime_price:
                tick_data = CLIENT.api.realtime_price[internal_asset]
                if tick_data:
                    LAST_TICK_TIME = time.time()
                    price = float(tick_data.get("price", 0))
                    ts = int(tick_data.get("time", time.time()))
                    
                    payload = {
                        "asset": CURRENT_ASSET,
                        "timeframe": CURRENT_TIMEFRAME,
                        "time": ts,
                        "open": price,
                        "high": price,
                        "low": price,
                        "close": price
                    }
                    UI_QUEUE.put(payload)
        except Exception as e:
            if CONSOLE_LEVEL >= 2:
                print(f"⚠️ Error inside data extraction interface: {e}")

asyncio.run_coroutine_threadsafe(realtime_price_listener(), ASYNC_LOOP)

# =====================================================================
# ⚡ Eel UI Binding Exposed Interfaces
# =====================================================================
@eel.expose
def login_to_quotex(email, password):
    global CLIENT, LOGIN_SUCCESS
    log(f"🔑 Secure proxy auth pipeline initiated for: {email}")
    
    async def _auth():
        global CLIENT
        try:
            CLIENT = Quotex(email=email, password=password)
            await CLIENT.connect()
            return True, "Success"
        except Exception as e:
            return False, str(e)
            
    future = asyncio.run_coroutine_threadsafe(_auth(), ASYNC_LOOP)
    try:
        success, msg = future.result(timeout=45) # প্রক্সি লেটেন্সির জন্য ৪৫ সেকেন্ড দেওয়া হলো
        LOGIN_SUCCESS = success
    except Exception as e:
        success, msg = False, f"Connection Timeout: {str(e)}"
    
    if success:
        log("✅ Connection authenticated over proxy tunnel successfully.")
        eel.showChartPage()()
    else:
        log(f"❌ Handshake failed: {msg}")
        eel.showError(msg)()

@eel.expose
def change_asset(asset_display: str):
    global CURRENT_ASSET
    if asset_display not in DISPLAY_TO_INTERNAL:
        return
        
    log(f"🔄 Requesting proxy stream transition to: {asset_display}")
    old_asset = CURRENT_ASSET
    CURRENT_ASSET = asset_display
    
    async def _switch():
        if CLIENT and is_websocket_connected():
            old_internal = DISPLAY_TO_INTERNAL.get(old_asset)
            if old_internal:
                safe_stop_realtime_price(old_internal)
                
            new_internal = DISPLAY_TO_INTERNAL.get(asset_display)
            period = TIMEFRAMES.get(CURRENT_TIMEFRAME, 60)
            
            # Fetching historical candles over secure proxy tunnel
            hist_data = await CLIENT.get_candles(
                asset=new_internal,
                end_from_time=time.time(),
                offset=150 * period,
                period=period
            )
            processed = process_candle_data(hist_data, period)
            
            for candle in processed:
                UI_QUEUE.put({
                    "asset": asset_display,
                    "timeframe": CURRENT_TIMEFRAME,
                    "is_history": True,
                    **candle
                })
                
            await CLIENT.start_realtime_price(new_internal, period)
            
    asyncio.run_coroutine_threadsafe(_switch(), ASYNC_LOOP)

@eel.expose
def get_categories():
    return ASSET_CATEGORIES

def write_login_html():
    pass

def write_chart_html():
    pass

if __name__ == '__main__':
    os.makedirs("web", exist_ok=True)
    write_login_html()
    write_chart_html()
    
    log("🚀 Quotex Pro Trader Client Engine Booted — 100% Real Live Streams Over Proxy")
    eel.init('web')
    eel.start('login.html', size=(1024, 768))
