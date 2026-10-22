import logging

import requests


logger = logging.getLogger("weather")


CITY = "Montes Claros"


LATITUDE = -16.735


LONGITUDE = -43.86167


FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


WEATHER_CODES = {
    0: "céu limpo",
    1: "predominantemente limpo",
    2: "parcialmente nublado",
    3: "nublado",
    45: "neblina",
    48: "neblina",
    51: "garoa fraca",
    53: "garoa",
    55: "garoa forte",
    61: "chuva fraca",
    63: "chuva",
    65: "chuva forte",
    80: "pancadas de chuva fracas",
    81: "pancadas de chuva",
    82: "pancadas de chuva fortes",
    95: "trovoada",
    96: "trovoada com granizo",
    99: "trovoada com granizo",
}


def describe_code(code):
    return WEATHER_CODES.get(code, "tempo indefinido")


def fetch_forecast():
    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "current": "temperature_2m,weather_code",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max",
        "timezone": "America/Sao_Paulo",
        "forecast_days": 1,
    }
    try:
        response = requests.get(FORECAST_URL, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as error:
        logger.error(f"Falha ao buscar o clima: {error}")
        return None


def format_weather(data):
    current = data["current"]
    daily = data["daily"]
    temperature = current["temperature_2m"]
    description = describe_code(current["weather_code"])
    minimum = daily["temperature_2m_min"][0]
    maximum = daily["temperature_2m_max"][0]
    rain = daily["precipitation_probability_max"][0]

    lines = [
        f"Agora em {CITY}: {temperature:.0f}°C, {description}.",
        f"Hoje: mínima de {minimum:.0f}°C e máxima de {maximum:.0f}°C.",
        f"Chance de chuva: {rain}%.",
    ]
    if rain >= 60:
        lines.append("☔ Leva guarda-chuva!")
    elif rain >= 30:
        lines.append("🌦️ Pode chover, fica de olho.")
    else:
        lines.append("☀️ Sem sinal de chuva.")
    if maximum >= 32:
        lines.append("🥵 Vai fazer calor, bebe água!")
    return "\n  ".join(lines)


def tell_weather(text):
    data = fetch_forecast()
    if data is None:
        return "Não consegui ver o clima agora. Confere se a internet está funcionando."
    return format_weather(data)
