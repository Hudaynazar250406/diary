const appElement = document.getElementById("dashboard-app");

const currentRole = appElement.dataset.role;


const isStudent = currentRole === "student";
const isTeacher = currentRole === "teacher";
const isAdmin = currentRole === "admin";

const state = {
    groups: [],
    students: [],
    disciplines: [],
    plans: [],
    grades: [],
    users: [],
    schedules: [],

    myDisciplines: [],
    mySchedule: [],
};


async function api(url, options = {}) {
    const response = await fetch(url, options);

    if (!response.ok) {
        let message = `Ошибка HTTP ${response.status}`;

        try {
            const data = await response.json();

            if (data.error) {
                message = data.error;
            }
        } catch {
            // Оставляем стандартное сообщение.
        }

        throw new Error(message);
    }

    if (response.status === 204) {
        return null;
    }

    const contentType = response.headers.get("content-type") || "";

    if (!contentType.includes("application/json")) {
        return null;
    }

    return response.json();
}


async function loadAllData() {
    clearMessage();

    try {
        if (isStudent) {
            const [
                grades,
                disciplines,
                schedule,
            ] = await Promise.all([
                api("/me/grades"),
                api("/me/disciplines"),
                api("/me/schedule"),
            ]);

            state.grades = grades;
            state.myDisciplines = disciplines;
            state.mySchedule = schedule;

            renderStudentData();

            return;
        }

        if (isAdmin) {
            const [
                groups,
                students,
                disciplines,
                plans,
                grades,
                users,
                schedules,
            ] = await Promise.all([
                api("/groups"),
                api("/students"),
                api("/disciplines"),
                api("/study_plans"),
                api("/grades"),
                api("/admin/users"),
                api("/schedules"),
            ]);

            state.groups = groups;
            state.students = students;
            state.disciplines = disciplines;
            state.plans = plans;
            state.grades = grades;
            state.users = users;
            state.schedules = schedules;

            renderAll();
            renderUsers();

            return;
        }

        if (isTeacher) {
            const [
                groups,
                students,
                disciplines,
                plans,
                grades,
                schedules,
            ] = await Promise.all([
                api("/groups"),
                api("/students"),
                api("/disciplines"),
                api("/study_plans"),
                api("/grades"),
                api("/schedules"),
            ]);

            state.groups = groups;
            state.students = students;
            state.disciplines = disciplines;
            state.plans = plans;
            state.grades = grades;
            state.schedules = schedules;

            renderAll();
        }
    } catch (error) {
        showMessage(
            error.message,
            "error",
        );
    }
}


function renderAll() {
    renderStats();
    renderGroups();
    renderStudents();
    renderDisciplines();
    renderPlans();
    renderSchedules();
    renderGrades();
    renderSelects();
}

function renderSchedules() {
    const body = document.getElementById(
        "schedule-table-body",
    );

    if (!body) {
        return;
    }

    body.replaceChildren();

    if (state.schedules.length === 0) {
        showEmptyRow(
            body,
            7,
            "Расписание пока не составлено.",
        );

        return;
    }

    const weekdays = {
        1: "Понедельник",
        2: "Вторник",
        3: "Среда",
        4: "Четверг",
        5: "Пятница",
        6: "Суббота",
        7: "Воскресенье",
    };

    for (const lesson of state.schedules) {
        const row = document.createElement("tr");

        const group = state.groups.find(
            (item) => item.id === lesson.group_id,
        );

        const discipline = state.disciplines.find(
            (item) => item.id === lesson.discipline_id,
        );

        row.appendChild(
            makeCell(lesson.id),
        );

        row.appendChild(
            makeCell(
                group
                    ? group.group_name
                    : `ID ${lesson.group_id}`,
            ),
        );

        row.appendChild(
            makeCell(
                weekdays[lesson.weekday],
            ),
        );

        row.appendChild(
            makeCell(
                `${lesson.start_time} — ${lesson.end_time}`,
            ),
        );

        row.appendChild(
            makeCell(
                discipline
                    ? discipline.discipline_name
                    : `ID ${lesson.discipline_id}`,
            ),
        );

        row.appendChild(
            makeCell(lesson.room || "—"),
        );

        row.appendChild(
            makeActionCell(
                () => editSchedule(lesson),
                () => deleteEntity(
                    "schedule",
                    lesson.id,
                    `занятие #${lesson.id}`,
                ),
            ),
        );

        body.appendChild(row);
    }
}

