"""
Модуль для получения данных о погоде
"""
import requests
from logger import app_logger


class WeatherService:
    """Сервис для получения погодных данных"""
    
    def __init__(self):
        # Координаты Екатеринбурга
        self.city_name = "Екатеринбург"
        self.lat = 56.8389
        self.lon = 60.6057
        
    def get_current_weather(self):
        """
        Получает текущую погоду для Екатеринбурга
        
        Returns:
            dict: {'temperature': float, 'wind_speed': float} или None при ошибке
        """
        # Пробуем несколько источников
        
        # Способ 1: wttr.in (без API ключа)
        result = self._get_from_wttr()
        if result:
            return result
        
        # Способ 2: Open-Meteo (бесплатный, без ключа)
        result = self._get_from_open_meteo()
        if result:
            return result
        
        app_logger.error("Не удалось получить погоду ни из одного источника")
        return None
    
    def _get_from_wttr(self):
        """Получает погоду из wttr.in"""
        try:
            url = f"https://wttr.in/{self.city_name}?format=j1"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                current = data.get('current_condition', [{}])[0]
                
                temperature = float(current.get('temp_C', 0))
                wind_speed = float(current.get('windspeedKmph', 0)) / 3.6  # км/ч в м/с
                
                app_logger.info(f"Погода получена из wttr.in: {temperature}°C, {wind_speed:.1f} м/с")
                
                return {
                    'temperature': round(temperature, 1),
                    'wind_speed': round(wind_speed, 1)
                }
        except Exception as e:
            app_logger.warning(f"Ошибка получения погоды из wttr.in: {e}")
            return None
    
    def _get_from_open_meteo(self):
        """Получает погоду из Open-Meteo API (бесплатный, без ключа)"""
        try:
            url = f"https://api.open-meteo.com/v1/forecast"
            params = {
                'latitude': self.lat,
                'longitude': self.lon,
                'current': 'temperature_2m,wind_speed_10m',
                'timezone': 'Europe/Moscow'
            }
            
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                current = data.get('current', {})
                
                temperature = float(current.get('temperature_2m', 0))
                wind_speed = float(current.get('wind_speed_10m', 0))
                
                app_logger.info(f"Погода получена из Open-Meteo: {temperature}°C, {wind_speed} м/с")
                
                return {
                    'temperature': round(temperature, 1),
                    'wind_speed': round(wind_speed, 1)
                }
        except Exception as e:
            app_logger.warning(f"Ошибка получения погоды из Open-Meteo: {e}")
            return None


# Тестирование при прямом запуске
if __name__ == '__main__':
    service = WeatherService()
    weather = service.get_current_weather()
    
    if weather:
        print(f"Температура: {weather['temperature']}°C")
        print(f"Скорость ветра: {weather['wind_speed']} м/с")
    else:
        print("Не удалось получить данные о погоде")

