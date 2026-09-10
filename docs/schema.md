# Схема базы данных StudentTrack

Документ описывает структуру реляционной базы данных системы **StudentTrack**.

На текущем этапе проекта в качестве СУБД используется **SQLite**, а взаимодействие с базой данных выполняется через **SQLAlchemy**.

## Общая схема

Основными сущностями системы являются:

- `Group` - учебная группа;
- `Student` - студент;
- `Discipline` - учебная дисциплина;
- `StudyPlan` - элемент учебного плана группы;
- `Grade` - оценка студента по дисциплине.

Основные связи:

```text
Group 1:N Student

Group 1:N StudyPlan

Discipline 1:N StudyPlan

Student 1:N Grade

Discipline 1:N Grade
```

Общая структура связей:

```text
Group -------- Student
  |
  |
  +---------- StudyPlan ---------- Discipline
                                      |
                                      |
Student -------- Grade ---------------+
```

`StudyPlan` связывает группу с дисциплиной.

`Grade` связывает студента с дисциплиной и содержит значение оценки и дату ее выставления.

---

# Таблица `groups`

Таблица содержит информацию об учебных группах.

Модель SQLAlchemy:

```text
Group
```

Имя таблицы:

```text
groups
```

## Поля

| Поле | Тип | Ограничения | Описание |
|---|---|---|---|
| `id` | Integer | Primary Key | Уникальный идентификатор группы |
| `group_name` | String | NOT NULL | Название учебной группы |
| `year` | Integer | NOT NULL | Год обучения |

Пример записи:

```json
{
  "id": 1,
  "group_name": "241-352",
  "year": 3
}
```

## Связи

Одна группа может содержать несколько студентов:

```text
Group 1:N Student
```

Связь реализуется следующим образом:

```text
groups.id -> students.group_id
```

Группа также может иметь несколько записей учебного плана:

```text
Group 1:N StudyPlan
```

Связь:

```text
groups.id -> study_plans.group_id
```

---

# Таблица `students`

Таблица содержит информацию о студентах.

Модель SQLAlchemy:

```text
Student
```

Имя таблицы:

```text
students
```

## Поля

| Поле | Тип | Ограничения | Описание |
|---|---|---|---|
| `id` | Integer | Primary Key | Уникальный идентификатор студента |
| `full_name` | String | NOT NULL | ФИО студента |
| `group_id` | Integer | Foreign Key, NOT NULL | Идентификатор учебной группы |
| `email` | String | Nullable | Электронная почта студента |

Внешний ключ:

```text
students.group_id -> groups.id
```

Пример записи:

```json
{
  "id": 1,
  "full_name": "Иван Иванов",
  "group_id": 1,
  "email": "ivan@example.com"
}
```

## Связи

Каждый студент относится к одной группе:

```text
Student N:1 Group
```

Один студент может иметь несколько оценок:

```text
Student 1:N Grade
```

Связь:

```text
students.id -> grades.student_id
```

---

# Таблица `disciplines`

Таблица содержит информацию об учебных дисциплинах.

Модель SQLAlchemy:

```text
Discipline
```

Имя таблицы:

```text
disciplines
```

## Поля

| Поле | Тип | Ограничения | Описание |
|---|---|---|---|
| `id` | Integer | Primary Key | Уникальный идентификатор дисциплины |
| `discipline_name` | String | NOT NULL | Название дисциплины |

Пример записи:

```json
{
  "id": 1,
  "discipline_name": "Методология и практики DevOps"
}
```

## Связи

Одна дисциплина может входить в учебные планы нескольких групп:

```text
Discipline 1:N StudyPlan
```

Связь:

```text
disciplines.id -> study_plans.discipline_id
```

По одной дисциплине может быть выставлено несколько оценок:

```text
Discipline 1:N Grade
```

Связь:

```text
disciplines.id -> grades.discipline_id
```

---

# Таблица `study_plans`

Таблица связывает учебную группу с дисциплиной и семестром.

Модель SQLAlchemy:

```text
StudyPlan
```

Имя таблицы:

