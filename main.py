import pandas as pd
import requests
import streamlit as st


API_URL = "https://api.open-meteo.com/v1/forecast"
OSAKA = {"latitude": 34.6937, "longitude": 135.5023}
WEATHER_CODES = {
	0: "快晴",
	1: "おおむね晴れ",
	2: "一部曇り",
	3: "曇り",
	45: "霧",
	48: "着氷性の霧",
	51: "弱い霧雨",
	53: "霧雨",
	55: "強い霧雨",
	56: "弱い着氷性の霧雨",
	57: "強い着氷性の霧雨",
	61: "弱い雨",
	63: "雨",
	65: "強い雨",
	66: "弱い着氷性の雨",
	67: "強い着氷性の雨",
	71: "弱い雪",
	73: "雪",
	75: "強い雪",
	77: "雪粒",
	80: "弱いにわか雨",
	81: "にわか雨",
	82: "強いにわか雨",
	85: "弱いにわか雪",
	86: "強いにわか雪",
	95: "雷雨",
	96: "弱いひょうを伴う雷雨",
	99: "強いひょうを伴う雷雨",
}

WEATHER_GROUPS = {
	0: "晴れ",
	1: "晴れ",
	2: "曇り",
	3: "曇り",
	45: "霧",
	48: "霧",
	51: "雨",
	53: "雨",
	55: "雨",
	56: "雨",
	57: "雨",
	61: "雨",
	63: "雨",
	65: "雨",
	66: "雨",
	67: "雨",
	71: "雪",
	73: "雪",
	75: "雪",
	77: "雪",
	80: "雨",
	81: "雨",
	82: "雨",
	85: "雪",
	86: "雪",
	95: "雷",
	96: "雷",
	99: "雷",
}


def get_weather_group(code):
	return WEATHER_GROUPS.get(code, "その他")


@st.cache_data(ttl=1800)
def get_forecast():
	response = requests.get(
		API_URL,
		params={
			**OSAKA,
			"daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum",
			"timezone": "Asia/Tokyo",
			"forecast_days": 7,
		},
		timeout=15,
	)
	response.raise_for_status()
	return response.json()


st.set_page_config(page_title="大阪の週間天気予報", page_icon="🌤️", layout="centered")
st.title("大阪の週間天気予報")
st.caption("Open-Meteoの予報データを使用しています。")

try:
	forecast = get_forecast()
	daily = forecast["daily"]
	weather = pd.DataFrame(
		{
			"日付": pd.to_datetime(daily["time"]).date,
			"天気区分": [get_weather_group(code) for code in daily["weather_code"]],
			"天気": [WEATHER_CODES.get(code, "不明") for code in daily["weather_code"]],
			"最高気温 (°C)": daily["temperature_2m_max"],
			"最低気温 (°C)": daily["temperature_2m_min"],
			"降水量 (mm)": daily["precipitation_sum"],
		}
	)

	st.dataframe(weather, hide_index=True, use_container_width=True)
	st.subheader("気温の推移")
	chart_data = weather.set_index("日付")[["最高気温 (°C)", "最低気温 (°C)"]]
	st.line_chart(chart_data)
except (requests.RequestException, KeyError, ValueError) as error:
	st.error(f"天気予報を取得できませんでした。時間をおいて再度お試しください。\n\n詳細: {error}")