function renderStudentData() {
    const gradesCounter = document.getElementById(
        "my-grades-count",
    );

    if (gradesCounter) {
        gradesCounter.textContent = state.grades.length;
    }

    renderMyDisciplines();
    renderMySchedule();
    renderMyGrades();
}

function renderMyDisciplines() {
    const body = document.getElementById(
        "my-disciplines-table-body",
    );

    if (!body) {
        return;
    }

    body.replaceChildren();

    if (state.myDisciplines.length === 0) {
        showEmptyRow(
            body,
            3,
            "Дисциплины пока не назначены.",
        );

        return;
    }

    for (const discipline of state.myDisciplines) {
        const row = document.createElement("tr");

        row.appendChild(
            makeCell(discipline.id),
        );

        row.appendChild(
            makeCell(discipline.discipline_name),
        );

        row.appendChild(
            makeCell(discipline.semester),
        );

        body.appendChild(row);
    }
}

function renderMySchedule() {
    const body = document.getElementById(
        "my-schedule-table-body",
    );

    if (!body) {
        return;
    }

    body.replaceChildren();

    if (state.mySchedule.length === 0) {
        showEmptyRow(
            body,
            4,
            "Расписание пока не составлено.",
        );

        return;
    }

    for (const lesson of state.mySchedule) {
        const row = document.createElement("tr");

        row.appendChild(
            makeCell(lesson.weekday_name),
        );

        row.appendChild(
            makeCell(
                `${lesson.start_time} — ${lesson.end_time}`,
            ),
        );

        row.appendChild(
            makeCell(lesson.discipline_name),
        );

        row.appendChild(
            makeCell(lesson.room || "—"),
        );

        body.appendChild(row);
    }
}

// function renderStudentData() {
//     renderMyGrades();
// }

function renderStats() {
    document.getElementById("groups-count").textContent = state.groups.length;
    document.getElementById("students-count").textContent = state.students.length;
    document.getElementById("disciplines-count").textContent = state.disciplines.length;
    document.getElementById("plans-count").textContent = state.plans.length;
    document.getElementById("grades-count").textContent = state.grades.length;
}


function makeCell(value) {
    const cell = document.createElement("td");
    cell.textContent = value ?? "—";

    return cell;
}


function makeActionCell(onEdit, onDelete) {
    const cell = document.createElement("td");
    cell.className = "table-actions";

    const editButton = document.createElement("button");

    editButton.type = "button";
    editButton.className = "button button-small button-secondary";
    editButton.textContent = "Изменить";
    editButton.addEventListener("click", onEdit);

    const deleteButton = document.createElement("button");

    deleteButton.type = "button";
    deleteButton.className = "button button-small button-danger";
    deleteButton.textContent = "Удалить";
    deleteButton.addEventListener("click", onDelete);

    cell.append(editButton, deleteButton);

    return cell;
}


function showEmptyRow(tableBody, columns, text) {
    const row = document.createElement("tr");
    const cell = document.createElement("td");

    cell.colSpan = columns;
    cell.className = "empty-cell";
    cell.textContent = text;

    row.appendChild(cell);
    tableBody.appendChild(row);
}

function renderGroups() {
    const body = document.getElementById(
        "groups-table-body",
    );

    body.replaceChildren();

    if (state.groups.length === 0) {
        showEmptyRow(
            body,
            4,
            "Группы пока не добавлены.",
        );

        return;
    }

    for (const group of state.groups) {
        const row = document.createElement("tr");

        row.appendChild(
            makeCell(group.id),
        );

        row.appendChild(
            makeCell(group.group_name),
        );

        row.appendChild(
            makeCell(group.year),
        );

        if (isAdmin) {
            row.appendChild(
                makeActionCell(
                    () => editGroup(group),

                    () => deleteEntity(
                        "group",
                        group.id,
                        group.group_name,
                    ),
                ),
            );
        } else {
            row.appendChild(
                makeCell("Только просмотр"),
            );
        }

        body.appendChild(row);
    }
}

// function renderGroups() {
//     const body = document.getElementById("groups-table-body");

//     body.replaceChildren();

//     if (state.groups.length === 0) {
//         showEmptyRow(body, 4, "Группы пока не добавлены.");
//         return;
//     }

//     for (const group of state.groups) {
//         const row = document.createElement("tr");

//         row.appendChild(makeCell(group.id));
//         row.appendChild(makeCell(group.group_name));
//         row.appendChild(makeCell(group.year));