```text
study_plans
```

`StudyPlan` используется для хранения учебного плана группы и для проверки возможности выставления оценки студенту.

## Поля

| Поле | Тип | Ограничения | Описание |
|---|---|---|---|
| `id` | Integer | Primary Key | Уникальный идентификатор записи учебного плана |
| `group_id` | Integer | Foreign Key, NOT NULL | Идентификатор группы |
| `discipline_id` | Integer | Foreign Key, NOT NULL | Идентификатор дисциплины |
| `semester` | Integer | NOT NULL | Семестр обучения |

Внешние ключи:

```text
study_plans.group_id -> groups.id

study_plans.discipline_id -> disciplines.id
```

Пример записи:

```json
{
  "id": 1,
  "group_id": 1,
  "discipline_id": 1,
  "semester": 1
}
```

Эта запись означает, что группа с `id = 1` изучает дисциплину с `id = 1` в первом семестре.

## Назначение

`StudyPlan` является связующей сущностью между `Group` и `Discipline`.

```text
Group --------\
               > StudyPlan
Discipline ---/
```

Одна группа может иметь несколько дисциплин:

```text
Group 1:N StudyPlan
```

Одна дисциплина может использоваться в учебных планах нескольких групп:

```text
Discipline 1:N StudyPlan
```

В результате между `Group` и `Discipline` формируется отношение многие-ко-многим через таблицу `study_plans`:

```text
Group M:N Discipline
```

Связующая таблица:

```text
Group -> StudyPlan <- Discipline
```

---

# Таблица `grades`

Таблица содержит оценки студентов по дисциплинам.

Модель SQLAlchemy:

```text
Grade
```

Имя таблицы:

```text
grades
```

## Поля

| Поле | Тип | Ограничения | Описание |
|---|---|---|---|
| `id` | Integer | Primary Key | Уникальный идентификатор оценки |
| `student_id` | Integer | Foreign Key, NOT NULL | Идентификатор студента |
| `discipline_id` | Integer | Foreign Key, NOT NULL | Идентификатор дисциплины |
| `grade` | Integer | NOT NULL, от 1 до 5 | Значение оценки |
| `date` | Date | NOT NULL | Дата выставления оценки |

Внешние ключи:

```text
grades.student_id -> students.id

grades.discipline_id -> disciplines.id
```

Пример записи:

```json
{
  "id": 1,
  "student_id": 1,
  "discipline_id": 1,
  "grade": 5,
  "date": "2026-09-10"
}
```

## Связи

Одна оценка принадлежит одному студенту:

```text
Grade N:1 Student
```

Одна оценка относится к одной дисциплине:

```text
Grade N:1 Discipline
```

Один студент может иметь несколько оценок:

```text
Student 1:N Grade
```

Одна дисциплина может иметь несколько связанных оценок:

```text
Discipline 1:N Grade
```

---

# Ограничение диапазона оценки

Оценка может принимать только целочисленные значения:

```text
1
2
3
4
5
```

Условие:

```text
1 <= grade <= 5
```

Например, следующий запрос является допустимым:

```json
{
  "student_id": 1,
  "discipline_id": 1,
  "grade": 5
}
```

Следующий запрос является недопустимым:

```json
{
  "student_id": 1,
  "discipline_id": 1,
  "grade": 6
}
```

При попытке создать оценку вне диапазона от 1 до 5 API должен вернуть:

```text
HTTP 400 Bad Request
```

---

# Бизнес-правило выставления оценки

Оценка может быть выставлена студенту только по дисциплине, которая присутствует в учебном плане его группы.

Общая последовательность проверки:

```text
student_id
    |
    v
Student
    |
    v
group_id


group_id + discipline_id
          |
          v
      StudyPlan
          |
          v
     запись есть?
       /      \
      да      нет
      |        |
      v        v
   Grade    HTTP 400
```

Алгоритм проверки:

1. Из запроса получается `student_id`.
2. По `student_id` выполняется поиск студента.
3. Если студент не существует, возвращается `HTTP 404`.
4. Из запроса получается `discipline_id`.
5. По `discipline_id` выполняется поиск дисциплины.
6. Если дисциплина не существует, возвращается `HTTP 404`.
7. Из записи студента определяется `group_id`.
8. Выполняется поиск записи `StudyPlan` для найденной группы и указанной дисциплины.
9. Если такая запись отсутствует, оценка не создается и возвращается `HTTP 400`.
10. Если запись существует, оценка сохраняется в таблице `grades`.

Условие поиска учебного плана:

```text
StudyPlan.group_id = Student.group_id

AND

StudyPlan.discipline_id = Grade.discipline_id
```

Упрощенно:

```text
Student
   |
   v
Group
   |
   +------------------+
                      |
                      v
                 StudyPlan
                      ^
                      |
                      |
                 Discipline
```

Если существует:

```text
StudyPlan(
    group_id = student.group_id,
    discipline_id = requested_discipline_id
)
```

то создание оценки разрешено.

Если такой записи нет, создание оценки запрещено.

---

# Пример допустимого выставления оценки

Пусть в базе существуют следующие данные:

```text
Group:
id = 1

Student:
id = 1
group_id = 1

Discipline:
id = 1

StudyPlan:
group_id = 1
discipline_id = 1
semester = 1
```

Структура:

```text
Student 1
   |
   v
Group 1
   |
   v
StudyPlan
   |
   v
Discipline 1
```

Тогда запрос:

```json
{
  "student_id": 1,
  "discipline_id": 1,
  "grade": 5
}
```

является допустимым.

В результате создается запись:

```text
Grade:
student_id = 1
discipline_id = 1
grade = 5
date = текущая дата
```

---

# Пример запрещенного выставления оценки

Пусть студент находится в группе `1`:

```text
Student:
id = 1
group_id = 1
```

И существует дисциплина:

```text
Discipline:
id = 2
```

Но в таблице `study_plans` отсутствует запись:

```text
group_id = 1
discipline_id = 2
```

Тогда запрос:

```json
{
  "student_id": 1,
  "discipline_id": 2,
  "grade": 5
}
```

должен быть отклонен.

Ответ:

```text
HTTP 400 Bad Request
```

Причина: дисциплина отсутствует в учебном плане группы студента.

---

# Связи между таблицами

## Group - Student

Тип связи:

```text
1:N
```

Одна группа содержит несколько студентов.

```text
groups.id -> students.group_id
```

Пример:

```text
Group 1
 |
 +-- Student 1
 |
 +-- Student 2
 |
 +-- Student 3
```

---

## Group - StudyPlan

Тип связи:

```text
1:N
```

Одна группа может иметь несколько записей учебного плана.

```text
groups.id -> study_plans.group_id
```

Пример:

```text
Group 1
 |
 +-- StudyPlan: Discipline 1
 |
 +-- StudyPlan: Discipline 2
 |
 +-- StudyPlan: Discipline 3
```

---

## Discipline - StudyPlan

Тип связи:

```text
1:N
```

Одна дисциплина может находиться в учебных планах нескольких групп.

```text
disciplines.id -> study_plans.discipline_id
```

Пример:

```text
Discipline 1
 |
 +-- StudyPlan for Group 1
 |
 +-- StudyPlan for Group 2
 |
 +-- StudyPlan for Group 3
```

---

## Student - Grade

Тип связи:

```text
1:N
```

Один студент может иметь несколько оценок.

```text
students.id -> grades.student_id
```

Пример:

```text
Student 1
 |
 +-- Grade 5
 |
 +-- Grade 4
 |
 +-- Grade 3
```

---

## Discipline - Grade

Тип связи:

```text
1:N
```

По одной дисциплине может быть выставлено несколько оценок.

```text
disciplines.id -> grades.discipline_id
```

Пример:

```text
Discipline 1
 |
 +-- Grade for Student 1
 |
 +-- Grade for Student 2
 |
 +-- Grade for Student 3
```

---

# Итоговая структура базы данных

