# StudentTrack HTTP API (ЛР1)

Базовый адрес: http://localhost:5000

## GET /health
Ответ: 200 {"status": "ok"}

## Дисциплины
| Метод | Путь | Описание | Успех | Ошибки |
|---|---|---|---|---|
| GET | /disciplines | список дисциплин | 200 [ {...} ] | 500 |
| GET | /disciplines/<id> | дисциплина по id | 200 {...} | 404 |
| POST | /disciplines | создать | 201 {...} | 400 |
| PUT | /disciplines/<id> | изменить | 200 {...} | 400, 404 |
| DELETE | /disciplines/<id> | удалить | 200 | 404 |

Пример POST /disciplines:
Запрос:  {"discipline_name": "DevOps"}
Ответ:   201 {"id": 1, "discipline_name": "DevOps"}
Ошибка:  400 {"error": "Bad Request", "message": "Поле 'discipline_name' обязательно"}

## Учебные планы
| Метод | Путь | Описание | Успех | Ошибки |
|---|---|---|---|---|
| GET | /study_plans | список планов | 200 | 500 |
| GET | /study_plans/<id> | план по id | 200 | 404 |
| POST | /study_plans | создать | 201 | 400 |
| PUT | /study_plans/<id> | изменить | 200 | 400, 404 |
| DELETE | /study_plans/<id> | удалить | 200 | 404 |

Пример POST /study_plans:
Запрос:  {"group_id": 1, "discipline_id": 1, "semester": 3}
Ответ:   201 {"id": 1, "group_id": 1, "discipline_id": 1, "semester": 3}
Ошибки:  400 — нет обязательных полей / semester < 1 / группа или дисциплина не найдены

## Оценки

| Метод | URL | Описание |
|---|---|---|
| GET | `/grades` | Получить список оценок |
| GET | `/grades/<id>` | Получить оценку |
| POST | `/grades` | Создать оценку |
| PUT | `/grades/<id>` | Изменить оценку |
| DELETE | `/grades/<id>` | Удалить оценку |

Пример создания оценки:

```json
{
  "student_id": 1,
  "discipline_id": 1,
  "grade": 5
}
```