//         row.appendChild(
//             makeActionCell(
//                 () => editGroup(group),
//                 () => deleteEntity(
//                     "group",
//                     group.id,
//                     group.group_name,
//                 ),
//             ),
//         );

//         body.appendChild(row);
//     }
// }


function renderStudents() {
    const body = document.getElementById("students-table-body");

    body.replaceChildren();

    if (state.students.length === 0) {
        showEmptyRow(body, 5, "Студенты пока не добавлены.");
        return;
    }

    for (const student of state.students) {
        const row = document.createElement("tr");

        const group = state.groups.find(
            (item) => item.id === student.group_id,
        );

        row.appendChild(makeCell(student.id));
        row.appendChild(makeCell(student.full_name));
        row.appendChild(makeCell(student.email || "—"));

        row.appendChild(
            makeCell(
                group
                    ? group.group_name
                    : `ID ${student.group_id}`,
            ),
        );

        if (isAdmin) {
            row.appendChild(
                makeActionCell(
                    () => editStudent(student),
                    () => deleteEntity(
                        "student",
                        student.id,
                        student.full_name,
                    ),
                ),
            );
        } else {
            row.appendChild(
                makeCell("Только просмотр"),
            );
        }

        body.appendChild(row);
    }
}


function renderDisciplines() {
    const body = document.getElementById("disciplines-table-body");

    body.replaceChildren();

    if (state.disciplines.length === 0) {
        showEmptyRow(
            body,
            3,
            "Дисциплины пока не добавлены.",
        );

        return;
    }

    for (const discipline of state.disciplines) {
        const row = document.createElement("tr");

        row.appendChild(makeCell(discipline.id));
        row.appendChild(makeCell(discipline.discipline_name));

        if (isAdmin) {
            row.appendChild(
                makeActionCell(
                    () => editDiscipline(discipline),
                    () => deleteEntity(
                        "discipline",
                        discipline.id,
                        discipline.discipline_name,
                    ),
                ),
            );
        } else {
            row.appendChild(
                makeCell("Только просмотр"),
            );
        }

        body.appendChild(row);
    }
}


function renderPlans() {
    const body = document.getElementById("plans-table-body");

    body.replaceChildren();

    if (state.plans.length === 0) {
        showEmptyRow(
            body,
            5,
            "Учебные планы пока не добавлены.",
        );

        return;
    }

    for (const plan of state.plans) {
        const row = document.createElement("tr");

        const group = state.groups.find(
            (item) => item.id === plan.group_id,
        );

        const discipline = state.disciplines.find(
            (item) => item.id === plan.discipline_id,
        );

        row.appendChild(makeCell(plan.id));

        row.appendChild(
            makeCell(
                group
                    ? group.group_name
                    : `ID ${plan.group_id}`,
            ),
        );

        row.appendChild(
            makeCell(
                discipline
                    ? discipline.discipline_name
                    : `ID ${plan.discipline_id}`,
            ),
        );

        row.appendChild(makeCell(plan.semester));

        if (isAdmin) {
            row.appendChild(
                makeActionCell(
                    () => editPlan(plan),
                    () => deleteEntity(
                        "plan",
                        plan.id,
                        `учебный план #${plan.id}`,
                    ),
                ),
            );
        } else {
            row.appendChild(
                makeCell("Только просмотр"),
            );
        }

        body.appendChild(row);
    }
}

function renderGrades() {
    const body = document.getElementById("grades-table-body");

    body.replaceChildren();

    if (state.grades.length === 0) {
        showEmptyRow(
            body,
            6,
            "Оценки пока не добавлены.",
        );

        return;
    }

    for (const grade of state.grades) {
        const row = document.createElement("tr");

        const student = state.students.find(
            (item) => item.id === grade.student_id,
        );

        const discipline = state.disciplines.find(
            (item) => item.id === grade.discipline_id,
        );

        row.appendChild(makeCell(grade.id));

        row.appendChild(
            makeCell(
                student
                    ? student.full_name
                    : `ID ${grade.student_id}`,
            ),
        );

        row.appendChild(
            makeCell(
                discipline
                    ? discipline.discipline_name
                    : `ID ${grade.discipline_id}`,
            ),
        );

        row.appendChild(makeCell(grade.grade));
        row.appendChild(makeCell(grade.date));

        if (isTeacher || isAdmin) {
            row.appendChild(
                makeActionCell(
                    () => editGrade(grade),
                    () => deleteEntity(
                        "grade",
                        grade.id,
                        `оценку #${grade.id}`,
                    ),
                ),
            );
        } else {
            row.appendChild(
                makeCell("Только просмотр"),
            );
        }

        body.appendChild(row);
    }
}

