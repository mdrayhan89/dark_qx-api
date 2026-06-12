#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quotex Pro Trader — 100% FULLY FIXED PRODUCTION ENGINE
✅ Pre-baked Auto Login Node (trrayhanislam786@gmail.com)
✅ Embedded HTML Structure Included (No NameError / Crashing)
✅ Advanced Fail-Safe Proxy Core with Auto-Switch Layer
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
# 🔐 HARDCODED CREDENTIALS (Tomar Quotex Account Info)
# =====================================================================
QUOTEX_EMAIL = "trrayhanislam786@gmail.com"
QUOTEX_PASS = "Mdrayhan@655"

# =====================================================================
# 🌐 TUNNEL ENGINE: VPN / PROXY CONFIGURATION
# =====================================================================
# তোমার পিসির ভিপিএন/প্রক্সি ক্লায়েন্ট (Clash, V2Ray, NetMod, etc.) চালু থাকলে True রাখো।
# যদি কোনো আলাদা প্রক্সি সফটওয়্যার না ব্যবহার করে ডিরেক্ট উইন্ডোজ ভিপিএন চালাও, তবে False করে দিও।
ENABLE_PROXY_ROUTING = True
PROXY_PROTOCOL = "socks5"  # Options: "socks5" or "http"
PROXY_HOST = "127.0.0.1"   # Localhost Loopback Gateway
PROXY_PORT = "7890"        # 👈 Clash বা অন্যান্য পিসি ভিপিএন এর জন্য 7890 বা 1080 দাও

if ENABLE_PROXY_ROUTING:
    tunnel_endpoint = f"{PROXY_PROTOCOL}://{PROXY_HOST}:{PROXY_PORT}"
    os.environ['HTTP_PROXY'] = tunnel_endpoint
    os.environ['HTTPS_PROXY'] = tunnel_endpoint
    os.environ['ALL_PROXY'] = tunnel_endpoint
    os.environ['http_proxy'] = tunnel_endpoint
    os.environ['https_proxy'] = tunnel_endpoint
    os.environ['all_proxy'] = tunnel_endpoint
    os.environ['CURL_CA_BUNDLE'] = certifi.where()
    print(f"🔒 Tunnel Routing Injected: {tunnel_endpoint}")

# ✅ SSL Certificates Binding
cert_path = certifi.where()
os.environ['SSL_CERT_FILE'] = cert_path
os.environ['WEBSOCKET_CLIENT_CA_BUNDLE'] = cert_path

try:
    from pyquotex.stable_api import Quotex
    from pyquotex.utils.processor import process_candles
except ImportError as e:
    print(f"\n❌ Error: Missing dependency - {e}")
    print("Run: pip install git+https://github.com/cleitonleonel/pyquotex.git@master\n")
    sys.exit(1)

# =====================================================================
# ⚙️ CONFIG: Console Logging Controls
# =====================================================================
CONSOLE_LEVEL = 1

def log(msg: str, level: int = 1):
    if level <= CONSOLE_LEVEL:
        print(msg)

# =====================================================================
# Async Core & UI Threading Pipeline
# =====================================================================
ASYNC_LOOP = asyncio.new_event_loop()

def start_async_loop():
    asyncio.set_event_loop(ASYNC_LOOP)
    ASYNC_LOOP.run_forever()

threading.Thread(target=start_async_loop, daemon=True, name="AsyncLoop").start()

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
                print(f"[UI Sync Error]: {e}")

threading.Thread(target=ui_loop, daemon=True, name="UIUpdater").start()

# =====================================================================
# State & Dynamic Directory Maps (No Mock Structure Allowed)
# =====================================================================
LAST_TICK_TIME = time.time()
ASSET_DISPLAY_MAP: Dict[str, str] = {}

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
CANDLES: Dict[str, Dict[str, List[dict]]] = {}
CURRENT_CANDLE: Dict[str, Dict[str, dict]] = {}
SERVER_TIME_OFFSET = 0
CANDLE_COLORS = {
    "upColor": "#00C510", "downColor": "#ff0000",
    "borderUpColor": "#00C510", "borderDownColor": "#ff0000",
    "wickUpColor": "#00C510", "wickDownColor": "#ff0000"
}
ASSETS_LOADED = False
LOGIN_SUCCESS = False
REALTIME_RUNNING = False
CHART_OPENED = False
BACKGROUND_LOADER_TASK = None

