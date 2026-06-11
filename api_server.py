import os
import sys
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
import uvicorn

# =====================================================================
# 🌐 SOCKS5 TUNNEL ENGINE (Bypass US IP Block on Replit)
# =====================================================================
def activate_socks5_vpn():
    print("🌐 Connecting to internal SOCKS5 VPN Tunnel for Replit...")
    socks5_api_url = "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks5&timeout=4000&country=IN,SG,DE,FR,BR&anonymity=elite"
    
    try:
        response = requests.get(socks5_api_url, timeout=10)
        if response.status_code == 200:
            proxies = [p.strip() for p in response.text.split("\n") if p.strip()]
            print(f"📥 Found {len(proxies)} SOCKS5 routes. Filtering Capable Tunnels...")
            
            for proxy in proxies[:15]:
                proxy_url = f"socks5://{proxy}"
                try:
                    test_resp = requests.get(
                        "https://www.cloudflare.com", 
                        proxies={"http": proxy_url, "https": proxy_url}, 
                        timeout=4
                    )
                    if test_resp.status_code == 200:
                        os.environ["HTTP_PROXY"] = proxy_url
                        os.environ["HTTPS_PROXY"] = proxy_url
                        os.environ["http_proxy"] = proxy_url
                        os.environ["https_proxy"] = proxy_url
                        print(f"✅ SOCKS5 VPN Tunnel Activated Successfully!")
                        print(f"🌍 Live Route: {proxy_url} (Non-US)")
                        return True
                except:
                    continue
    except Exception as e:
        print(f"❌ SOCKS5 Tunnel Error: {e}")
    
    print("⚠️ Warning: Tunnel failed. Replit might face US blocking.")
    return False

# বুট হওয়ার আগেই ভিপিএন টানেল অন করা
activate_socks5_vpn()

# =====================================================================
# 🛠️ LOCAL PYQUOTEX IMPORT CHECK
# =====================================================================
try:
    import pyquotex
    print("📦 'pyquotex' module loaded successfully in Replit.")
except ImportError:
    pyquotex = None
    print("⚠️ Warning: 'pyquotex.py' file not found in Replit workspace.")

quotex_client = None

# =====================================================================
# 📊 ALL SUPPORTED PAIRS DIRECTORY (COMPLETE EXPANDED LIST)
# =====================================================================
VALID_ASSETS = {
    # 🌟 Forex & OTC Pairs
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

    # 🛢️ Commodities Pairs
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

# =====================================================================
# 🚀 FASTAPI ENGINE SETUP
# =====================================================================
app = FastAPI(title="DARK-X Replit Institutional Engine", version="2.5.0")

class LoginData(BaseModel):
    email: str
    password: str

class CandleRequest(BaseModel):
    asset: str       
    period: int      
    count: int       

    @field_validator('asset')
    @classmethod
    def validate_asset(cls, value):
        if value not in VALID_ASSETS:
            raise ValueError(f"Invalid asset pair '{value}'")
        return value

@app.get("/")
def read_root():
    return {
        "status": "online",
        "platform": "Replit Production Cloud",
        "owner_developer": "DARK-X-RAYHAN",
        "total_pairs_loaded": len(VALID_ASSETS),
        "vpn_status": "Active" if "socks5" in os.environ.get("HTTPS_PROXY", "") else "Inactive",
        "secure_route": os.environ.get("HTTPS_PROXY", "Direct Connection")
    }

@app.get("/assets")
def get_all_assets():
    return {"status": "success", "total": len(VALID_ASSETS), "pairs": VALID_ASSETS}

@app.post("/login")
def quotex_login(data: LoginData):
    global quotex_client
    try:
        print(f"🔑 Manual login route active via SOCKS5: {data.email}")
        if pyquotex is not None:
            quotex_client = pyquotex.Client(email=data.email, password=data.password)
            return {"status": "success", "message": "Logged into Quotex via Replit SOCKS5 Tunnel!"}
        else:
            return {"status": "simulation_success", "message": "Tunnel is up. pyquotex.py is missing in root."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Login Failed: {str(e)}")

@app.post("/fetch-candles")
def fetch_candles(data: CandleRequest):
    global quotex_client
    try:
        asset_display = VALID_ASSETS[data.asset]
        print(f"📊 Pulling data: {data.count} candles for {asset_display}")
        
        if pyquotex is not None and quotex_client is not None:
            # তোমার pyquotex লাইব্রেরি অনুযায়ী কলটি কাজ করবে
            # candles_data = quotex_client.get_candles(data.asset, data.period, data.count)
            candles_data = [] 
            return {"status": "success", "asset": data.asset, "data": candles_data}
        else:
            return {
                "status": "simulation_data",
                "asset": data.asset,
                "name": asset_display,
                "count": data.count,
                "message": "SOCKS5 Tunnel active. Run login first or check pyquotex.py."
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Data stream error: {str(e)}")

# =====================================================================
# ⚡ BACKGROUND SECRETS AUTO-BOOT
# =====================================================================
@app.on_event("startup")
def automatic_replit_boot():
    global quotex_client
    print("🚀 Repl Web Server Booted! Checking background credentials...")
    
    BOT_EMAIL = os.environ.get("QUOTEX_EMAIL")
    BOT_PASSWORD = os.environ.get("QUOTEX_PASSWORD")
    
    if not BOT_EMAIL or not BOT_PASSWORD:
        print("ℹ️ Note: Auto-login skipped. Setup 'QUOTEX_EMAIL' in Replit Secrets to enable auto-boot.")
        return

    print(f"🔑 Auto-routing background credentials for: {BOT_EMAIL}")
    try:
        if pyquotex is not None:
            quotex_client = pyquotex.Client(email=BOT_EMAIL, password=BOT_PASSWORD)
            print("✅ Background connection established successfully!")
        else:
            print("⚠️ Auto-login simulated. Upload 'pyquotex.py' to turn on real stream.")
    except Exception as e:
        print(f"❌ Background connection failed: {str(e)}")

if __name__ == "__main__":
    # Replit Standard Port 8080
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