// function renderGrades() {
//     const body = document.getElementById("grades-table-body");

//     body.replaceChildren();

//     if (state.grades.length === 0) {
//         showEmptyRow(
//             body,
//             6,
//             "Оценки пока не добавлены.",
//         );

//         return;
//     }

//     for (const grade of state.grades) {
//         const row = document.createElement("tr");

//         const student = state.students.find(
//             (item) => item.id === grade.student_id,
//         );

//         const discipline = state.disciplines.find(
//             (item) => item.id === grade.discipline_id,
//         );

//         row.appendChild(makeCell(grade.id));

//         row.appendChild(
//             makeCell(
//                 student
//                     ? student.full_name
//                     : `ID ${grade.student_id}`,
//             ),
//         );

//         row.appendChild(
//             makeCell(
//                 discipline
//                     ? discipline.discipline_name
//                     : `ID ${grade.discipline_id}`,
//             ),
//         );

//         row.appendChild(makeCell(grade.grade));
//         row.appendChild(makeCell(grade.date));

//         row.appendChild(
//             makeActionCell(
//                 () => editGrade(grade),
//                 () => deleteEntity(
//                     "grade",
//                     grade.id,
//                     `оценку #${grade.id}`,
//                 ),
//             ),
//         );

//         body.appendChild(row);
//     }
// }


function fillSelect(
    selectId,
    items,
    valueKey,
    labelBuilder,
    placeholder,
) {
    const select = document.getElementById(selectId);
    if (!select) {
        return;
    }

    const previousValue = select.value;

    select.replaceChildren();

    const placeholderOption = document.createElement("option");

    placeholderOption.value = "";
    placeholderOption.textContent = placeholder;

    select.appendChild(placeholderOption);

    for (const item of items) {
        const option = document.createElement("option");

        option.value = item[valueKey];
        option.textContent = labelBuilder(item);

        select.appendChild(option);
    }

    const valueExists = [...select.options].some(
        (option) => option.value === previousValue,
    );

    if (valueExists) {
        select.value = previousValue;
    }
}


function renderSelects() {
    fillSelect(
        "student-group-id",
        state.groups,
        "id",
        (group) => `${group.group_name} (${group.year})`,
        "Выберите группу",
    );

    fillSelect(
        "plan-group-id",
        state.groups,
        "id",
        (group) => `${group.group_name} (${group.year})`,
        "Выберите группу",
    );

    fillSelect(
        "plan-discipline-id",
        state.disciplines,
        "id",
        (discipline) => discipline.discipline_name,
        "Выберите дисциплину",
    );

    fillSelect(
        "grade-student-id",
        state.students,
        "id",
        (student) => student.full_name,
        "Выберите студента",
    );

    updateGradeDisciplineOptions();

    fillSelect(
        "schedule-group-id",
        state.groups,
        "id",
        (group) => `${group.group_name} (${group.year})`,
        "Выберите группу",
    );
    
    updateScheduleDisciplineOptions();
}

function updateScheduleDisciplineOptions(
    selectedDisciplineId = null,
) {
    const groupSelect = document.getElementById(
        "schedule-group-id",
    );

    const disciplineSelect = document.getElementById(
        "schedule-discipline-id",
    );

    if (!groupSelect || !disciplineSelect) {
        return;
    }

    const groupId = Number(groupSelect.value);

    disciplineSelect.replaceChildren();

    const placeholder = document.createElement("option");

    placeholder.value = "";

    if (groupId) {
        placeholder.textContent = "Выберите дисциплину";
    } else {
        placeholder.textContent = "Сначала выберите группу";
    }

    disciplineSelect.appendChild(placeholder);

    if (!groupId) {
        return;
    }

    const disciplineIds = new Set(
        state.plans
            .filter(
                (plan) => plan.group_id === groupId,
            )
            .map(
                (plan) => plan.discipline_id,
            ),
    );

    const disciplines = state.disciplines.filter(
        (discipline) => disciplineIds.has(
            discipline.id,
        ),
    );

    for (const discipline of disciplines) {
        const option = document.createElement("option");

        option.value = discipline.id;
        option.textContent = discipline.discipline_name;

        disciplineSelect.appendChild(option);
    }

    if (selectedDisciplineId !== null) {
        disciplineSelect.value = String(
            selectedDisciplineId,
        );
    }
}

