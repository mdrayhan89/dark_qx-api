#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import threading
import time
import os
import certifi
from fastapi import FastAPI, Query, HTTPException
import uvicorn

# ✅ SSL/TLS কনফিগারেশন (আপনার live_chart_27.py এর হুবহু কপি)
cert_path = certifi.where()
os.environ['SSL_CERT_FILE'] = cert_path
os.environ['WEBSOCKET_CLIENT_CA_BUNDLE'] = cert_path

try:
    from pyquotex.stable_api import Quotex
except ImportError as e:
    print(f"❌ Error: Missing pyquotex - {e}")
    exit(1)

app = FastAPI(title="Quotex Live Candle API — Hybrid Thread Cache Version")

OWNER_INFO = {
    "Owner": "DARK-X-RAYHAN",
    "Telegram": "@mdrayhan85",
    "success": True
}

# ✅ গ্লোবাল স্টেট এবং থ্রেড-সেফ ক্যাশ ডিকশনারি
CLIENT = None
QUOTEX_LOOP = None
CONNECTED_EVENT = threading.Event()
CANDLE_CACHE = {}  # এটি প্রতিটি পেয়ারের ক্যান্ডেল মেমোরিতে সেফ রাখবে

# অল সাপোর্টেড পেয়ার ডিরেক্টরি
ASSET_DISPLAY_MAP = {
    # Forex & OTC Pairs
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

    # Crypto Pairs
    "ADAUSD_otc": "Cardano (OTC)", "APTUSD_otc": "Aptos (OTC)", "ARBUSD_otc": "Arbitrum (OTC)", "ATOUSD_otc": "ATO (OTC)",
    "AVAUSD_otc": "Avalanche (OTC)", "AXSUSD_otc": "Axie Infinity (OTC)", "BCHUSD_otc": "Bitcoin Cash (OTC)",
    "BNBUSD_otc": "Binance Coin (OTC)", "BONUSD_otc": "Bonk (OTC)", "BTCUSD_otc": "Bitcoin (OTC)", "DASUSD_otc": "Dash (OTC)",
    "DOGUSD_otc": "Dogecoin (OTC)", "DOTUSD_otc": "Polkadot (OTC)", "ETCUSD_otc": "Ethereum Classic (OTC)",
    "ETHUSD_otc": "Ethereum (OTC)", "FLOUSD_otc": "Floki (OTC)", "GALUSD_otc": "Gala (OTC)", "HMSUSD_otc": "Hamster Kombat (OTC)",
    "LINUSD_otc": "Chainlink (OTC)", "LTCUSD_otc": "Litecoin (OTC)", "MELUSD_otc": "Melania Meme (OTC)",
    "SHIBUSD_otc": "Shiba Inu (OTC)", "SOLUSD_otc": "Solana (OTC)", "TIAUSD_otc": "Celestia (OTC)", "TONUSD_otc": "Toncoin (OTC)",
    "TRUUSD_otc": "TrueFi (OTC)", "TRXUSD_otc": "TRON (OTC)", "WIFUSD_otc": "Dogwifhat (OTC)", "XRPUSD_otc": "Ripple (OTC)",
    "ZECUSD_otc": "Zcash (OTC)",

    # Commodities Pairs
    "XAUUSD": "Gold", "XAUUSD_otc": "Gold (OTC)", "XAGUSD": "Silver", "XAGUSD_otc": "Silver (OTC)",
    "UKBrent_otc": "UK Brent (OTC)", "USCrude_otc": "US Crude (OTC)",

    # Stocks Pairs
    "AXP_otc": "American Express (OTC)", "BA_otc": "Boeing Company (OTC)", "FB_otc": "Facebook (OTC)",
    "INTC_otc": "Intel (OTC)", "JNJ_otc": "Johnson & Johnson (OTC)", "MCD_otc": "McDonald's (OTC)",
    "MSFT_otc": "Microsoft (OTC)", "PFE_otc": "Pfizer Inc (OTC)", "PEPUSD_otc": "PepsiCo (OTC)",

    # Indices Pairs
    "DJIUSD": "Dow Jones", "NDXUSD": "NASDAQ 100", "F40EUR": "CAC 40", "FTSGBP": "FTSE 100",
    "HSIHKD": "Hong Kong 50", "IBXEUR": "IBEX 35", "JPXJPY": "Nikkei 225", "CHIA50": "China A50",
    "STXEUR": "EURO STOXX 50"
}

# ✅ ক্যান্ডেল ডাটা ব্যাকগ্রাউন্ডে সিঙ্ক রাখার জন্য ডেডিকেটেড ওয়াচার (হুবহু live_chart_27 এর লজিক)
async def candle_data_watcher():
    print("📢 Live Candle Cache Synchronizer Started...")
    while True:
        try:
            if CLIENT and CLIENT.api and hasattr(CLIENT.api, 'candles'):
                # পাইকোটেক্সের ইন্টারনাল মেমোরি থেকে ডাটা আমাদের গ্লোবাল ক্যাশে কপি করা হচ্ছে
                raw_candles = CLIENT.api.candles.candles_data
                for asset, data in raw_candles.items():
                    if data:
                        if isinstance(data, dict):
                            CANDLE_CACHE[asset] = list(data.values())
                        elif isinstance(data, list):
                            CANDLE_CACHE[asset] = data
        except Exception as e:
            pass
        await asyncio.sleep(0.5)  # প্রতি ৫০০ মিলি-সেকেন্ডে ইন্টারনাল মেমোরি রিফ্রেশ করবে