```text
groups
--------------------------------
id              PK
group_name      NOT NULL
year            NOT NULL


students
--------------------------------
id              PK
full_name       NOT NULL
group_id        FK -> groups.id
email


disciplines
--------------------------------
id              PK
discipline_name NOT NULL


study_plans
--------------------------------
id              PK
group_id        FK -> groups.id
discipline_id   FK -> disciplines.id
semester        NOT NULL


grades
--------------------------------
id              PK
student_id      FK -> students.id
discipline_id   FK -> disciplines.id
grade           NOT NULL, 1-5
date            NOT NULL
```

---

# Схема внешних ключей

```text
groups.id
    |
    +-> students.group_id
    |
    +-> study_plans.group_id


disciplines.id
    |
    +-> study_plans.discipline_id
    |
    +-> grades.discipline_id


students.id
    |
    +-> grades.student_id
```

---

# Логическая схема

```text
                 groups
                /      \
               /        \
              v          v
        students      study_plans
            |          /       ^
            |         /        /
            |        /        /
            v       /        /
          grades <-+        /
            ^              /
            |             /
            |            /
            +---- disciplines
```

В более простом виде:

```text
Group -> Student -> Grade
  |                  ^
  |                  |
  v                  |
StudyPlan <- Discipline
```

При этом:

```text
Group -> StudyPlan <- Discipline
```

определяет набор дисциплин, которые разрешены для группы.

А:

```text
Student -> Grade <- Discipline
```

определяет конкретную оценку студента по дисциплине.

---

# Ограничения целостности

Для сохранения целостности данных применяются следующие правила:

1. Каждая запись имеет уникальный первичный ключ `id`.
2. `Student.group_id` должен ссылаться на существующую группу.
3. `StudyPlan.group_id` должен ссылаться на существующую группу.
4. `StudyPlan.discipline_id` должен ссылаться на существующую дисциплину.
5. `Grade.student_id` должен ссылаться на существующего студента.
6. `Grade.discipline_id` должен ссылаться на существующую дисциплину.
7. Значение `Grade.grade` должно находиться в диапазоне от 1 до 5.
8. Оценка может быть выставлена только по дисциплине, присутствующей в учебном плане группы студента.
9. Для каждой оценки сохраняется дата ее выставления.

---

# Обработка ошибок

При нарушении ограничений API возвращает соответствующий HTTP-код.

| Ситуация | HTTP-код |
|---|---|
| Некорректные данные запроса | `400 Bad Request` |
| Оценка меньше 1 или больше 5 | `400 Bad Request` |
| Дисциплина отсутствует в учебном плане группы | `400 Bad Request` |
| Студент не существует | `404 Not Found` |
| Дисциплина не существует | `404 Not Found` |
| Оценка не существует | `404 Not Found` |

---

# Использование SQLite

На текущем этапе проекта в качестве базы данных используется SQLite.

SQLite выбрана для первой лабораторной работы, поскольку она:

- не требует отдельного сервера базы данных;
- проста для локальной разработки;
- позволяет хранить базу данных в одном файле;
- поддерживается SQLAlchemy;
- подходит для минимально работоспособной версии приложения.

Подключение к базе данных выполняется через SQLAlchemy.

Пример строки подключения:

```text
sqlite:///studenttrack.db
```

Файл базы данных является локальным файлом проекта и не должен добавляться в Git.

---

# Работа через SQLAlchemy

Все основные сущности представлены моделями SQLAlchemy:

```text
Group
Student
Discipline
StudyPlan
Grade
```

Каждая модель соответствует отдельной таблице:

```text
Group      -> groups
Student    -> students
Discipline -> disciplines
StudyPlan  -> study_plans
Grade      -> grades
```

SQLAlchemy используется для:

- создания таблиц;
- определения первичных и внешних ключей;
- создания записей;
- получения записей;
- изменения записей;
- удаления записей;
- выполнения запросов к базе данных.

Использование ORM позволяет не привязывать основную логику приложения непосредственно к синтаксису SQLite.

В следующих этапах проекта предусматривается возможность перехода на PostgreSQL.