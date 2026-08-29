"""
SanEpi AI — точка входа.
С логированием всех событий и ошибок.

Запуск:
    python app.py            — графический интерфейс
    python app.py --console  — консольное меню
"""
import sys
import os
import logging
from datetime import datetime
from pathlib import Path

# ============================================================
# НАСТРОЙКА ЛОГИРОВАНИЯ
# ============================================================
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / f"app_{datetime.now().strftime('%Y%m%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),  # Логи в файл
        logging.StreamHandler(sys.stdout),                # Логи в консоль
    ],
)

logger = logging.getLogger("SAQSHY")


def log_system_info():
    """Записать информацию о системе в лог."""
    logger.info("=" * 60)
    logger.info("SAQSHY SanEpi — Запуск приложения")
    logger.info("=" * 60)
    logger.info(f"Python версия: {sys.version}")
    logger.info(f"Платформа: {sys.platform}")
    logger.info(f"Рабочая директория: {Path.cwd()}")
    logger.info(f"Файл логов: {LOG_FILE}")
    logger.info("=" * 60)


def run_console():
    """Консольный режим."""
    logger.info("Запуск в КОНСОЛЬНОМ режиме")
    
    try:
        from modules.ai_assistant import ask_ai
        from modules.document_manager import DocumentManager

        document_manager = DocumentManager()
        logger.info("Модули консольного режима загружены")

        while True:
            print("\n" + "=" * 60)
            print("SanEpi AI")
            print("=" * 60)
            print("1. Добавить приказ вручную")
            print("2. Задать вопрос AI")
            print("3. Выход")

            choice = input("\nВыберите пункт: ").strip()
            logger.info(f"Пользователь выбрал: {choice}")

            if choice == "1":
                try:
                    result = document_manager.add_pdf()
                    print()
                    print(result["message"])
                    logger.info("Приказ добавлен вручную")
                except Exception as e:
                    logger.error(f"Ошибка при добавлении приказа: {e}", exc_info=True)
                    import traceback
                    traceback.print_exc()

            elif choice == "2":
                question = input("Введите вопрос: ").strip()
                if question:
                    logger.info(f"Вопрос к AI: {question}")
                    try:
                        result = ask_ai(question)
                        print()
                        print(result["answer"])
                    except Exception as e:
                        logger.error(f"Ошибка AI: {e}", exc_info=True)
                        print("❌ Ошибка при запросе к AI")

            elif choice == "3":
                logger.info("Выход из консольного режима")
                print("Выход из SanEpi AI.")
                break

            else:
                logger.warning(f"Неверный пункт меню: {choice}")
                print("Неверный пункт. Попробуйте снова.")

    except Exception as e:
        logger.critical(f"Критическая ошибка в консольном режиме: {e}", exc_info=True)
        raise


def run_gui():
    """Графический режим."""
    logger.info("Запуск в ГРАФИЧЕСКОМ режиме")
    
    try:
        from modules.main_window import start_main_window
        logger.info("Модуль main_window импортирован")
        start_main_window()
    except ImportError as e:
        logger.critical(f"Не удалось импортировать main_window: {e}", exc_info=True)
        print(f"❌ Критическая ошибка: не найден модуль main_window\n{e}")
        input("Нажмите Enter для выхода...")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"Критическая ошибка GUI: {e}", exc_info=True)
        print(f"❌ Критическая ошибка: {e}")
        input("Нажмите Enter для выхода...")
        sys.exit(1)


def main():
    """Главная точка входа."""
    log_system_info()
    
    try:
        # Автоперевод интерфейса
        import modules.auto_translate  # noqa: F401
        logger.info("Модуль автоперевода загружен")
    except Exception as e:
        logger.warning(f"Не удалось загрузить автоперевод: {e}")

    if "--console" in sys.argv:
        run_console()
    else:
        run_gui()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # Перехват самых критических ошибок, которые не пойманы внутри
        logging.critical(f"НЕОБРАБОТАННАЯ ОШИБКА: {e}", exc_info=True)
        print(f"\n❌ Критическая ошибка: {e}")
        input("Нажмите Enter для выхода...")
        sys.exit(1)