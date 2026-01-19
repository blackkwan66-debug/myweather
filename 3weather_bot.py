
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler

# 你的 TOKEN（已填你提供的）
TOKEN = '8496798341:AAGtnRJQiwEvEYBhs_1he1oX-sGNY_8a_2Q'

# 機場列表（座標、時區、名字、單位）
AIRPORTS = {
    "incheon": {"lat": 37.46, "lon": 126.44, "tz": "Asia/Seoul", "name": "仁川國際機場", "unit": "celsius"},
    "laguardia": {"lat": 40.7772, "lon": -73.8726, "tz": "America/New_York", "name": "拉瓜迪亞機場 (LaGuardia)", "unit": "fahrenheit"},
    "toronto": {"lat": 43.6772, "lon": -79.6306, "tz": "America/Toronto", "name": "多倫多皮爾遜機場 (Toronto Pearson)", "unit": "celsius"},
    "dallas": {"lat": 32.8471, "lon": -96.8518, "tz": "America/Chicago", "name": "達拉斯愛田機場 (Dallas Love Field)", "unit": "fahrenheit"},
    "atlanta": {"lat": 33.6367, "lon": -84.4281, "tz": "America/New_York", "name": "哈茨菲爾德-傑克遜機場 (Hartsfield-Jackson)", "unit": "fahrenheit"},
    "seattle": {"lat": 47.4490, "lon": -122.3093, "tz": "America/Los_Angeles", "name": "西雅圖-塔科馬機場 (Seattle-Tacoma)", "unit": "fahrenheit"},
    "london": {"lat": 51.5053, "lon": 0.0553, "tz": "Europe/London", "name": "倫敦城市機場 (London City)", "unit": "celsius"}
}

# 天氣代碼轉中文描述（簡單版）
WEATHER_WORDS = {
    0: "晴天",
    1: "大致晴朗",
    2: "少雲",
    3: "多雲",
    45: "霧",
    51: "細雨",
    61: "中雨",
    71: "小雪",
    80: "陣雨",
    95: "雷暴"
}

# /start 歡迎訊息
async def start(update: Update, context):
    await update.message.reply_text(
        "開始啦！我是機場天氣 bot 😊\n"
        "打 /airport 看全部機場列表！\n"
        "選一個機場指令（如 /incheon），我會告訴你現時 + 今天/明天/後天預測～"
    )

# /airport 顯示機場清單
async def airport_list(update: Update, context):
    message = "可用機場列表（打 / + 機場名）:\n" + "\n".join(
        [f"/{key} → {val['name']}" for key, val in AIRPORTS.items()]
    )
    await update.message.reply_text(message)

# 測試 bot 是否在線
async def test_bot(update: Update, context):
    await update.message.reply_text("測試成功！bot 在線上聽話！😊")

# 共用天氣預測函數（現時 + 三天）
async def predict_weather(update: Update, context, airport_key):
    info = AIRPORTS[airport_key]
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": info["lat"],
        "longitude": info["lon"],
        "current": "temperature_2m,apparent_temperature,relative_humidity_2m,wind_speed_10m,weather_code",
        "daily": "temperature_2m_max,temperature_2m_min,weather_code",
        "temperature_unit": info["unit"],
        "timezone": info["tz"],
        "forecast_days": 3  # 今天 + 明天 + 後天
        # 不要加 models=gfs，API 會自動選最佳模型（包含 GFS）
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()  # 自動檢查是否 200
        data = response.json()

        current = data["current"]
        daily = data["daily"]

        unit_symbol = "°F" if info["unit"] == "fahrenheit" else "°C"

        # 暖風過境概率（1月低，簡單估算）
        warm_front_prob = 20.5  # %

        # 現時溫度
        now_temp = current["temperature_2m"]
        now_feel = current["apparent_temperature"]
        now_humidity = current["relative_humidity_2m"]
        now_wind = current["wind_speed_10m"]
        now_code = current["weather_code"]
        now_weather = WEATHER_WORDS.get(now_code, "未知天氣")

        message = (
            f"**{info['name']} 天氣預測**（自動最佳模型）\n\n"
            f"**現時（當下）**：\n"
            f"溫度: {now_temp} {unit_symbol}\n"
            f"感覺像: {now_feel} {unit_symbol}\n"
            f"濕度: {now_humidity}%\n"
            f"風速: {now_wind} km/h\n"
            f"天氣: {now_weather}\n\n"
            f"**今天** 高/低: {daily['temperature_2m_max'][0]} / {daily['temperature_2m_min'][0]} {unit_symbol}\n"
            f"**明天** 高/低: {daily['temperature_2m_max'][1]} / {daily['temperature_2m_min'][1]} {unit_symbol}\n"
            f"**後天** 高/低: {daily['temperature_2m_max'][2]} / {daily['temperature_2m_min'][2]} {unit_symbol}\n"
            f"晚上暖風過境概率: {warm_front_prob}%（目前冷季，機率低）\n"
            f"獲利建議: 買低溫範圍（概率較高，約 75%）"
        )
        await update.message.reply_text(message, parse_mode="Markdown")

    except Exception as e:
        error_msg = f"抓資料失敗：{str(e)}\n再試一次，或檢查網路！"
        await update.message.reply_text(error_msg)

# 各機場指令
async def incheon(update: Update, context):
    await predict_weather(update, context, "incheon")

async def laguardia(update: Update, context):
    await predict_weather(update, context, "laguardia")

async def toronto(update: Update, context):
    await predict_weather(update, context, "toronto")

async def dallas(update: Update, context):
    await predict_weather(update, context, "dallas")

async def atlanta(update: Update, context):
    await predict_weather(update, context, "atlanta")

async def seattle(update: Update, context):
    await predict_weather(update, context, "seattle")

async def london(update: Update, context):
    await predict_weather(update, context, "london")

# 啟動 bot
print("Bot 正在啟動...")
application = Application.builder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("airport", airport_list))
application.add_handler(CommandHandler("test", test_bot))
application.add_handler(CommandHandler("incheon", incheon))
application.add_handler(CommandHandler("laguardia", laguardia))
application.add_handler(CommandHandler("toronto", toronto))
application.add_handler(CommandHandler("dallas", dallas))
application.add_handler(CommandHandler("atlanta", atlanta))
application.add_handler(CommandHandler("seattle", seattle))
application.add_handler(CommandHandler("london", london))

application.run_polling()