# ✅ ব্যাকগ্রাউন্ড থ্রেড ম্যানেজার (FastAPI এর লুপ থেকে এটি সম্পূর্ণ আলাদা থাকবে)
def run_quotex_worker():
    global QUOTEX_LOOP, CLIENT
    QUOTEX_LOOP = asyncio.new_event_loop()
    asyncio.set_event_loop(QUOTEX_LOOP)
    
    email = "trrayhanislam786@gmail.com"
    password = "Mdrayhan@655"
    
    print("🔐 Isolated Background Thread-এ Quotex লগইন করা হচ্ছে...")
    CLIENT = Quotex(email=email, password=password, host="qxbroker.com", lang="en")
    
    success, reason = QUOTEX_LOOP.run_until_complete(CLIENT.connect())
    if success:
        QUOTEX_LOOP.run_until_complete(CLIENT.change_account("PRACTICE"))
        print("✅ Quotex কানেকশন সফল! ব্যাকগ্রাউন্ড থ্রেড নিরাপদভাবে রানিং।")
        CONNECTED_EVENT.set()
        
        # ডাটা সিঙ্কার টাস্কটি ব্যাকগ্রাউন্ড লুপে পুশ করা হলো
        QUOTEX_LOOP.create_task(candle_data_watcher())
        QUOTEX_LOOP.run_forever()
    else:
        print(f"❌ কানেকশন ব্যর্থ হয়েছে: {reason}")

# সার্ভার স্টার্ট হওয়ার সাথে সাথে থ্রেড রান করবে
@app.on_event("startup")
def startup_event():
    threading.Thread(target=run_quotex_worker, daemon=True, name="QuotexCoreEngine").start()

@app.get("/api/candles")
def get_candles(
    pair: str = Query("USDMXN_OTC"),
    count: int = Query(1000)
):
    # উডকর্ন লকিং এড়াতে এই এন্ডপয়েন্টটি সিঙ্ক্রোনাস (def) রাখা হয়েছে
    if not CONNECTED_EVENT.is_set():
        raise HTTPException(status_code=503, detail="Quotex Client is initializing, please wait 5 seconds...")

    input_pair = pair.strip().replace("-", "_")
    target_pair = None
    for k in ASSET_DISPLAY_MAP.keys():
        if k.lower() == input_pair.lower():
            target_pair = k
            break
            
    if not target_pair:
        raise HTTPException(status_code=400, detail=f"Pair '{pair}' টি সঠিক নয়।")

    raw_data = CANDLE_CACHE.get(target_pair, [])
    
    # যদি মেমোরি ক্যাশে ডাটা না থাকে (১ম বার পেয়ার কল করলে), তবে রিয়েলটাইম স্ট্রিম পুশ করবে
    if not raw_data:
        try:
            # থ্রেড-সেফ উপায়ে ব্যাকগ্রাউন্ড লুপে রিয়েলটাইম প্রাইস ট্রিম অন করা হচ্ছে
            asyncio.run_coroutine_threadsafe(CLIENT.start_realtime_price(target_pair, 60), QUOTEX_LOOP)
            
            # সকেট কানেকশন এস্টাবলিশ হয়ে ক্যাশে ডাটা আসার জন্য ১.৫ সেকেন্ড হোল্ড করবে (মেইন লুপ জ্যাম ছাড়া)
            for _ in range(3):
                time.sleep(0.5)
                raw_data = CANDLE_CACHE.get(target_pair, [])
                if raw_data:
                    break
            
            # ব্যাকআপ হিস্টোরি কল (যদি সকেট ডাটা রিফ্লেক্ট হতে সামান্য লেট করে)
            if not raw_data:
                future = asyncio.run_coroutine_threadsafe(
                    CLIENT.get_candles(asset=target_pair, end_from_time=int(time.time()), offset=count * 60, period=60),
                    QUOTEX_LOOP
                )
                raw_data = future.result(timeout=6)
        except Exception:
            return {**OWNER_INFO, "total_count": 0, "data": [], "message": "Initializing pair stream. Please refresh in 2 seconds."}

    if isinstance(raw_data, dict):
        raw_data = list(raw_data.values())

    if not raw_data or not isinstance(raw_data, list):
        return {**OWNER_INFO, "total_count": 0, "data": [], "message": "Market data is loading. Please refresh."}

    # ডাটা ভ্যালিডেশন এবং ক্লিনিং (০ ক্যান্ডেল বাগ পুরোপুরি ফিক্সড)
    valid_candles = []
    for c in raw_data:
        if c and isinstance(c, dict) and "time" in c and "open" in c:
            if float(c.get("open", 0)) > 0:
                valid_candles.append(c)

    # ক্যান্ডেলগুলোকে ক্রনোলজিক্যাল অর্ডারে সর্ট করা (ওল্ড থেকে নিউ)
    valid_candles = sorted(valid_candles, key=lambda x: int(float(x.get("time", 0))))

    formatted_data = []
    for i, c in enumerate(valid_candles[-count:]):
        try:
            o = float(c.get("open", 0))
            cl = float(c.get("close", 0))
            ts = int(float(c.get("time", time.time())))
            
            # বাংলাদেশ সময় ফরম্যাট (UTC+6)
            t_str = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(ts + 21600))
            
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
    uvicorn.run(app, host="0.0.0.0", port=8000)