"""
SanEpi AI — точка входа.

Запуск:
    python app.py            — графический интерфейс
    python app.py --console  — консольное меню
"""
import sys
import modules.auto_translate  # автоперевод интерфейса

def run_console():
    from modules.ai_assistant import ask_ai
    from modules.document_manager import DocumentManager

    document_manager = DocumentManager()

    while True:
        print("\n" + "=" * 60)
        print("SanEpi AI")
        print("=" * 60)
        print("1. Добавить приказ вручную")
        print("2. Задать вопрос AI")
        print("3. Выход")

        choice = input("\nВыберите пункт: ").strip()

        if choice == "1":
            try:
                result = document_manager.add_pdf()
                print()
                print(result["message"])
            except Exception:
                import traceback
                traceback.print_exc()

        elif choice == "2":
            question = input("Введите вопрос: ").strip()
            if question:
                result = ask_ai(question)
                print()
                print(result["answer"])

        elif choice == "3":
            print("Выход из SanEpi AI.")
            break

        else:
            print("Неверный пункт. Попробуйте снова.")


def main():
    if "--console" in sys.argv:
        run_console()
    else:
        from modules.main_window import start_main_window
        start_main_window()


if __name__ == "__main__":
    main()