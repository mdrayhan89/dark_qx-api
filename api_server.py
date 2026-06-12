#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quotex Pro Trader — MASTER ENGINE (ALL PAIRS FIXED)
✅ Complete 100+ Asset Directory Pipeline Fully Integrated
✅ Generates 3000 Candles Historical Array Structure (Matches Screenshot)
✅ Embedded Lightweight Dashboard API Server For Live Matrix
✅ 100% Render Cloud Headless & Local Mode Friendly
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
from http.server import SimpleHTTPRequestHandler, HTTPServer
from typing import Optional, Dict, List, Tuple

# SSL Core Adaption Layer
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
cert_path = certifi.where()
os.environ['SSL_CERT_FILE'] = cert_path
os.environ['WEBSOCKET_CLIENT_CA_BUNDLE'] = cert_path

# Headless Platform Detection
IS_RENDER = os.environ.get('RENDER') is not None or os.environ.get('PORT') is not None
PORT = int(os.environ.get('PORT', 8080))

try:
    from pyquotex.stable_api import Quotex
    from pyquotex.utils.processor import process_candles
except ImportError as e:
    print(f"\n❌ Core Dependency Missing: {e}")
    print("Please check your requirements.txt dependencies.\n")
    sys.exit(1)

# Runtime Context Engagements
ASYNC_LOOP = asyncio.new_event_loop()
CLIENT: Optional[Quotex] = None
GLOBAL_DASHBOARD_DATA = {}
CANDLES: Dict[str, Dict[str, List[dict]]] = {}
CURRENT_CANDLE: Dict[str, Dict[str, dict]] = {}

# =====================================================================
# 📊 ALL SUPPORTED PAIRS DIRECTORY (100% UNTOUCHED & TOTAL FIXED)
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
TIMEFRAMES = {"1m": 60, "5m": 300, "15m": 900}

CURRENT_ASSET = "AUD/CAD (OTC)"  # ডেডিকেটেড হিস্টোরিক্যাল এসেট বুট পয়েন্ট
CURRENT_TIMEFRAME = "1m"

# ড্যাশবোর্ড জেসন নোড ইন্টিগ্রেশন
for internal, display in ASSET_DISPLAY_MAP.items():
    GLOBAL_DASHBOARD_DATA[display] = {
        "asset": display, "price": "Loading...", "direction": "STABLE", "timestamp": int(time.time())
    }

def configure_backend_tunnel():
    if os.environ.get('PROXY_URL'):
        os.environ['HTTPS_PROXY'] = os.environ.get('PROXY_URL', '')
        os.environ['HTTP_PROXY'] = os.environ.get('PROXY_URL', '')

# =====================================================================
# 🌐 LIGHTWEIGHT WEBSERVER FOR INTERFACE MATRIX
# =====================================================================
class WebStreamHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/live-data':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(GLOBAL_DASHBOARD_DATA).encode('utf-8'))
        else:
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            html_content = """
            <!DOCTYPE html><html><head><meta charset="UTF-8"><title>Live Matrix</title>
            <style>
                body { background: #0c1017; color: #fff; font-family: sans-serif; margin: 30px; }
                table { width: 100%; max-width: 800px; margin: 0 auto; border-collapse: collapse; background: #161b22; border-radius: 6px; overflow: hidden;}
                th, td { padding: 12px; text-align: left; border-bottom: 1px solid #30363d; }
                th { background: #21262d; color: #8b949e; }
                .up { color: #26a69a; font-weight: bold; }
                .down { color: #ef5350; font-weight: bold; }
                .stable { color: #8b949e; }
            </style></head><body>
            <h2 style="text-align:center; color:#4f46e5;">📊 Quotex Asset Matrix Stream</h2>
            <table><thead><tr><th>Asset Pair</th><th>Live Price</th><th>Vector</th></tr></thead>
            <tbody id="rows"></tbody></table>
            <script>
                async function load() {
                    const r = await fetch('/api/live-data'); const d = await r.json();
                    let h = ''; for(let k in d) {
                        let a = d[k]; let cls = a.direction.toLowerCase();
                        h += `<tr><td><b>${a.asset}</b></td><td class="${cls}">${a.price}</td><td class="${cls}">${a.direction}</td></tr>`;
                    }
                    document.getElementById('rows').innerHTML = h;
                } setInterval(load, 500); load();
            </script></body></html>
            """
            self.wfile.write(html_content.encode('utf-8'))

def start_web_server():
    server = HTTPServer(('0.0.0.0', PORT), WebStreamHandler)
    print(f"🌐 Cloud Interface Dashboard Link Active on Port: {PORT}")
    server.serve_forever()

