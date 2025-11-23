"""
Веб-приложение для генерации протоколов
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from urllib.parse import quote
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, ValidationError
from typing import List, Optional, Dict, Any
import os
from pathlib import Path

from document_generator import DocumentGenerator
from validator import DataValidator
from logger import app_logger
from contracts_db import ContractsDatabase
from history_manager import HistoryManager
from weather_service import WeatherService
import config

app = FastAPI(title="Генератор протоколов")

# Обработчик ошибок валидации Pydantic
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """Обработка ошибок валидации Pydantic"""
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        msg = error["msg"]
        errors.append(f"{field}: {msg}")
    
    app_logger.error(f"Ошибка валидации Pydantic: {errors}")
    return JSONResponse(
        status_code=422,
        content={"detail": errors, "errors": errors}
    )

# Настройка статических файлов и шаблонов
static_dir = Path(__file__).parent / "web_static"
templates_dir = Path(__file__).parent / "web_templates"

if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

templates = Jinja2Templates(directory=str(templates_dir))

# Инициализация сервисов
contracts_db = ContractsDatabase()
history_manager = HistoryManager()
weather_service = WeatherService()

# Модели данных
class LadderData(BaseModel):
    number: int
    name: Optional[str] = ""
    height: str
    width: str
    steps_count: str
    mount_points: str
    platform_length: Optional[str] = ""
    platform_width: Optional[str] = ""
    fence_height: Optional[str] = ""
    wall_distance: Optional[str] = ""
    ground_distance: Optional[str] = ""
    step_distance: str
    damage_found: bool = False
    mount_violation_found: bool = False
    weld_violation_found: bool = False
    paint_compliant: bool = True

class MarchData(BaseModel):
    number: int
    has_march: bool = True
    has_platform: bool = True
    march_width: Optional[str] = ""
    march_length: Optional[str] = ""
    step_width: Optional[str] = ""
    step_distance: Optional[str] = ""
    steps_count: Optional[str] = ""
    march_fence_height: Optional[str] = ""
    platform_length: Optional[str] = ""
    platform_width: Optional[str] = ""
    platform_fence_height: Optional[str] = ""
    platform_ground_distance: Optional[str] = ""

class ReportData(BaseModel):
    protocol_type: str = "vertical"
    date: str
    customer: str
    object_full_address: str
    test_time: str = "дневное время"
    temperature: Optional[str] = ""
    wind_speed: Optional[str] = ""
    
    # Для вертикальных лестниц
    ladders: List[LadderData] = []
    ladders_compliance: Dict[str, Any] = {}
    
    # Для маршевых лестниц
    ladder_name: Optional[str] = ""
    mount_points: Optional[str] = ""
    marches: List[MarchData] = []
    
    # Для ограждений кровли
    fence_name: Optional[str] = ""
    length: Optional[str] = ""
    height: Optional[str] = ""
    mount_points_roof: Optional[str] = ""
    mount_pitch: Optional[str] = ""
    parapet_height: Optional[str] = ""
    
    # Визуальный осмотр (для маршевых и ограждений)
    damage_found: bool = False
    mount_violation_found: bool = False
    weld_violation_found: bool = False
    paint_compliant: bool = True
    
    # Соответствие нормам
    project_compliant: bool = False
    project_number: Optional[str] = ""


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Главная страница"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/customers")
async def get_customers():
    """Получение списка заказчиков"""
    try:
        # Получаем заказчиков из разных источников
        recent_customers = history_manager.get_recent_customers()
        db_customers = contracts_db.get_all_customers()
        
        # Объединяем все списки, убираем дубликаты и сортируем
        all_customers = list(set(config.DEFAULT_CUSTOMERS + recent_customers + db_customers))
        all_customers.sort()
        
        return {"customers": all_customers}
    except Exception as e:
        app_logger.error(f"Ошибка получения списка заказчиков: {e}")
        return {"customers": config.DEFAULT_CUSTOMERS}


@app.get("/api/customer/{customer_name}")
async def get_customer_contract(customer_name: str):
    """Получение договора по заказчику для автозаполнения"""
    try:
        contract = contracts_db.get_latest_contract_for_customer(customer_name)
        if contract:
            return {
                "found": True,
                "object_full_address": contract.get('object_full_address', ''),
                "file_name": contract.get('file_name', '')
            }
        return {"found": False, "object_full_address": ""}
    except Exception as e:
        app_logger.error(f"Ошибка получения договора: {e}")
        return {"found": False, "object_full_address": ""}


@app.get("/api/weather")
async def get_weather():
    """Получение текущей погоды"""
    try:
        weather = weather_service.get_current_weather()
        if weather:
            return {
                "success": True,
                "temperature": weather['temperature'],
                "wind_speed": weather['wind_speed']
            }
        return {
            "success": False,
            "message": "Не удалось получить данные о погоде"
        }
    except Exception as e:
        app_logger.error(f"Ошибка получения погоды: {e}")
        return {
            "success": False,
            "message": str(e)
        }


@app.post("/api/validate")
async def validate_data(data: ReportData):
    """Валидация данных"""
    try:
        app_logger.info(f"=== ВАЛИДАЦИЯ ДАННЫХ ===")
        app_logger.info(f"Тип протокола: {data.protocol_type}")
        
        # Преобразуем Pydantic модель в dict
        data_dict = data.model_dump()
        
        # Преобразуем ladders и marches в нужный формат
        if data.protocol_type == "vertical":
            app_logger.info(f"Валидация вертикальных лестниц: {len(data.ladders)} лестниц")
            data_dict["ladders"] = [l.model_dump() for l in data.ladders]
            # Для вертикальных лестниц нужны данные соответствия
            if not data_dict.get("ladders_compliance"):
                data_dict["ladders_compliance"] = {}
        elif data.protocol_type == "stair":
            app_logger.info(f"Валидация маршевых лестниц: {len(data.marches)} маршей")
            data_dict["marches"] = [m.model_dump() for m in data.marches]
            data_dict["mount_points"] = data.mount_points
        elif data.protocol_type == "roof":
            app_logger.info(f"Валидация ограждений кровли")
            data_dict["mount_points"] = data.mount_points_roof
        
        # Валидация
        app_logger.info("Вызов DataValidator.validate_all_data...")
        is_valid, errors = DataValidator.validate_all_data(data_dict)
        
        app_logger.info(f"Результат валидации: valid={is_valid}, errors={len(errors)}")
        if errors:
            app_logger.warning(f"Ошибки валидации: {errors}")
        
        return {
            "valid": is_valid,
            "errors": errors
        }
    except Exception as e:
        import traceback
        error_msg = f"Ошибка валидации: {str(e)}\n{traceback.format_exc()}"
        app_logger.error(error_msg)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate")
async def generate_report(data: ReportData):
    """Генерация отчёта"""
    try:
        app_logger.info(f"=== ЗАПРОС НА ГЕНЕРАЦИЮ ===")
        app_logger.info(f"Тип протокола: {data.protocol_type}")
        app_logger.info(f"Дата: {data.date}")
        app_logger.info(f"Заказчик: {data.customer}")
        app_logger.info(f"Объект: {data.object_full_address}")
        
        # Преобразуем Pydantic модель в dict
        data_dict = data.model_dump()
        
        # Преобразуем ladders и marches в нужный формат
        if data.protocol_type == "vertical":
            app_logger.info(f"Обработка вертикальных лестниц...")
            app_logger.info(f"Получено лестниц: {len(data.ladders)}")
            data_dict["ladders"] = [l.model_dump() for l in data.ladders]
            
            # Логируем данные каждой лестницы
            for idx, ladder in enumerate(data_dict["ladders"], 1):
                app_logger.info(f"  Лестница {idx}: name={ladder.get('name')}, height={ladder.get('height')}, width={ladder.get('width')}")
            
            # Для вертикальных лестниц нужны данные соответствия
            if not data_dict.get("ladders_compliance"):
                data_dict["ladders_compliance"] = {}
            app_logger.info(f"Вертикальные лестницы обработаны: {len(data_dict['ladders'])} лестниц")
        elif data.protocol_type == "stair":
            app_logger.info(f"Обработка маршевых лестниц...")
            app_logger.info(f"Получено маршей: {len(data.marches)}")
            data_dict["marches"] = [m.model_dump() for m in data.marches]
            data_dict["mount_points"] = data.mount_points
            app_logger.info(f"Маршевые лестницы обработаны: {len(data_dict['marches'])} маршей")
        elif data.protocol_type == "roof":
            app_logger.info(f"Обработка ограждений кровли...")
            data_dict["mount_points"] = data.mount_points_roof
            app_logger.info(f"Ограждения кровли: длина={data_dict.get('length')}, высота={data_dict.get('height')}")
        
        # Валидация перед генерацией
        app_logger.info("=== НАЧАЛО ВАЛИДАЦИИ ===")
        is_valid, errors = DataValidator.validate_all_data(data_dict)
        if not is_valid:
            app_logger.error(f"Валидация не пройдена. Ошибки: {errors}")
            raise HTTPException(status_code=400, detail={"errors": errors})
        
        app_logger.info("Валидация пройдена успешно ✓")
        
        # Генерация документа
        app_logger.info("=== НАЧАЛО ГЕНЕРАЦИИ ДОКУМЕНТА ===")
        app_logger.info(f"Создание DocumentGenerator...")
        generator = DocumentGenerator()
        app_logger.info("Генератор создан, вызов create_document...")
        app_logger.info(f"Передаваемые данные в create_document: protocol_type={data_dict.get('protocol_type')}")
        
        try:
            filepath = generator.create_document(data_dict)
            app_logger.info(f"✓ create_document вернул путь: {filepath}")
        except Exception as gen_error:
            import traceback
            app_logger.error(f"ОШИБКА в create_document: {str(gen_error)}")
            app_logger.error(f"Traceback:\n{traceback.format_exc()}")
            raise
        
        
        app_logger.info(f"Документ успешно создан: {filepath}")
        
        # Проверяем существование файла
        file_path_obj = Path(filepath)
        if not file_path_obj.exists():
            app_logger.error(f"Файл не найден после генерации: {filepath}")
            raise HTTPException(status_code=500, detail="Файл не был создан")
        
        app_logger.info(f"Размер файла: {file_path_obj.stat().st_size} байт")
        filename = os.path.basename(filepath)
        app_logger.info(f"Имя файла для скачивания: {filename}")
        
        # Отправляем отчет на email в фоне (не блокируем ответ)
        try:
            from email_sender import send_report_email
            app_logger.info("Попытка отправки отчета на email...")
            
            # Формируем тему и текст письма
            email_subject = f"Отчет: {data.customer} - {data.date}"
            email_body = f"""Здравствуйте!

