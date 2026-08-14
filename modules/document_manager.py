import hashlib
import shutil
from pathlib import Path
from tkinter import filedialog

from modules.update_knowledge_base import update_knowledge_base


PROJECT_DIR = Path(__file__).resolve().parent.parent
KNOWLEDGE_BASE_DIR = PROJECT_DIR / "knowledge_base"
MANUAL_DOCUMENTS_DIR = (
    KNOWLEDGE_BASE_DIR / "manual_documents"
)


class DocumentManager:
    """
    Добавление и удаление вручную выбранных
    PDF-документов в SanEpi AI.
    """

    def _init_(self):
        MANUAL_DOCUMENTS_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

    @staticmethod
    def calculate_hash(
        file_path: Path
    ) -> str:
        file_hash = hashlib.sha256()

        with file_path.open("rb") as file:
            while True:
                chunk = file.read(
                    1024 * 1024
                )

                if not chunk:
                    break

                file_hash.update(chunk)

        return file_hash.hexdigest()

    def find_duplicate(
        self,
        source_path: Path
    ) -> Path | None:
        source_hash = self.calculate_hash(
            source_path
        )

        for existing_file in (
            MANUAL_DOCUMENTS_DIR.glob("*.pdf")
        ):
            try:
                existing_hash = (
                    self.calculate_hash(
                        existing_file
                    )
                )

                if existing_hash == source_hash:
                    return existing_file

            except Exception as error:
                print(
                    "Не удалось проверить файл:",
                    existing_file,
                    error
                )

        return None

    @staticmethod
    def create_unique_path(
        destination: Path
    ) -> Path:
        if not destination.exists():
            return destination

        counter = 2

        while True:
            candidate = destination.with_name(
                f"{destination.stem}_{counter}"
                f"{destination.suffix}"
            )

            if not candidate.exists():
                return candidate

            counter += 1

    def add_pdf(
        self,
        parent=None,
        progress_callback=None
    ) -> dict:
        selected_file = (
            filedialog.askopenfilename(
                parent=parent,
                title=(
                    "Выберите приказ "
                    "в формате PDF"
                ),
                filetypes=[
                    (
                        "PDF-документы",
                        "*.pdf"
                    ),
                    (
                        "Все файлы",
                        "."
                    ),
                ]
            )
        )

        if not selected_file:
            return {
                "status": "cancelled",
                "message": (
                    "Добавление отменено."
                )
            }

        source_path = Path(
            selected_file
        ).resolve()

        if not source_path.exists():
            raise FileNotFoundError(
                "Выбранный файл не найден: "
                f"{source_path}"
            )

        if not source_path.is_file():
            raise ValueError(
                "Выбранный путь "
                "не является файлом."
            )

        if source_path.suffix.lower() != ".pdf":
            raise ValueError(
                "Сейчас поддерживаются "
                "только PDF-документы."
            )

        duplicate = self.find_duplicate(
            source_path
        )

        if duplicate:
            return {
                "status": "duplicate",
                "message": (
                    "Этот документ уже "
                    "находится в базе."
                ),
                "file_path": str(duplicate)
            }

        MANUAL_DOCUMENTS_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        destination = (
            MANUAL_DOCUMENTS_DIR
            / source_path.name
        )

        destination = self.create_unique_path(
            destination
        )

        try:
            shutil.copy2(
                source_path,
                destination
            )

            if progress_callback:
                progress_callback(
                    "Документ скопирован. "
                    "Извлечение текста..."
                )

            update_result = (
                update_knowledge_base(
                    progress_callback=(
                        progress_callback
                    )
                )
            )

            return {
                "status": "added",
                "message": (
                    "Документ добавлен "
                    "в базу SanEpi AI."
                ),
                "file_path": str(destination),
                "update_result": update_result,
            }

        except Exception:
            if destination.exists():
                destination.unlink()

            raise

    def delete_document(
        self,
        document: dict,
        progress_callback=None
    ) -> dict:
        """
        Удаляет только документ из папки
        knowledge_base/manual_documents.
        """
        relative_path = str(
            document.get(
                "relative_path",
                ""
            )
        ).strip()

        if not relative_path:
            raise ValueError(
                "У документа отсутствует путь."
            )

        document_type = str(
            document.get(
                "document_type",
                ""
            )
        ).strip().lower()

        if document_type != "manual_documents":
            raise PermissionError(
                "Можно удалять только приказы, "
                "добавленные вручную."
            )

        file_path = (
            KNOWLEDGE_BASE_DIR
            / relative_path
        ).resolve()

        manual_directory = (
            MANUAL_DOCUMENTS_DIR.resolve()
        )

        try:
            file_path.relative_to(
                manual_directory
            )

        except ValueError as error:
            raise PermissionError(
                "Нельзя удалить документ "
                "за пределами manual_documents."
            ) from error

        if not file_path.exists():
            raise FileNotFoundError(
                "Файл приказа не найден: "
                f"{file_path}"
            )

        if not file_path.is_file():
            raise ValueError(
                "Выбранный путь "
                "не является файлом."
            )

        file_name = file_path.name

        file_path.unlink()

        if progress_callback:
            progress_callback(
                "Документ удалён. "
                "Обновление базы..."
            )

        update_result = update_knowledge_base(
            progress_callback=progress_callback
        )

        return {
            "status": "deleted",
            "message": (
                f"Приказ «{file_name}» удалён."
            ),
            "update_result": update_result,
        }