async function submitSchedule(event) {
    event.preventDefault();

    const id = document.getElementById(
        "schedule-edit-id",
    ).value;

    const room = document.getElementById(
        "schedule-room",
    ).value.trim();

    const payload = {
        group_id: Number(
            document.getElementById(
                "schedule-group-id",
            ).value,
        ),

        discipline_id: Number(
            document.getElementById(
                "schedule-discipline-id",
            ).value,
        ),

        weekday: Number(
            document.getElementById(
                "schedule-weekday",
            ).value,
        ),

        start_time: document.getElementById(
            "schedule-start-time",
        ).value,

        end_time: document.getElementById(
            "schedule-end-time",
        ).value,

        room: room || null,
    };

    await saveEntity(
        "schedule",
        id,
        payload,
    );
}

function editSchedule(lesson) {
    openSection("schedule");

    setFormMode(
        "schedule",
        lesson.id,
        "Изменить занятие",
    );

    document.getElementById(
        "schedule-group-id",
    ).value = String(lesson.group_id);

    updateScheduleDisciplineOptions(
        lesson.discipline_id,
    );

    document.getElementById(
        "schedule-weekday",
    ).value = String(lesson.weekday);

    document.getElementById(
        "schedule-start-time",
    ).value = lesson.start_time;

    document.getElementById(
        "schedule-end-time",
    ).value = lesson.end_time;

    document.getElementById(
        "schedule-room",
    ).value = lesson.room || "";
}

function updateGradeDisciplineOptions(
    selectedDisciplineId = null,
) {
    const studentSelect = document.getElementById(
        "grade-student-id",
    );

    const disciplineSelect = document.getElementById(
        "grade-discipline-id",
    );

    if (!studentSelect || !disciplineSelect) {
        return;
    }

    const studentId = Number(studentSelect.value);

    const student = state.students.find(
        (item) => item.id === studentId,
    );

    disciplineSelect.replaceChildren();

    const placeholder = document.createElement("option");

    placeholder.value = "";

    if (student) {
        placeholder.textContent = "Выберите дисциплину";
    } else {
        placeholder.textContent = "Сначала выберите студента";
    }

    disciplineSelect.appendChild(placeholder);

    if (!student) {
        return;
    }

    const allowedDisciplineIds = new Set(
        state.plans
            .filter(
                (plan) => plan.group_id === student.group_id,
            )
            .map(
                (plan) => plan.discipline_id,
            ),
    );

    const allowedDisciplines = state.disciplines.filter(
        (discipline) => allowedDisciplineIds.has(
            discipline.id,
        ),
    );

    for (const discipline of allowedDisciplines) {
        const option = document.createElement("option");

        option.value = discipline.id;
        option.textContent = discipline.discipline_name;

        disciplineSelect.appendChild(option);
    }

    if (selectedDisciplineId !== null) {
        disciplineSelect.value = String(
            selectedDisciplineId,
        );
    }
}


function openSection(sectionName) {
    const sections = document.querySelectorAll(
        ".dashboard-section",
    );

    for (const section of sections) {
        section.hidden = (
            section.id !== `section-${sectionName}`
        );
    }

    const buttons = document.querySelectorAll(
        ".nav-button",
    );

    for (const button of buttons) {
        button.classList.toggle(
            "active",
            button.dataset.section === sectionName,
        );
    }

    const titles = {
        overview: "Обзор",
        groups: "Группы",
        students: "Студенты",
        disciplines: "Дисциплины",
        plans: "Учебные планы",
        schedule: "Расписание",
        grades: "Оценки",
        users: "Пользователи",

        "my-disciplines": "Мои дисциплины",
        "my-schedule": "Моё расписание",
        "my-grades": "Мои оценки",
    };

    document.getElementById(
        "page-title",
    ).textContent = titles[sectionName];
}


function setFormMode(prefix, id, title) {
    document.getElementById(
        `${prefix}-edit-id`,
    ).value = id;

    document.getElementById(
        `${prefix}-form-title`,
    ).textContent = title;

    document.getElementById(
        `${prefix}-cancel`,
    ).hidden = false;
}


