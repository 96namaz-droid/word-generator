"""
Веб-версия генератора отчётов
FastAPI приложение с адаптивным интерфейсом
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Literal
import sys
import os
from pathlib import Path

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from document_generator import DocumentGenerator
from validator import DataValidator
from weather_service import WeatherService
from contracts_db import ContractsDatabase
from contract_parser import ContractParser
from logger import app_logger
import config

# Инициализация FastAPI
app = FastAPI(title="Генератор отчётов о пожарных лестницах")

# Настройка статических файлов и шаблонов
static_dir = Path(__file__).parent / "web_static"
templates_dir = Path(__file__).parent / "web_templates"

# Создаём директории если не существуют
static_dir.mkdir(exist_ok=True)
templates_dir.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
templates = Jinja2Templates(directory=str(templates_dir))

# Инициализация сервисов
generator = DocumentGenerator()
validator = DataValidator()
weather_service = WeatherService()
contracts_db = ContractsDatabase()


# Модели данных
class LadderData(BaseModel):
    number: int
    name: Optional[str] = ""
    ladder_type: Literal["vertical"] = "vertical"
    height: Optional[str] = ""
    width: Optional[str] = ""
    steps_count: Optional[str] = ""
    mount_points: Optional[str] = ""
    platform_length: Optional[str] = ""
    platform_width: Optional[str] = ""
    fence_height: Optional[str] = ""
    wall_distance: Optional[str] = ""
    ground_distance: Optional[str] = ""
    step_distance: Optional[str] = ""
    # Визуальный осмотр
    damage_found: bool = False
    mount_violation_found: bool = False
    weld_violation_found: bool = False
    paint_compliant: bool = True


class ComplianceData(BaseModel):
    compliant: bool = True
    violations: Dict[str, bool] = {}
    name: Optional[str] = ""


class ReportData(BaseModel):
    date: str
    customer: str
    object_full_address: str
    ladders: List[LadderData]
    test_time: str = "дневное время"
    temperature: Optional[str] = ""
    wind_speed: Optional[str] = ""
    ladders_compliance: Dict[int, ComplianceData] = {}
    project_compliant: bool = False
    project_number: Optional[str] = ""


# API Endpoints
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Главная страница"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/weather")
async def get_weather():
    """Получить текущую погоду для Екатеринбурга"""
    try:
        weather = weather_service.get_current_weather()
        if weather:
            return {"success": True, "data": weather}
        else:
            raise HTTPException(status_code=503, detail="Не удалось получить данные о погоде")
    except Exception as e:
        app_logger.error(f"Ошибка получения погоды: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/customers")
async def get_customers():
    """Получить список заказчиков"""
    try:
        customers = contracts_db.get_all_customers()
        return {"success": True, "customers": customers}
    except Exception as e:
        app_logger.error(f"Ошибка получения заказчиков: {e}")
        return {"success": False, "error": str(e)}


@app.get("/api/contract/{customer}")
async def get_contract(customer: str):
    """Получить данные договора для заказчика"""
    try:
        contract = contracts_db.get_latest_contract_for_customer(customer)
        if contract:
            return {"success": True, "data": contract}
        else:
            return {"success": False, "error": "Договор не найден"}
    except Exception as e:
        app_logger.error(f"Ошибка получения договора: {e}")
        return {"success": False, "error": str(e)}


@app.post("/api/validate")
async def validate_data(data: ReportData):
    """Валидация данных отчёта"""
    try:
        # Конвертируем Pydantic модели в словари
        data_dict = data.model_dump()
        
        # Конвертируем вложенные модели
        data_dict['ladders'] = [ladder.model_dump() if isinstance(ladder, LadderData) else ladder 
                                for ladder in data_dict['ladders']]
        
        data_dict['ladders_compliance'] = {
            k: (v.model_dump() if isinstance(v, ComplianceData) else v)
            for k, v in data_dict.get('ladders_compliance', {}).items()
        }
        
        is_valid, errors = validator.validate_all_data(data_dict)
        
        return {
            "success": True,
            "is_valid": is_valid,
            "errors": errors
        }
    except Exception as e:
        app_logger.error(f"Ошибка валидации: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate")
async def generate_report(data: ReportData):
    """Генерация отчёта"""
    try:
        # Конвертируем Pydantic модели в словари
        data_dict = data.model_dump()
        
        # Конвертируем вложенные модели
        data_dict['ladders'] = [ladder.model_dump() if isinstance(ladder, LadderData) else ladder 
                                for ladder in data_dict['ladders']]
        
        data_dict['ladders_compliance'] = {
            int(k): (v.model_dump() if isinstance(v, ComplianceData) else v)
            for k, v in data_dict.get('ladders_compliance', {}).items()
        }
        
        # Валидация
        is_valid, errors = validator.validate_all_data(data_dict)
        if not is_valid:
            return {
                "success": False,
                "errors": errors
            }
        
        # Генерация документа
        filepath = generator.create_document(data_dict)
        filename = os.path.basename(filepath)
        
        app_logger.info(f"Документ сгенерирован: {filepath}")
        
        return {
            "success": True,
            "filename": filename,
            "filepath": filepath
        }
        
    except Exception as e:
        app_logger.error(f"Ошибка генерации документа: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/download/{filename}")
async def download_report(filename: str):
    """Скачать сгенерированный отчёт"""
    try:
        filepath = config.REPORTS_DIR / filename
        
        if not filepath.exists():
            raise HTTPException(status_code=404, detail="Файл не найден")
        
        return FileResponse(
            path=str(filepath),
            filename=filename,
            media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        
    except Exception as e:
        app_logger.error(f"Ошибка скачивания файла: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/contracts/update")
async def update_contracts():
    """Обновить базу договоров"""
    try:
        if not config.EXTERNAL_CONTRACTS_DIR.exists():
            return {
                "success": False,
                "error": f"Папка с договорами не найдена: {config.EXTERNAL_CONTRACTS_DIR}"
            }
        
        parser = ContractParser(config.EXTERNAL_CONTRACTS_DIR)
        contracts_data = parser.scan_contracts_directory()
        
        if not contracts_data:
            return {
                "success": False,
                "error": "В папке не найдено договоров"
            }
        
        contracts_db.update_contracts(contracts_data)
        stats = contracts_db.get_stats()
        
        app_logger.info(f"База договоров обновлена: {stats}")
        
        return {
            "success": True,
            "stats": stats
        }
        
    except Exception as e:
        app_logger.error(f"Ошибка обновления базы договоров: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@app.get("/api/health")
async def health_check():
    """Проверка работоспособности"""
    return {
        "status": "ok",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    
    app_logger.info("Запуск веб-сервера...")
    print("="*60)
    print("🚀 Веб-версия генератора отчётов")
    print("="*60)
    print(f"📍 Адрес: http://localhost:8000")
    print(f"📱 Откройте этот адрес в браузере на компьютере или телефоне")
    print("="*60)
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