Автоматически сгенерирован новый отчет:

Дата: {data.date}
Заказчик: {data.customer}
Объект: {data.object_full_address}
Тип протокола: {data.protocol_type}

Файл прикреплен к письму.

С уважением,
Система генерации отчетов"""
            
            email_success, email_message = send_report_email(
                str(file_path_obj),
                subject=email_subject,
                body=email_body
            )
            
            if email_success:
                app_logger.info(f"✓ {email_message}")
            else:
                app_logger.warning(f"⚠ Не удалось отправить email: {email_message}")
                # Не прерываем генерацию, если email не отправился
        except Exception as email_error:
            app_logger.warning(f"Ошибка при попытке отправки email (игнорируется): {email_error}")
            # Не прерываем генерацию, если email не отправился
        
        # Правильное кодирование имени файла для Content-Disposition (RFC 5987)
        # Используем оба формата: старый (для совместимости) и новый (RFC 5987)
        # Для имен с кириллицей используем RFC 5987
        if any(ord(c) > 127 for c in filename):
            # Файл содержит не-ASCII символы - используем RFC 5987
            encoded_filename = quote(filename, safe='')
            content_disposition = f'attachment; filename="{filename}"; filename*=UTF-8\'\'{encoded_filename}'
        else:
            # Только ASCII символы - используем простой формат
            content_disposition = f'attachment; filename="{filename}"'
        
        app_logger.info(f"Content-Disposition: {content_disposition}")
        
        # Возвращаем файл
        return FileResponse(
            str(file_path_obj),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=filename,
            headers={
                "Content-Disposition": content_disposition,
                "Content-Type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            }
        )
    except HTTPException:
        raise
    except ValueError as e:
        # Ошибки валидации генератора
        app_logger.error(f"Ошибка валидации генератора: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        error_msg = f"Ошибка генерации: {str(e)}\n{traceback.format_exc()}"
        app_logger.error(error_msg)
        # Возвращаем более подробную информацию об ошибке
        raise HTTPException(
            status_code=500, 
            detail={
                "error": str(e),
                "type": type(e).__name__
            }
        )


if __name__ == "__main__":
    import uvicorn
    config.ensure_directories()
    uvicorn.run(app, host="0.0.0.0", port=8000)