function resetForm(prefix) {
    const form = document.getElementById(
        `${prefix}-form`,
    );

    form.reset();

    document.getElementById(
        `${prefix}-edit-id`,
    ).value = "";

    document.getElementById(
        `${prefix}-cancel`,
    ).hidden = true;

    const defaultTitles = {
        group: "Добавить группу",
        student: "Добавить студента",
        discipline: "Добавить дисциплину",
        plan: "Добавить учебный план",
        grade: "Добавить оценку",
        schedule: "Добавить занятие",
    };

    document.getElementById(
        `${prefix}-form-title`,
    ).textContent = defaultTitles[prefix];

    if (prefix === "grade") {
        updateGradeDisciplineOptions();
    }

    if (prefix === "schedule") {
        updateScheduleDisciplineOptions();
    }
}


function editGroup(group) {
    openSection("groups");

    setFormMode(
        "group",
        group.id,
        "Изменить группу",
    );

    document.getElementById(
        "group-name",
    ).value = group.group_name;

    document.getElementById(
        "group-year",
    ).value = group.year;

    document.getElementById(
        "group-name",
    ).focus();
}


function editStudent(student) {
    openSection("students");

    setFormMode(
        "student",
        student.id,
        "Изменить студента",
    );

    document.getElementById(
        "student-name",
    ).value = student.full_name;

    document.getElementById(
        "student-email",
    ).value = student.email || "";

    document.getElementById(
        "student-group-id",
    ).value = String(student.group_id);

    document.getElementById(
        "student-name",
    ).focus();
}


function editDiscipline(discipline) {
    openSection("disciplines");

    setFormMode(
        "discipline",
        discipline.id,
        "Изменить дисциплину",
    );

    document.getElementById(
        "discipline-name",
    ).value = discipline.discipline_name;

    document.getElementById(
        "discipline-name",
    ).focus();
}


function editPlan(plan) {
    openSection("plans");

    setFormMode(
        "plan",
        plan.id,
        "Изменить учебный план",
    );

    document.getElementById(
        "plan-group-id",
    ).value = String(plan.group_id);

    document.getElementById(
        "plan-discipline-id",
    ).value = String(plan.discipline_id);

    document.getElementById(
        "plan-semester",
    ).value = plan.semester;
}


function editGrade(grade) {
    openSection("grades");

    setFormMode(
        "grade",
        grade.id,
        "Изменить оценку",
    );

    document.getElementById(
        "grade-student-id",
    ).value = String(grade.student_id);

    updateGradeDisciplineOptions(
        grade.discipline_id,
    );

    document.getElementById(
        "grade-value",
    ).value = grade.grade;
}


async function submitGroup(event) {
    event.preventDefault();

    const id = document.getElementById(
        "group-edit-id",
    ).value;

    const payload = {
        group_name: document.getElementById(
            "group-name",
        ).value.trim(),

        year: Number(
            document.getElementById(
                "group-year",
            ).value,
        ),
    };

    await saveEntity(
        "group",
        id,
        payload,
    );
}


async function submitStudent(event) {
    event.preventDefault();

    const id = document.getElementById(
        "student-edit-id",
    ).value;

    const email = document.getElementById(
        "student-email",
    ).value.trim();

    const payload = {
        full_name: document.getElementById(
            "student-name",
        ).value.trim(),

        email: email || null,

        group_id: Number(
            document.getElementById(
                "student-group-id",
            ).value,
        ),
    };

    await saveEntity(
        "student",
        id,
        payload,
    );
}


async function submitDiscipline(event) {
    event.preventDefault();

    const id = document.getElementById(
        "discipline-edit-id",
    ).value;

    const payload = {
        discipline_name: document.getElementById(
            "discipline-name",
        ).value.trim(),
    };

    await saveEntity(
        "discipline",
        id,
        payload,
    );
}


async function submitPlan(event) {
    event.preventDefault();

    const id = document.getElementById(
        "plan-edit-id",
    ).value;

    const payload = {
        group_id: Number(
            document.getElementById(
                "plan-group-id",
            ).value,
        ),

        discipline_id: Number(
            document.getElementById(
                "plan-discipline-id",
            ).value,
        ),

        semester: Number(
            document.getElementById(
                "plan-semester",
            ).value,
        ),
    };

    await saveEntity(
        "plan",
        id,
        payload,
    );
}


async function submitGrade(event) {
    event.preventDefault();

    const id = document.getElementById(
        "grade-edit-id",
    ).value;

    const payload = {
        student_id: Number(
            document.getElementById(
                "grade-student-id",
            ).value,
        ),

        discipline_id: Number(
            document.getElementById(
                "grade-discipline-id",
            ).value,
        ),

        grade: Number(
            document.getElementById(
                "grade-value",
            ).value,
        ),
    };

    await saveEntity(
        "grade",
        id,
        payload,
    );
}

