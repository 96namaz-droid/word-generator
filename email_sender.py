"""
Модуль для отправки email с отчетами
"""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
from pathlib import Path
from typing import Tuple
from logger import app_logger


# Настройки SMTP для list.ru
SMTP_SERVER = "smtp.list.ru"
SMTP_PORT = 587  # TLS
SMTP_PORT_SSL = 465  # SSL альтернатива
EMAIL_FROM = "2728941@list.ru"
EMAIL_TO = "2728941@list.ru"

# Пароль можно задать через переменную окружения EMAIL_PASSWORD
# или через файл .env (если будет использоваться python-dotenv)


def send_report_email(filepath: str, subject: str = None, body: str = None) -> Tuple[bool, str]:
    """
    Отправляет отчет по email
    
    Args:
        filepath: Путь к файлу отчета
        subject: Тема письма (если None - автоматическая)
        body: Текст письма (если None - автоматический)
    
    Returns:
        tuple[bool, str]: (успех, сообщение об ошибке или успехе)
    """
    try:
        # Получаем пароль из переменной окружения
        email_password = os.getenv("EMAIL_PASSWORD")
        if not email_password:
            app_logger.warning("EMAIL_PASSWORD не установлен. Отправка email будет пропущена.")
            return False, "Пароль email не настроен (установите переменную окружения EMAIL_PASSWORD)"
        
        # Проверяем существование файла
        file_path_obj = Path(filepath)
        if not file_path_obj.exists():
            error_msg = f"Файл для отправки не найден: {filepath}"
            app_logger.error(error_msg)
            return False, error_msg
        
        app_logger.info(f"Начало отправки email с файлом: {filepath}")
        
        # Создаем сообщение
        msg = MIMEMultipart()
        msg['From'] = EMAIL_FROM
        msg['To'] = EMAIL_TO
        
        # Тема письма
        if subject is None:
            filename_only = file_path_obj.name
            subject = f"Отчет: {filename_only}"
        msg['Subject'] = subject
        
        # Текст письма
        if body is None:
            body = f"""Здравствуйте!

К вам прикреплен автоматически сгенерированный отчет.

Файл: {file_path_obj.name}
Размер: {file_path_obj.stat().st_size} байт

С уважением,
Система генерации отчетов"""
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # Прикрепляем файл
        with open(filepath, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
        
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename= {file_path_obj.name}'
        )
        msg.attach(part)
        
        # Подключаемся к SMTP серверу и отправляем
        app_logger.info(f"Подключение к SMTP серверу {SMTP_SERVER}:{SMTP_PORT}...")
        
        try:
            # Пробуем TLS сначала
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()  # Включаем TLS
            server.login(EMAIL_FROM, email_password)
            text = msg.as_string()
            server.sendmail(EMAIL_FROM, EMAIL_TO, text)
            server.quit()
            app_logger.info(f"✓ Email успешно отправлен на {EMAIL_TO}")
            return True, f"Отчет успешно отправлен на {EMAIL_TO}"
            
        except Exception as tls_error:
            app_logger.warning(f"TLS соединение не удалось: {tls_error}. Пробую SSL...")
            try:
                # Пробуем SSL как альтернативу
                server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT_SSL)
                server.login(EMAIL_FROM, email_password)
                text = msg.as_string()
                server.sendmail(EMAIL_FROM, EMAIL_TO, text)
                server.quit()
                app_logger.info(f"✓ Email успешно отправлен на {EMAIL_TO} (через SSL)")
                return True, f"Отчет успешно отправлен на {EMAIL_TO}"
            except Exception as ssl_error:
                error_msg = f"Ошибка отправки email (TLS и SSL): TLS={str(tls_error)}, SSL={str(ssl_error)}"
                app_logger.error(error_msg)
                return False, error_msg
        
    except Exception as e:
        error_msg = f"Ошибка при отправке email: {str(e)}"
        app_logger.error(error_msg)
        import traceback
        app_logger.error(traceback.format_exc())
        return False, error_msg