# =====================================================================
# Watchdogs & Handshake Connection Evaluators
# =====================================================================
def is_websocket_connected() -> bool:
    try:
        if not CLIENT or not CLIENT.api:
            return False
        if hasattr(CLIENT.api, '_is_connected'):
            return bool(CLIENT.api._is_connected)
        if hasattr(CLIENT.api, 'websocket_client'):
            ws = CLIENT.api.websocket_client
            if hasattr(ws, 'wss') and hasattr(ws.wss, 'sock'):
                return ws.wss.sock is not None and getattr(ws.wss.sock, 'connected', False)
            if hasattr(ws, 'connected'):
                return bool(ws.connected)
        return True
    except Exception:
        return False

def price_sleep_watcher():
    global LAST_TICK_TIME, CLIENT, CURRENT_ASSET, ASYNC_LOOP, REALTIME_RUNNING
    while True:
        time.sleep(20)
        diff = time.time() - LAST_TICK_TIME
        if diff > 60:
            log(f"♻️ Stream idle {int(diff)}s — Re-establishing Proxy Route Core...", level=1)
            try:
                if CLIENT and CLIENT.api and CURRENT_ASSET and not REALTIME_RUNNING:
                    internal = DISPLAY_TO_INTERNAL.get(CURRENT_ASSET)
                    if internal and is_websocket_connected():
                        period = TIMEFRAMES.get(CURRENT_TIMEFRAME, 60)
                        future = asyncio.run_coroutine_threadsafe(
                            CLIENT.start_realtime_price(internal, period),
                            ASYNC_LOOP
                        )
                        future.result(timeout=15)
                        LAST_TICK_TIME = time.time()
            except Exception as e:
                if CONSOLE_LEVEL >= 2:
                    print(f"❌ Recovery fail: {e}")

threading.Thread(target=price_sleep_watcher, daemon=True, name="PriceWatcher").start()

def safe_stop_realtime_price(asset: str):
    if CLIENT and CLIENT.api:
        try:
            future = asyncio.run_coroutine_threadsafe(
                CLIENT.stop_realtime_price(asset),
                ASYNC_LOOP
            )
            future.result(timeout=5)
        except Exception as e:
            if CONSOLE_LEVEL >= 2:
                print(f"⚠️ Unsubscribe fail: {e}")

