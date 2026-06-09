#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import threading
import time
import os
import certifi
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# ✅ SSL/TLS স্ট্যাটিক এনভায়রনমেন্ট কনফিগারেশন (Render-এর জন্য)
cert_path = certifi.where()
os.environ['SSL_CERT_FILE'] = cert_path
os.environ['WEBSOCKET_CLIENT_CA_BUNDLE'] = cert_path

try:
    from pyquotex.stable_api import Quotex
except ImportError as e:
    print(f"❌ Error: Missing pyquotex - {e}")
    exit(1)

app = FastAPI(title="Quotex Live Candle API — Render Fully Fixed")

# ✅ CORS পলিসি এনাবল (যাতে ক্লাউডফ্লেয়ার বা ব্রাউজার থেকে রিকোয়েস্ট ব্লক না হয়)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OWNER_INFO = {
    "Owner": "DARK-X-RAYHAN",
    "Telegram": "@mdrayhan85",
    "success": True
}

CLIENT = None
QUOTEX_LOOP = None
CONNECTED_EVENT = threading.Event()

# গ্লোবাল লাইটওয়েট মেমোরি ক্যাশ (র‍্যাম বাঁচানোর জন্য)
CANDLE_CACHE = {}

ASSET_DISPLAY_MAP = {
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
    "XAUUSD": "Gold", "XAUUSD_otc": "Gold (OTC)", "XAGUSD": "Silver", "XAGUSD_otc": "Silver (OTC)",
    "UKBrent_otc": "UK Brent (OTC)", "USCrude_otc": "US Crude (OTC)"
}

# ✅ ক্যান্ডেল ডাটা ওয়াচার (রেন্ডার মেমোরি সেভার)
async def candle_data_watcher():
    while True:
        try:
            if CLIENT and CLIENT.api and hasattr(CLIENT.api, 'candles'):
                raw_candles = CLIENT.api.candles.candles_data
                for asset in list(raw_candles.keys()):
                    data = raw_candles[asset]
                    if data:
                        if isinstance(data, dict):
                            CANDLE_CACHE[asset] = list(data.values())
                        elif isinstance(data, list):
                            CANDLE_CACHE[asset] = list(data)
        except Exception:
            pass
        await asyncio.sleep(1.0)

# ✅ কোটেক্স কানেকশন কোর ইঞ্জিন (ValueError পুরোপুরি ফিক্সড)
def run_quotex_worker():
    global QUOTEX_LOOP, CLIENT
    QUOTEX_LOOP = asyncio.new_event_loop()
    asyncio.set_event_loop(QUOTEX_LOOP)
    
    # 🔐 রেন্ডারের এনভায়রনমেন্ট ভেরিয়েবল থেকে ক্রেডেনশিয়াল রিড করার লজিক
    email = os.environ.get("QUOTEX_EMAIL", "trrayhanislam786@gmail.com")
    password = os.environ.get("QUOTEX_PASSWORD", "Mdrayhan@655")
    
    print("🔐 Render Isolated Engine Connecting...")
    CLIENT = Quotex(email=email, password=password, host="qxbroker.com", lang="en")
    
    try:
        success, reason = QUOTEX_LOOP.run_until_complete(CLIENT.connect())
        if success:
            QUOTEX_LOOP.run_until_complete(CLIENT.change_account("PRACTICE"))
            print("✅ Quotex Connected Successfully on Render!")
            CONNECTED_EVENT.set()
            
            QUOTEX_LOOP.create_task(candle_data_watcher())
            QUOTEX_LOOP.run_forever()
        else:
            print(f"❌ Connection failed: {reason}")
    except Exception as e:
        print(f"❌ Worker Error: {str(e)}")

@app.on_event("startup")
def startup_event():
    threading.Thread(target=run_quotex_worker, daemon=True, name="RenderQuotexCore").start()

@app.get("/api/candles")
def get_candles(
    pair: str = Query("USDMXN_OTC"),
    count: int = Query(1000)
):
    if not CONNECTED_EVENT.is_set() or CLIENT is None or CLIENT.api is None:
        return {**OWNER_INFO, "total_count": 0, "data": [], "message": "Server is waking up/initializing. Please refresh after 5 seconds."}

    input_pair = pair.strip().replace("-", "_")
    target_pair = None
    for k in ASSET_DISPLAY_MAP.keys():
        if k.lower() == input_pair.lower():
            target_pair = k
            break
            
    if not target_pair:
        raise HTTPException(status_code=400, detail=f"Pair '{pair}' is invalid.")

    raw_data = CANDLE_CACHE.get(target_pair, [])
    
    if not raw_data:
        try:
            asyncio.run_coroutine_threadsafe(CLIENT.start_realtime_price(target_pair, 60), QUOTEX_LOOP)
            for _ in range(6):
                time.sleep(0.5)
                raw_data = CANDLE_CACHE.get(target_pair, [])
                if raw_data:
                    break
            
            if not raw_data:
                future = asyncio.run_coroutine_threadsafe(
                    CLIENT.get_candles(asset=target_pair, end_from_time=int(time.time()), offset=count * 60, period=60),
                    QUOTEX_LOOP
                )
                raw_data = future.result(timeout=6)
        except Exception:
            return {**OWNER_INFO, "total_count": 0, "data": [], "message": "Starting asset stream on Render. Please refresh again."}

    if isinstance(raw_data, dict):
        raw_data = list(raw_data.values())

    if not raw_data or not isinstance(raw_data, list):
        return {**OWNER_INFO, "total_count": 0, "data": [], "message": "Data synchronization in progress. Please reload."}

    valid_candles = []
    for c in raw_data:
        if c and isinstance(c, dict) and "time" in c and "open" in c:
            if float(c.get("open", 0)) > 0:
                valid_candles.append(c)

    valid_candles = sorted(valid_candles, key=lambda x: int(float(x.get("time", 0))))

    formatted_data = []
    for i, c in enumerate(valid_candles[-count:]):
        try:
            o = float(c.get("open", 0))
            cl = float(c.get("close", 0))
            ts = int(float(c.get("time", time.time())))
            
            t_str = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(ts + 21600))  # BD Time (UTC+6)
            
            formatted_data.append({
                "id": str(i + 1),
                "pair": target_pair.upper(),
                "market_name": ASSET_DISPLAY_MAP[target_pair],
                "timeframe": "M1",
                "candle_time": t_str,
                "open": str(o),
                "high": str(c.get("high", o)),
                "low": str(c.get("low", o)),
                "close": str(cl),
                "volume": str(c.get("volume", 0)),
                "color": "green" if cl > o else ("red" if cl < o else "doji"),
                "created_at": t_str
            })
        except Exception:
            continue

    return {
        **OWNER_INFO,
        "requested_pair": target_pair,
        "total_count": len(formatted_data),
        "data": formatted_data
    }

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