function renderMyGrades() {
    const body = document.getElementById(
        "my-grades-table-body",
    );

    if (!body) {
        return;
    }

    body.replaceChildren();

    if (state.grades.length === 0) {
        showEmptyRow(
            body,
            4,
            "Оценки пока отсутствуют.",
        );

        return;
    }

    for (const grade of state.grades) {
        const row = document.createElement("tr");

        row.appendChild(
            makeCell(grade.id),
        );

        row.appendChild(
            makeCell(grade.discipline_name),
        );

        row.appendChild(
            makeCell(grade.grade),
        );

        row.appendChild(
            makeCell(grade.date),
        );

        body.appendChild(row);
    }
}

function renderUsers() {
    const body = document.getElementById(
        "users-table-body",
    );

    if (!body) {
        return;
    }

    body.replaceChildren();

    if (state.users.length === 0) {
        showEmptyRow(
            body,
            6,
            "Пользователи отсутствуют.",
        );

        return;
    }

    for (const user of state.users) {
        const row = document.createElement("tr");

        row.appendChild(
            makeCell(user.id),
        );

        row.appendChild(
            makeCell(user.username),
        );

        row.appendChild(
            makeCell(user.email),
        );


        const roleCell = document.createElement(
            "td",
        );

        const studentCell = document.createElement(
            "td",
        );

        const actionsCell = document.createElement(
            "td",
        );


        if (user.role === "admin") {
            roleCell.textContent = "Администратор";
            studentCell.textContent = "—";
            actionsCell.textContent = "Только CLI";
        } else {
            const roleSelect = document.createElement(
                "select",
            );

            roleSelect.dataset.userId = user.id;
            roleSelect.className = "user-role-select";

            const studentRole = document.createElement(
                "option",
            );

            studentRole.value = "student";
            studentRole.textContent = "Студент";

            const teacherRole = document.createElement(
                "option",
            );

            teacherRole.value = "teacher";
            teacherRole.textContent = "Преподаватель";

            roleSelect.append(
                studentRole,
                teacherRole,
            );

            roleSelect.value = user.role;

            roleCell.appendChild(roleSelect);


            const studentSelect = document.createElement(
                "select",
            );

            studentSelect.dataset.userId = user.id;
            studentSelect.className = (
                "user-student-select"
            );

            const emptyOption = document.createElement(
                "option",
            );

            emptyOption.value = "";
            emptyOption.textContent = "Не привязан";

            studentSelect.appendChild(
                emptyOption,
            );

            for (const student of state.students) {
                const option = document.createElement(
                    "option",
                );

                option.value = student.id;
                option.textContent = student.full_name;

                studentSelect.appendChild(option);
            }

            if (user.student_id !== null) {
                studentSelect.value = String(
                    user.student_id,
                );
            }

            studentSelect.disabled = (
                user.role !== "student"
            );

            roleSelect.addEventListener(
                "change",
                () => {
                    studentSelect.disabled = (
                        roleSelect.value !== "student"
                    );
                },
            );

            studentCell.appendChild(
                studentSelect,
            );


            const saveButton = document.createElement(
                "button",
            );

            saveButton.type = "button";

            saveButton.className = (
                "button "
                + "button-small "
                + "button-primary"
            );

            saveButton.textContent = "Сохранить";

            saveButton.addEventListener(
                "click",
                () => saveUserSettings(user.id),
            );

            actionsCell.appendChild(
                saveButton,
            );
        }

        row.appendChild(roleCell);
        row.appendChild(studentCell);
        row.appendChild(actionsCell);

        body.appendChild(row);
    }
}

async function saveUserSettings(userId) {
    const roleSelect = document.querySelector(
        `.user-role-select[data-user-id="${userId}"]`,
    );

    const studentSelect = document.querySelector(
        `.user-student-select[data-user-id="${userId}"]`,
    );

    if (!roleSelect) {
        return;
    }

    const role = roleSelect.value;

    try {
        await api(
            `/admin/users/${userId}/role`,
            {
                method: "PUT",

                headers: {
                    "Content-Type": "application/json",
                },

                body: JSON.stringify({
                    role: role,
                }),
            },
        );

        if (role === "student") {
            let studentId = null;

            if (
                studentSelect
                && studentSelect.value
            ) {
                studentId = Number(
                    studentSelect.value,
                );
            }

            await api(
                `/admin/users/${userId}/student`,
                {
                    method: "PUT",

                    headers: {
                        "Content-Type": "application/json",
                    },

                    body: JSON.stringify({
                        student_id: studentId,
                    }),
                },
            );
        }

        await loadAllData();

        showMessage(
            "Пользователь обновлён.",
            "success",
        );
    } catch (error) {
        showMessage(
            error.message,
            "error",
        );
    }
}

