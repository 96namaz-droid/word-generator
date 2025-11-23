"""
Скрипт запуска веб-версии приложения
"""
import uvicorn
import config

if __name__ == "__main__":
    config.ensure_directories()
    print("=" * 50)
    print("Запуск веб-версии генератора протоколов")
    print("=" * 50)
    print("\nВеб-интерфейс доступен по адресу:")
    print("  http://localhost:8000")
    print("\nДля доступа с других устройств в локальной сети:")
    print("  http://<IP_адрес_компьютера>:8000")
    print("\nДля остановки нажмите Ctrl+C")
    print("=" * 50)
    print()
    
    uvicorn.run(
        "web_app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