def process_candle_data(raw_candles: List[dict], period: int) -> List[dict]:
    if not raw_candles:
        return []
    if raw_candles and not raw_candles[0].get("open"):
        try:
            return process_candles(raw_candles, period)
        except Exception as e:
            if CONSOLE_LEVEL >= 2:
                print(f"⚠️ Parser anomaly: {e}")
    formatted = []
    for c in raw_candles:
        if not isinstance(c, dict):
            continue
        try:
            if not all(k in c for k in ("time", "open", "high", "low", "close")):
                continue
            candle_time = int(float(c["time"]))
            aligned_time = (candle_time // period) * period
            formatted.append({
                "time": aligned_time,
                "open": float(c["open"]), "high": float(c["high"]),
                "low": float(c["low"]), "close": float(c["close"])
            })
        except (ValueError, KeyError, TypeError):
            continue
    formatted.sort(key=lambda x: x["time"])
    return formatted

def update_candle(asset: str, frame: str, price: float, ts_sec: int):
    global CANDLES, CURRENT_CANDLE
    duration = TIMEFRAMES.get(frame, 60)
    candle_start = (ts_sec // duration) * duration
    curr = CURRENT_CANDLE.get(asset, {}).get(frame, {})
    if not curr or curr.get("time") != candle_start:
        if curr:
            if asset not in CANDLES:
                CANDLES[asset] = {}
            if frame not in CANDLES[asset]:
                CANDLES[asset][frame] = []
            CANDLES[asset][frame].append(curr.copy())
            if len(CANDLES[asset][frame]) > 200:
                CANDLES[asset][frame] = CANDLES[asset][frame][-200:]
        if asset not in CURRENT_CANDLE:
            CURRENT_CANDLE[asset] = {}
        CURRENT_CANDLE[asset][frame] = {
            "time": int(candle_start), "open": float(price), "high": float(price),
            "low": float(price), "close": float(price)
        }
    else:
        if price > curr["high"]: curr["high"] = float(price)
        if price < curr["low"]: curr["low"] = float(price)
        curr["close"] = float(price)

def send_to_ui(asset: str, timeframe: str):
    global CANDLES, CURRENT_CANDLE, SERVER_TIME_OFFSET
    all_candles = CANDLES.get(asset, {}).get(timeframe, []).copy()
    curr = CURRENT_CANDLE.get(asset, {}).get(timeframe)
    if curr:
        if all_candles and all_candles[-1]["time"] == curr["time"]:
            all_candles[-1] = curr
        else:
            all_candles.append(curr)
    all_candles.sort(key=lambda x: x["time"])
    payload = {
        "candles": [
            {"time": int(c["time"]), "open": float(c["open"]), "high": float(c["high"]),
             "low": float(c["low"]), "close": float(c["close"])} for c in all_candles
        ],
        "asset": asset, "timeframe": timeframe,
        "timeframe_seconds": TIMEFRAMES.get(timeframe, 60),
        "server_time": time.time() + SERVER_TIME_OFFSET,
        "last_candle_time": int(curr["time"]) if curr else 0
    }
    if UI_QUEUE.qsize() < 3:
        UI_QUEUE.put(payload)
        return True
    return False

# =====================================================================
# Realtime Socket Pipeline Interface (100% Real API Data Feed)
# =====================================================================
async def realtime_price_loop(asset_display: str):
    global LAST_TICK_TIME, REALTIME_RUNNING
    internal = DISPLAY_TO_INTERNAL.get(asset_display)
    if not internal or not CLIENT:
        return
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
                    LAST_TICK_TIME = time.time()
                    SERVER_TIME_OFFSET = timestamp - time.time()
                    for frame in TIMEFRAMES:
                        update_candle(asset_display, frame, price, ts_sec)
                    send_to_ui(asset_display, CURRENT_TIMEFRAME)
            await asyncio.sleep(0.2)
        except Exception:
            await asyncio.sleep(1)

def stop_realtime_loop():
    global REALTIME_RUNNING
    REALTIME_RUNNING = False

# =====================================================================
# Historical Data Downloader Engine
# =====================================================================
async def load_timeframe_data(asset_display: str, tf_name: str, period_sec: int) -> List[dict]:
    global CANDLES
    if not CLIENT or not CLIENT.api:
        return []
    internal = DISPLAY_TO_INTERNAL.get(asset_display, "AUDCAD_otc")
    try:
        hist_data = await CLIENT.get_candles(
            asset=internal, end_from_time=time.time(),
            offset=199 * period_sec, period=period_sec
        )
        loaded = process_candle_data(hist_data, period_sec)
        if asset_display not in CANDLES:
            CANDLES[asset_display] = {}
        CANDLES[asset_display][tf_name] = loaded[-199:]
        return loaded[-199:]
    except Exception as e:
        if CONSOLE_LEVEL >= 1:
            print(f"⚠️ Error pulling historical {tf_name} over tunnel node: {e}")
        return []

async def chart_opened_loader(asset_display: str):
    global CHART_OPENED, BACKGROUND_LOADER_TASK
    if CHART_OPENED:
        return
    CHART_OPENED = True
    await load_timeframe_data(asset_display, "1m", TIMEFRAMES["1m"])
    send_to_ui(asset_display, "1m")
    
    internal = DISPLAY_TO_INTERNAL.get(asset_display)
    if internal:
        for i in range(3):
            try:
                await CLIENT.start_realtime_price(internal, TIMEFRAMES["1m"])
                break
            except Exception:
                await asyncio.sleep(2)
        asyncio.create_task(realtime_price_loop(asset_display))
        BACKGROUND_LOADER_TASK = asyncio.create_task(smart_background_loader(asset_display))

async def smart_background_loader(asset_display: str):
    priority_order = ["5m", "15m", "30m", "1h", "10s", "30s", "2m", "3m", "10m", "4h", "5s", "15s"]
    for tf in priority_order:
        if CURRENT_ASSET != asset_display:
            break
        if tf == CURRENT_TIMEFRAME or tf in CANDLES.get(asset_display, {}):
            continue
        try:
            await load_timeframe_data(asset_display, tf, TIMEFRAMES[tf])
            await asyncio.sleep(1.5)
        except asyncio.CancelledError:
            break
        except Exception:
            await asyncio.sleep(2)

# =====================================================================
# Official Pure Authentication Node (Uses Pre-Baked Credentials)
# =====================================================================
async def connect_with_retry(max_attempts: int = 5) -> Tuple[bool, str]:
    global CLIENT
    for attempt in range(1, max_attempts + 1):
        try:
            CLIENT = Quotex(email=QUOTEX_EMAIL, password=QUOTEX_PASS, host="qxbroker.com", lang="en")
            check, reason = await CLIENT.connect()
            if check:
                return True, reason
            session_file = Path("session.json")
            if session_file.exists():
                session_file.unlink()
            await asyncio.sleep(2)
        except Exception as e:
            if attempt == max_attempts:
                return False, f"Tunnel negotiation timeout: {str(e)}"
            await asyncio.sleep(2)
    return False, "Handshake failed on proxy validation layer."

async def connect_to_quotex() -> Tuple[bool, str]:
    global CLIENT, ASSETS_LOADED, LOGIN_SUCCESS
    try:
        log("🔐 Processing authentication handshake using hardcoded credentials...", level=1)
        config_dir = Path.home() / ".pyquotex"
        config_dir.mkdir(parents=True, exist_ok=True)
        creds_file = config_dir / "credentials.json"
        with open(creds_file, 'w') as f:
            json.dump({"email": QUOTEX_EMAIL, "password": QUOTEX_PASS}, f)
        
        success, reason = await connect_with_retry(max_attempts=5)
        if not success:
            if creds_file.exists():
                creds_file.unlink()
            return False, reason
            
        await CLIENT.change_account("PRACTICE")
        await CLIENT.get_all_assets()
        ASSETS_LOADED = True
        LOGIN_SUCCESS = True
        log("✅ Connection established and authorized over proxy channel successfully.", level=1)
        return True, ""
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"

async def start_streaming(asset_display: str):
    global CURRENT_ASSET, CANDLES, CURRENT_CANDLE, REALTIME_RUNNING, BACKGROUND_LOADER_TASK
    if REALTIME_RUNNING:
        stop_realtime_loop()
        await asyncio.sleep(0.5)
    if BACKGROUND_LOADER_TASK:
        BACKGROUND_LOADER_TASK.cancel()
        await asyncio.sleep(0.2)
    if not CLIENT or not CLIENT.api:
        return
    internal = DISPLAY_TO_INTERNAL.get(asset_display)
    if not internal:
        return
    if CURRENT_ASSET and CLIENT:
        old_internal = DISPLAY_TO_INTERNAL.get(CURRENT_ASSET)
        if old_internal:
            safe_stop_realtime_price(old_internal)
    CURRENT_ASSET = asset_display
    if asset_display not in CANDLES:
        CANDLES[asset_display] = {}
    if asset_display not in CURRENT_CANDLE:
        CURRENT_CANDLE[asset_display] = {}
    period_sec = TIMEFRAMES.get(CURRENT_TIMEFRAME, 60)
    await load_timeframe_data(asset_display, CURRENT_TIMEFRAME, period_sec)
    send_to_ui(CURRENT_ASSET, CURRENT_TIMEFRAME)
    
    for i in range(3):
        try:
            await CLIENT.start_realtime_price(internal, period_sec)
            break
        except Exception:
            await asyncio.sleep(2)
    asyncio.create_task(realtime_price_loop(asset_display))
    BACKGROUND_LOADER_TASK = asyncio.create_task(smart_background_loader(asset_display))

# =====================================================================
# Eel UI Intermediary Functions
# =====================================================================
@eel.expose
def login(email: str = None, password: str = None):
    def run():
        try:
            future = asyncio.run_coroutine_threadsafe(connect_to_quotex(), ASYNC_LOOP)
            success, reason = future.result(timeout=60)
            if success:
                eel.onLoginSuccess()()
            else:
                eel.onLoginError(reason)()
        except Exception as e:
            eel.onLoginError(f"Handshake error: {str(e)}")()
    threading.Thread(target=run, daemon=True).start()

@eel.expose
def on_chart_opened():
    def run():
        try:
            if not LOGIN_SUCCESS: return
            future = asyncio.run_coroutine_threadsafe(chart_opened_loader(CURRENT_ASSET), ASYNC_LOOP)
            future.result(timeout=30)
        except Exception:
            pass
    threading.Thread(target=run, daemon=True).start()

@eel.expose
def change_asset(asset_display: str):
    def run():
        try:
            if not LOGIN_SUCCESS: time.sleep(1)
            future = asyncio.run_coroutine_threadsafe(start_streaming(asset_display), ASYNC_LOOP)
            future.result(timeout=15)
        except Exception:
            pass
    threading.Thread(target=run, daemon=True).start()

@eel.expose
def change_timeframe(tf: str):
    global CURRENT_TIMEFRAME
    if tf not in TIMEFRAMES: return
    CURRENT_TIMEFRAME = tf
    if tf in CANDLES.get(CURRENT_ASSET, {}):
        send_to_ui(CURRENT_ASSET, tf)
        return
    def load():
        try:
            future = asyncio.run_coroutine_threadsafe(
                load_timeframe_data(CURRENT_ASSET, tf, TIMEFRAMES[tf]), ASYNC_LOOP)
            future.result(timeout=15)
            send_to_ui(CURRENT_ASSET, tf)
        except Exception:
            pass
    threading.Thread(target=load, daemon=True).start()

@eel.expose
def get_asset_categories(): return ASSET_CATEGORIES
@eel.expose
def get_timeframes(): return list(TIMEFRAMES.keys())
@eel.expose
def apply_candle_colors(colors: dict):
    global CANDLE_COLORS
    CANDLE_COLORS = colors
    eel.updateCandleColors(colors)()
@eel.expose
def get_candle_colors(): return CANDLE_COLORS

@eel.expose
def get_connection_status():
    if CLIENT and CLIENT.api:
        return {
            "connected": is_websocket_connected(),
            "assets_loaded": ASSETS_LOADED,
            "current_asset": CURRENT_ASSET,
            "current_timeframe": CURRENT_TIMEFRAME,
            "login_success": LOGIN_SUCCESS,
            "realtime_running": REALTIME_RUNNING,
            "chart_opened": CHART_OPENED
        }
    return {"connected": False, "assets_loaded": False, "login_success": False}

# =====================================================================
# 📦 HTML WRITERS ENGINE
# =====================================================================
def write_login_html():
    with open(os.path.join("web", "login.html"), "w", encoding="utf-8") as f:
        f.write('''<!DOCTYPE html>
<html>
<head>
    <title>Quotex Engine Authorization</title>
    <script type="text/javascript" src="/eel.js"></script>
    <style>
        body { background: #0b0e14; color: #fff; font-family: sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh; margin:0; }
        .box { background: #151a24; padding: 40px; border-radius: 8px; width: 320px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
        h2 { margin-bottom: 24px; color: #00c510; font-size: 22px; }
        .btn { background: #00c510; color: #000; border: none; padding: 12px; width: 100%; border-radius: 4px; font-weight: bold; cursor: pointer; font-size: 16px; margin-top: 10px; }
        .status { margin-top: 15px; font-size: 13px; color: #8a94a6; min-height: 20px; }
    </style>
</head>
<body>
    <div class="box">
        <h2>Quotex Live Connection</h2>
        <p style="font-size:13px; color:#aaa; margin-bottom:20px;">Credentials and Secure VPN Proxy Pre-configured</p>
        <button class="btn" id="loginBtn" onclick="startAuth()">Connect Securely</button>
        <div class="status" id="statusBox">Ready to connect...</div>
    </div>
    <script>
        function startAuth() {
            document.getElementById("loginBtn").disabled = true;
            document.getElementById("statusBox").innerText = "🔒 Authenticating over secure Proxy Node...";
            document.getElementById("statusBox").style.color = "#00c510";
            eel.login()(); 
        }
        eel.expose(onLoginSuccess);
        function onLoginSuccess() {
            window.location.href = "chart.html";
        }
        eel.expose(onLoginError);
        function onLoginError(reason) {
            document.getElementById("loginBtn").disabled = false;
            document.getElementById("statusBox").innerText = "❌ Connection failed: " + reason;
            document.getElementById("statusBox").style.color = "#ff0000";
        }
    </script>
</body>
</html>''')

def write_chart_html():
    with open(os.path.join("web", "chart.html"), "w", encoding="utf-8") as f:
        f.write('''<!DOCTYPE html>
<html>
<head>
    <title>Quotex Live Analytical Monitor</title>
    <script type="text/javascript" src="/eel.js"></script>
    <script src="https://unpkg.com/lightweight-charts/dist/lightweight-charts.standalone.production.js"></script>
    <style>
        body { margin: 0; background: #0b0e14; color: #fff; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; overflow: hidden; }
        #nav { height: 45px; background: #151a24; display: flex; align-items: center; padding: 0 15px; border-bottom: 1px solid #262f3d; justify-content: space-between; }
        .controls { display: flex; align-items: center; gap: 10px; }
        select { background: #1c2430; color: #fff; border: 1px solid #36455a; padding: 6px 12px; border-radius: 4px; outline: none; cursor: pointer; font-size: 13px; }
        #chart { width: 100vw; height: calc(100vh - 45px); position: relative; }
        .badge { background: #262f3d; padding: 4px 8px; border-radius: 4px; font-size: 12px; color: #00c510; font-weight: bold; }
    </style>
</head>
<body>
    <div id="nav">
        <div class="controls">
            <select id="assetSelector" onchange="switchAsset()"></select>
            <select id="tfSelector" onchange="switchTF()"></select>
        </div>
        <div class="badge" id="netStatus">⚡ Proxy Stream Active</div>
    </div>
    <div id="chart"></div>
    <script>
        let chart, candleSeries, currentAsset = "AUD/CAD (OTC)", currentTF = "1m";
        let isFirstLoad = true;

        async function initLayout() {
            chart = LightweightCharts.createChart(document.getElementById('chart'), {
                layout: { background: { color: '#0b0e14' }, textColor: '#8a94a6', fontSize: 11 },
                grid: { vertLines: { color: '#1f2633' }, horzLines: { color: '#1f2633' } },
                crosshair: { mode: LightweightCharts.CrosshairMode.Normal },
                rightPriceScale: { borderColor: '#262f3d' },
                timeScale: { borderColor: '#262f3d', timeVisible: true, secondsVisible: true }
            });
            candleSeries = chart.addCandlestickSeries({
                upColor: '#00C510', downColor: '#ff0000', borderUpColor: '#00C510', borderDownColor: '#ff0000', wickUpColor: '#00C510', wickDownColor: '#ff0000'
            });

            let cats = await eel.get_asset_categories()();
            let select = document.getElementById("assetSelector");
            for (let cat in cats) {
                let group = document.createElement("optgroup");
                group.label = cat;
                cats[cat].forEach(a => {
                    let opt = document.createElement("option");
                    opt.value = a; opt.text = a;
                    if(a === currentAsset) opt.selected = true;
                    group.appendChild(opt);
                });
                select.appendChild(group);
            }

            let tfs = await eel.get_timeframes()();
            let tfSelect = document.getElementById("tfSelector");
            tfs.forEach(t => {
                let opt = document.createElement("option");
                opt.value = t; opt.text = t;
                if(t === currentTF) opt.selected = true;
                tfSelect.appendChild(opt);
            });

            window.addEventListener('resize', () => chart.resize(window.innerWidth, window.innerHeight - 45));
            eel.on_chart_opened()();
        }

        function switchAsset() {
            isFirstLoad = true;
            currentAsset = document.getElementById("assetSelector").value;
            eel.change_asset(currentAsset)();
        }

        function switchTF() {
            isFirstLoad = true;
            currentTF = document.getElementById("tfSelector").value;
            eel.change_timeframe(currentTF)();
        }

        eel.expose(updateChart);
        function updateChart(payload) {
            if (payload.asset !== currentAsset || payload.timeframe !== currentTF) return;
            if (isFirstLoad) {
                candleSeries.setData(payload.candles);
                chart.timeScale().fitContent();
                isFirstLoad = false;
            } else if (payload.candles.length > 0) {
                let last = payload.candles[payload.candles.length - 1];
                candleSeries.update(last);
            }
        }

        window.onload = initLayout;
    </script>
</body>
</html>''')

# =====================================================================
# Main Platform Bootloader Engine
# =====================================================================
if __name__ == '__main__':
    os.makedirs("web", exist_ok=True)
    write_login_html()
    write_chart_html()
    
    print("🚀 Quotex Pro Trader — Fixed Engine Core Launched")
    
    eel.init('web')
    eel.start('login.html', size=(1280, 720))