async function saveEntity(type, id, payload) {
    const paths = {
        group: "/groups",
        student: "/students",
        discipline: "/disciplines",
        plan: "/study_plans",
        grade: "/grades",
        schedule: "/schedules",
    };

    const basePath = paths[type];

    let url = basePath;
    let method = "POST";

    if (id) {
        url = `${basePath}/${id}`;
        method = "PUT";
    }

    try {
        await api(
            url,
            {
                method: method,

                headers: {
                    "Content-Type": "application/json",
                },

                body: JSON.stringify(payload),
            },
        );

        resetForm(type);

        await loadAllData();

        if (id) {
            showMessage(
                "Изменения сохранены.",
                "success",
            );
        } else {
            showMessage(
                "Запись добавлена.",
                "success",
            );
        }
    } catch (error) {
        showMessage(
            error.message,
            "error",
        );
    }
}


async function deleteEntity(
    type,
    id,
    label,
) {
    const paths = {
        group: "/groups",
        student: "/students",
        discipline: "/disciplines",
        plan: "/study_plans",
        grade: "/grades",
        schedule: "/schedules",
    };

    const confirmed = window.confirm(
        `Удалить ${label}?`,
    );

    if (!confirmed) {
        return;
    }

    try {
        await api(
            `${paths[type]}/${id}`,
            {
                method: "DELETE",
            },
        );

        await loadAllData();

        showMessage(
            "Запись удалена.",
            "success",
        );
    } catch (error) {
        showMessage(
            error.message,
            "error",
        );
    }
}


function showMessage(message, type) {
    const box = document.getElementById(
        "dashboard-message",
    );

    box.textContent = message;
    box.className = `dashboard-message ${type}`;
    box.hidden = false;
}


function clearMessage() {
    const box = document.getElementById(
        "dashboard-message",
    );

    box.hidden = true;
    box.textContent = "";
}

function bindIfExists(
    id,
    eventName,
    handler,
) {
    const element = document.getElementById(id);

    if (!element) {
        return;
    }

    element.addEventListener(
        eventName,
        handler,
    );
}

function bindEvents() {
    const navigationButtons = document.querySelectorAll(
        ".nav-button",
    );

    for (const button of navigationButtons) {
        button.addEventListener(
            "click",
            () => openSection(
                button.dataset.section,
            ),
        );
    }

    bindIfExists(
        "refresh-button",
        "click",
        loadAllData,
    );

    bindIfExists(
        "group-form",
        "submit",
        submitGroup,
    );

    bindIfExists(
        "student-form",
        "submit",
        submitStudent,
    );

    bindIfExists(
        "discipline-form",
        "submit",
        submitDiscipline,
    );

    bindIfExists(
        "plan-form",
        "submit",
        submitPlan,
    );

    bindIfExists(
        "grade-form",
        "submit",
        submitGrade,
    );

    bindIfExists(
        "grade-student-id",
        "change",
        () => updateGradeDisciplineOptions(),
    );

    bindIfExists(
        "group-cancel",
        "click",
        () => resetForm("group"),
    );

    bindIfExists(
        "student-cancel",
        "click",
        () => resetForm("student"),
    );

    bindIfExists(
        "discipline-cancel",
        "click",
        () => resetForm("discipline"),
    );

    bindIfExists(
        "plan-cancel",
        "click",
        () => resetForm("plan"),
    );

    bindIfExists(
        "grade-cancel",
        "click",
        () => resetForm("grade"),
    );

    bindIfExists(
        "schedule-form",
        "submit",
        submitSchedule,
    );

    bindIfExists(
        "schedule-group-id",
        "change",
        () => updateScheduleDisciplineOptions(),
    );

    bindIfExists(
        "schedule-cancel",
        "click",
        () => resetForm("schedule"),
    );
}


document.addEventListener(
    "DOMContentLoaded",
    async () => {
        bindEvents();
        openSection("overview");
        await loadAllData();
    },
);