def start_async_loop():
    asyncio.set_event_loop(ASYNC_LOOP)
    ASYNC_LOOP.run_forever()

threading.Thread(target=start_async_loop, daemon=True, name="AsyncCore").start()
threading.Thread(target=start_web_server, daemon=True, name="WebUI").start()

# =====================================================================
# ⚡ CORE DATA STREAMING PIPELINES
# =====================================================================
def process_candle_data(raw_candles: List[dict], period: int) -> List[dict]:
    if not raw_candles: return []
    if raw_candles and not raw_candles[0].get("open"):
        try: return process_candles(raw_candles, period)
        except Exception: return []
    formatted = []
    for c in raw_candles:
        try:
            formatted.append({
                "time": (int(float(c["time"])) // period) * period, "open": float(c["open"]),
                "high": float(c["high"]), "low": float(c["low"]), "close": float(c["close"])
            })
        except Exception: continue
    formatted.sort(key=lambda x: x["time"])
    return formatted

async def load_3000_candles(asset_display: str, tf_name: str) -> List[dict]:
    global CANDLES
    if not CLIENT or not CLIENT.api: return []
    internal = DISPLAY_TO_INTERNAL.get(asset_display, "AUDCAD_otc")
    period_sec = TIMEFRAMES.get(tf_name, 60)
    try:
        print(f"\n📥 Fetching 3000 Candles Array Block for {asset_display}...")
        hist_data = await CLIENT.get_candles(asset=internal, end_from_time=time.time(), offset=3000 * period_sec, period=period_sec)
        loaded = process_candle_data(hist_data, period_sec)
        if asset_display not in CANDLES: CANDLES[asset_display] = {}
        CANDLES[asset_display][tf_name] = loaded[-3000:]
        print(f"📦 [ARRAY SUCCESS] Loaded {len(CANDLES[asset_display][tf_name])} Candles for {asset_display}.")
        return CANDLES[asset_display][tf_name]
    except Exception as e:
        print(f"❌ Array Engine Error: {e}")
        return []

def update_live_matrix(asset_display: str, price: float):
    global GLOBAL_DASHBOARD_DATA
    prev = GLOBAL_DASHBOARD_DATA.get(asset_display, {})
    prev_p = prev.get("price")
    if prev_p == "Loading...": direction = "STABLE"
    else: direction = "UP" if price > float(prev_p) else ("DOWN" if price < float(prev_p) else prev.get("direction", "STABLE"))
    GLOBAL_DASHBOARD_DATA[asset_display] = {
        "asset": asset_display, "price": f"{price:.5f}", "direction": direction, "timestamp": int(time.time())
    }

async def dynamic_bulk_stream_loop():
    """মাস্টার ডিরেক্টরির সব পেয়ার থেকে ডেটা ফেচিং লুপ"""
    while True:
        if CLIENT and CLIENT.api:
            for internal, display in ASSET_DISPLAY_MAP.items():
                try:
                    data = await CLIENT.get_realtime_price(internal)
                    if data and len(data) > 0:
                        price = float(data[-1].get("price", data[-1].get("close", 0)))
                        if price > 0:
                            update_live_matrix(display, price)
                except Exception: continue
        await asyncio.sleep(0.2)

async def start_broker_pipeline():
    global CLIENT
    email = os.environ.get("QUOTEX_EMAIL", "trrayhanislam786@gmail.com")
    password = os.environ.get("QUOTEX_PASSWORD", "@quotextrader123")
    
    CLIENT = Quotex(email=email, password=password, host="qxbroker.com", lang="en")
    check, reason = await CLIENT.connect()
    if check:
        await CLIENT.change_account("PRACTICE")
        print("✅ [CONNECTED] WebSocket Streaming Tunnel successfully mapped.")
        
        # ৩০০০ হিস্টোরিক্যাল ক্যান্ডেল ইনিশিয়াল বুট স্ট্র্যাপার কল
        await load_3000_candles(CURRENT_ASSET, CURRENT_TIMEFRAME)
        
        # সব পেয়ার ডাইনামিক সাবস্ক্রিপশন রেজিস্ট্রেশন
        print("⚡ Subscribing to all master pairs in directory...")
        for internal in ASSET_DISPLAY_MAP.keys():
            await CLIENT.start_realtime_price(internal, 60)
            
        asyncio.run_coroutine_threadsafe(dynamic_bulk_stream_loop(), ASYNC_LOOP)
    else:
        print(f"❌ Pipeline Failed: {reason}")

if __name__ == '__main__':
    configure_backend_tunnel()
    asyncio.run_coroutine_threadsafe(start_broker_pipeline(), ASYNC_LOOP)
    while True:
        time.sleep(1)
