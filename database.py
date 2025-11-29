"""Модуль для работы с базой данных (JSON файл)."""
import json
import logging
import os
from typing import Dict, Any, Optional
from datetime import datetime
from config import config


class QuestionsDatabase:
    """Класс для работы с вопросами пользователей."""
    
    def __init__(self, file_path: str = None):
        """Инициализация базы данных."""
        self.file_path = file_path or config.QUESTIONS_FILE
        self._data: Dict[str, Any] = {}
        self.load()
    
    def load(self) -> None:
        """Загружает данные из файла."""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
                logging.info(f"Загружено {len(self._data)} записей из {self.file_path}")
            except json.JSONDecodeError as e:
                logging.error(f"Ошибка парсинга JSON: {e}")
                self._data = {}
            except Exception as e:
                logging.error(f"Ошибка загрузки вопросов: {e}")
                self._data = {}
        else:
            self._data = {}
            logging.info(f"Файл {self.file_path} не найден, создана новая база")
    
    def save(self) -> bool:
        """Сохраняет данные в файл."""
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logging.error(f"Ошибка сохранения вопросов: {e}")
            return False
    
    def add_question(self, user_id: int, question: str, username: str = None, 
                     full_name: str = None) -> bool:
        """Добавляет новый вопрос."""
        user_id_str = str(user_id)
        self._data[user_id_str] = {
            "question": question,
            "username": username,
            "full_name": full_name,
            "created_at": datetime.now().isoformat(),
            "admin_ready_to_reply": False,
            "answered": False
        }
        return self.save()
    
    def get_question(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получает вопрос пользователя."""
        user_id_str = str(user_id)
        return self._data.get(user_id_str)
    
    def set_admin_ready(self, user_id: int) -> bool:
        """Помечает, что админ готов ответить."""
        user_id_str = str(user_id)
        if user_id_str in self._data:
            if isinstance(self._data[user_id_str], dict):
                self._data[user_id_str]["admin_ready_to_reply"] = True
            else:
                # Миграция старого формата
                self._data[user_id_str] = {
                    "question": self._data[user_id_str],
                    "admin_ready_to_reply": True,
                    "created_at": datetime.now().isoformat(),
                    "answered": False
                }
            return self.save()
        return False
    
    def mark_answered(self, user_id: int) -> bool:
        """Помечает вопрос как отвеченный."""
        user_id_str = str(user_id)
        if user_id_str in self._data:
            if isinstance(self._data[user_id_str], dict):
                self._data[user_id_str]["answered"] = True
            return self.save()
        return False
    
    def delete_question(self, user_id: int) -> bool:
        """Удаляет вопрос."""
        user_id_str = str(user_id)
        if user_id_str in self._data:
            del self._data[user_id_str]
            return self.save()
        return False
    
    def get_pending_questions(self) -> Dict[str, Dict[str, Any]]:
        """Возвращает все неотвеченные вопросы."""
        return {
            uid: data for uid, data in self._data.items()
            if isinstance(data, dict) and not data.get("answered", False)
        }
    
    def get_ready_to_reply(self) -> Optional[tuple[int, Dict[str, Any]]]:
        """Возвращает первый вопрос, на который админ готов ответить."""
        for uid, data in self._data.items():
            if isinstance(data, dict) and data.get("admin_ready_to_reply") and not data.get("answered"):
                return int(uid), data
        return None
    
    def get_statistics(self) -> Dict[str, int]:
        """Возвращает статистику по вопросам."""
        total = len(self._data)
        pending = sum(1 for d in self._data.values() 
                     if isinstance(d, dict) and not d.get("answered", False))
        answered = total - pending
        return {
            "total": total,
            "pending": pending,
            "answered": answered
        }
    
    def get_all_questions(self) -> Dict[str, Any]:
        """Возвращает все вопросы (для админа)."""
        return self._data.copy()


# Глобальный экземпляр базы данных
db = QuestionsDatabase()

