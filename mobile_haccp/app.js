"use strict";

const config = window.SAN_EPI_CONFIG || {};

const messageBox = document.getElementById("messageBox");
const loginSection = document.getElementById("loginSection");
const registerSection = document.getElementById("registerSection");
const appSection = document.getElementById("appSection");
const emailInput = document.getElementById("emailInput");
const passwordInput = document.getElementById("passwordInput");
const loginButton = document.getElementById("loginButton");
const openRegisterButton = document.getElementById("openRegisterButton");
const registerNameInput = document.getElementById("registerNameInput");
const registerEmailInput = document.getElementById("registerEmailInput");
const registerPasswordInput = document.getElementById("registerPasswordInput");
const registerPasswordConfirmInput = document.getElementById("registerPasswordConfirmInput");
const registerObjectInput = document.getElementById("registerObjectInput");
const registerDepartmentInput = document.getElementById("registerDepartmentInput");
const registerButton = document.getElementById("registerButton");
const backToLoginButton = document.getElementById("backToLoginButton");
const userName = document.getElementById("userName");
const userRole = document.getElementById("userRole");
const logoutButton = document.getElementById("logoutButton");
const objectSelect = document.getElementById("objectSelect");
const departmentSelect = document.getElementById("departmentSelect");
const equipmentSelect = document.getElementById("equipmentSelect");
const equipmentInfo = document.getElementById("equipmentInfo");
const dateInput = document.getElementById("dateInput");
const timeInput = document.getElementById("timeInput");
const temperatureInput = document.getElementById("temperatureInput");
const responsibleInput = document.getElementById("responsibleInput");
const correctiveActionInput = document.getElementById("correctiveActionInput");
const saveMeasurementButton = document.getElementById("saveMeasurementButton");
const refreshButton = document.getElementById("refreshButton");
const recordsList = document.getElementById("recordsList");

let supabaseClient = null;
let currentUser = null;
let currentProfile = null;
let equipmentMap = new Map();

function escapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

function createTextId() {
    if (window.crypto && typeof window.crypto.randomUUID === "function") {
        return window.crypto.randomUUID().replaceAll("-", "");
    }

    return Date.now().toString(16) + Math.random().toString(16).slice(2);
}

function showMessage(text, type = "success") {
    messageBox.textContent = text;
    messageBox.className = `message ${type}`;
}

function hideMessage() {
    messageBox.textContent = "";
    messageBox.className = "message hidden";
}

function setButtonLoading(button, loading, normalText, loadingText) {
    button.disabled = loading;
    button.textContent = loading ? loadingText : normalText;
}

function setCurrentDateAndTime() {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, "0");
    const day = String(now.getDate()).padStart(2, "0");
    const hours = String(now.getHours()).padStart(2, "0");
    const minutes = String(now.getMinutes()).padStart(2, "0");

    dateInput.value = `${year}-${month}-${day}`;
    timeInput.value = `${hours}:${minutes}`;
}

function resetSelect(selectElement, placeholder) {
    selectElement.innerHTML = "";

    const option = document.createElement("option");
    option.value = "";
    option.textContent = placeholder;
    selectElement.appendChild(option);
}

function fillSelect(selectElement, items, placeholder) {
    resetSelect(selectElement, placeholder);

    for (const item of items) {
        const option = document.createElement("option");
        option.value = item.id;
        option.textContent = item.name;
        selectElement.appendChild(option);
    }
}

function getRoleName(role) {
    const roleNames = {
        admin: "Администратор",
        manager: "Руководитель объекта",
        employee: "Сотрудник подразделения"
    };

    return roleNames[role] || role || "Пользователь";
}

function showLogin() {
    loginSection.classList.remove("hidden");
    registerSection.classList.add("hidden");
    appSection.classList.add("hidden");
    currentUser = null;
    currentProfile = null;
}

function showRegistration() {
    hideMessage();
    loginSection.classList.add("hidden");
    registerSection.classList.remove("hidden");
    appSection.classList.add("hidden");
    registerNameInput.focus();
}

function showApplication() {
    loginSection.classList.add("hidden");
    registerSection.classList.add("hidden");
    appSection.classList.remove("hidden");
}

async function loadProfile() {
    const { data, error } = await supabaseClient
        .from("profiles")
        .select("id, full_name, role, object_id, department_id, active")
        .eq("id", currentUser.id)
        .single();

    if (error) {
        throw new Error(`Не удалось загрузить профиль: ${error.message}`);
    }

    if (!data.active) {
        throw new Error(
            "Ваш аккаунт ещё не активирован или отключён администратором."
        );
    }

    currentProfile = data;
    userName.textContent = data.full_name || "Пользователь";
    userRole.textContent = getRoleName(data.role);
    responsibleInput.value = data.full_name || "";
}

async function loadObjects() {
    resetSelect(objectSelect, "Загрузка объектов...");
    objectSelect.disabled = true;

    const { data, error } = await supabaseClient
        .from("haccp_objects")
        .select("id, name")
        .eq("active", true)
        .order("name");

    if (error) {
        throw new Error(`Ошибка загрузки объектов: ${error.message}`);
    }

    fillSelect(objectSelect, data || [], "Выберите объект");
    objectSelect.disabled = false;

    if (
        currentProfile.object_id
        && (data || []).some((item) => item.id === currentProfile.object_id)
    ) {
        objectSelect.value = currentProfile.object_id;
        await loadDepartments(currentProfile.object_id);
    }

    if (!data || data.length === 0) {
        showMessage("Для вашего аккаунта объект ещё не назначен.", "warning");
    }
}

async function loadDepartments(objectId) {
    resetSelect(departmentSelect, "Загрузка подразделений...");
    resetSelect(equipmentSelect, "Выберите оборудование");
    departmentSelect.disabled = true;
    equipmentSelect.disabled = true;
    equipmentInfo.classList.add("hidden");

    if (!objectId) {
        resetSelect(departmentSelect, "Выберите подразделение");
        return;
    }

    const { data, error } = await supabaseClient
        .from("haccp_departments")
        .select("id, name, category")
        .eq("object_id", objectId)
        .eq("active", true)
        .order("category")
        .order("name");

    if (error) {
        showMessage(`Ошибка подразделений: ${error.message}`, "error");
        return;
    }

    fillSelect(departmentSelect, data || [], "Выберите подразделение");
    departmentSelect.disabled = false;

    if (
        currentProfile.department_id
        && (data || []).some((item) => item.id === currentProfile.department_id)
    ) {
        departmentSelect.value = currentProfile.department_id;
        await loadEquipment(currentProfile.department_id);
    }
}

async function loadEquipment(departmentId) {
    resetSelect(equipmentSelect, "Загрузка оборудования...");
    equipmentSelect.disabled = true;
    equipmentInfo.classList.add("hidden");
    equipmentMap.clear();

    if (!departmentId) {
        resetSelect(equipmentSelect, "Выберите оборудование");
        return;
    }

    const columns = [
        "id",
        "name",
        "equipment_type",
        "location",
        "temperature_min",
        "temperature_max",
        "responsible",
        "control_times"
    ].join(", ");

    const { data, error } = await supabaseClient
        .from("haccp_equipment")
        .select(columns)
        .eq("department_id", departmentId)
        .eq("active", true)
        .order("name");

    if (error) {
        showMessage(`Ошибка оборудования: ${error.message}`, "error");
        return;
    }

    for (const item of data || []) {
        equipmentMap.set(item.id, item);
    }

    fillSelect(equipmentSelect, data || [], "Выберите оборудование");
    equipmentSelect.disabled = false;

    if (!data || data.length === 0) {
        showMessage("В этом подразделении оборудование не добавлено.", "warning");
    }
}

function showEquipmentInfo() {
    const equipment = equipmentMap.get(equipmentSelect.value);

    if (!equipment) {
        equipmentInfo.innerHTML = "";
        equipmentInfo.classList.add("hidden");
        return;
    }

    const minimum = Number(equipment.temperature_min);
    const maximum = Number(equipment.temperature_max);
    const times = Array.isArray(equipment.control_times)
        ? equipment.control_times.join(", ")
        : "—";

    equipmentInfo.innerHTML = `
        <strong>${escapeHtml(equipment.name)}</strong><br>
        Тип: ${escapeHtml(equipment.equipment_type || "—")}<br>
        Местонахождение: ${escapeHtml(equipment.location || "—")}<br>
        Допустимый диапазон: ${escapeHtml(minimum)} °C — ${escapeHtml(maximum)} °C<br>
        Время контроля: ${escapeHtml(times)}
    `;

    equipmentInfo.classList.remove("hidden");

    if (equipment.responsible && !responsibleInput.value.trim()) {
        responsibleInput.value = equipment.responsible;
    }
}

async function loadRecords() {
    recordsList.innerHTML = '<div class="empty">Загрузка записей...</div>';

    const { data, error } = await supabaseClient
        .from("haccp_temperature_records")
        .select(
            [
                "id",
                "object_id",
                "department_id",
                "equipment_id",
                "measurement_date",
                "measurement_time",
                "temperature",
                "temperature_min",
                "temperature_max",
                "status",
                "responsible",
                "corrective_action",
                "created_at"
            ].join(", ")
        )
        .order("measurement_date", { ascending: false })
        .order("measurement_time", { ascending: false })
        .limit(20);

    if (error) {
        recordsList.innerHTML = '<div class="empty">Не удалось загрузить журнал.</div>';
        showMessage(`Ошибка журнала: ${error.message}`, "error");
        return;
    }

    if (!data || data.length === 0) {
        recordsList.innerHTML = '<div class="empty">Записей пока нет.</div>';
        return;
    }

    const objectIds = [...new Set(data.map((item) => item.object_id).filter(Boolean))];
    const departmentIds = [...new Set(data.map((item) => item.department_id).filter(Boolean))];
    const equipmentIds = [...new Set(data.map((item) => item.equipment_id).filter(Boolean))];

    const [objectsResult, departmentsResult, equipmentResult] = await Promise.all([
        objectIds.length
            ? supabaseClient.from("haccp_objects").select("id, name").in("id", objectIds)
            : Promise.resolve({ data: [], error: null }),
        departmentIds.length
            ? supabaseClient.from("haccp_departments").select("id, name").in("id", departmentIds)
            : Promise.resolve({ data: [], error: null }),
        equipmentIds.length
            ? supabaseClient.from("haccp_equipment").select("id, name").in("id", equipmentIds)
            : Promise.resolve({ data: [], error: null })
    ]);

    const objectNames = new Map((objectsResult.data || []).map((item) => [item.id, item.name]));
    const departmentNames = new Map((departmentsResult.data || []).map((item) => [item.id, item.name]));
    const equipmentNames = new Map((equipmentResult.data || []).map((item) => [item.id, item.name]));

    recordsList.innerHTML = data.map((record) => {
        const normal = record.status === "Норма";
        const cardClass = normal ? "record normal" : "record deviation";
        const statusIcon = normal ? "✅" : "❌";
        const action = record.corrective_action
            ? `<div><strong>Корректирующее действие:</strong> ${escapeHtml(record.corrective_action)}</div>`
            : "";

        return `
            <article class="${cardClass}">
                <div class="record-title">
                    ${statusIcon} ${escapeHtml(record.measurement_date)}
                    ${escapeHtml(String(record.measurement_time || "").slice(0, 5))}
                    — ${escapeHtml(equipmentNames.get(record.equipment_id) || "Оборудование")}
                </div>
                <div><strong>Объект:</strong> ${escapeHtml(objectNames.get(record.object_id) || "—")}</div>
                <div><strong>Подразделение:</strong> ${escapeHtml(departmentNames.get(record.department_id) || "—")}</div>
                <div><strong>Температура:</strong> ${escapeHtml(record.temperature)} °C</div>
                <div><strong>Диапазон:</strong> ${escapeHtml(record.temperature_min)} °C — ${escapeHtml(record.temperature_max)} °C</div>
                <div><strong>Статус:</strong> ${escapeHtml(record.status)}</div>
                <div><strong>Ответственный:</strong> ${escapeHtml(record.responsible || "—")}</div>
                ${action}
            </article>
        `;
    }).join("");
}

async function saveMeasurement() {
    hideMessage();

    const objectId = objectSelect.value;
    const departmentId = departmentSelect.value;
    const equipmentId = equipmentSelect.value;
    const measurementDate = dateInput.value;
    const measurementTime = timeInput.value;
    const temperatureText = temperatureInput.value.trim().replace(",", ".");
    const responsible = responsibleInput.value.trim();
    const correctiveAction = correctiveActionInput.value.trim();
    const equipment = equipmentMap.get(equipmentId);

    if (!objectId || !departmentId || !equipmentId || !equipment) {
        showMessage("Выберите объект, подразделение и оборудование.", "warning");
        return;
    }

    if (!measurementDate || !measurementTime) {
        showMessage("Укажите дату и время измерения.", "warning");
        return;
    }

    if (temperatureText === "") {
        showMessage("Введите измеренную температуру.", "warning");
        return;
    }

    const temperature = Number(temperatureText);
    const minimum = Number(equipment.temperature_min);
    const maximum = Number(equipment.temperature_max);

    if (!Number.isFinite(temperature)) {
        showMessage("Температура должна быть числом.", "warning");
        return;
    }

    if (!responsible) {
        showMessage("Укажите ответственного сотрудника.", "warning");
        return;
    }

    const status = temperature >= minimum && temperature <= maximum
        ? "Норма"
        : "Отклонение";

    if (status === "Отклонение" && !correctiveAction) {
        showMessage(
            "При отклонении обязательно укажите корректирующее действие.",
            "warning"
        );
        correctiveActionInput.focus();
        return;
    }

    setButtonLoading(
        saveMeasurementButton,
        true,
        "💾 Сохранить измерение",
        "⏳ Сохранение..."
    );

    const record = {
        id: createTextId(),
        object_id: objectId,
        department_id: departmentId,
        equipment_id: equipmentId,
        measurement_date: measurementDate,
        measurement_time: measurementTime,
        temperature,
        temperature_min: minimum,
        temperature_max: maximum,
        status,
        responsible,
        corrective_action: correctiveAction
    };

    const { error } = await supabaseClient
        .from("haccp_temperature_records")
        .insert(record);

    setButtonLoading(
        saveMeasurementButton,
        false,
        "💾 Сохранить измерение",
        "⏳ Сохранение..."
    );

    if (error) {
        if (error.code === "23505") {
            showMessage(
                "Для этого оборудования на выбранные дату и время запись уже существует.",
                "warning"
            );
        } else {
            showMessage(`Ошибка сохранения: ${error.message}`, "error");
        }
        return;
    }

    temperatureInput.value = "";
    correctiveActionInput.value = "";
    setCurrentDateAndTime();
    showMessage(`Измерение сохранено. Статус: ${status}.`, status === "Норма" ? "success" : "warning");
    await loadRecords();
}

async function login() {
    hideMessage();

    const email = emailInput.value.trim();
    const password = passwordInput.value;

    if (!email || !password) {
        showMessage("Введите электронную почту и пароль.", "warning");
        return;
    }

    setButtonLoading(loginButton, true, "Войти", "Вход...");

    const { data, error } = await supabaseClient.auth.signInWithPassword({
        email,
        password
    });

    setButtonLoading(loginButton, false, "Войти", "Вход...");

    if (error) {
        showMessage("Неверная электронная почта или пароль.", "error");
        return;
    }

    currentUser = data.user;
    passwordInput.value = "";

    try {
        await startUserSession();
    } catch (sessionError) {
        showMessage(sessionError.message, "error");
        await supabaseClient.auth.signOut();
        showLogin();
    }
}

async function register() {
    hideMessage();

    const fullName = registerNameInput.value.trim();
    const email = registerEmailInput.value.trim();
    const password = registerPasswordInput.value;
    const passwordConfirm = registerPasswordConfirmInput.value;
    const requestedObject = registerObjectInput.value.trim();
    const requestedDepartment = registerDepartmentInput.value.trim();

    if (
        !fullName
        || !email
        || !password
        || !passwordConfirm
        || !requestedObject
        || !requestedDepartment
    ) {
        showMessage("Заполните все поля регистрации.", "warning");
        return;
    }

    if (password.length < 6) {
        showMessage("Пароль должен содержать минимум 6 символов.", "warning");
        return;
    }

    if (password !== passwordConfirm) {
        showMessage("Введённые пароли не совпадают.", "warning");
        return;
    }

    setButtonLoading(
        registerButton,
        true,
        "Создать аккаунт",
        "Регистрация..."
    );

    const { error } = await supabaseClient.auth.signUp({
        email,
        password,
        options: {
            data: {
                full_name: fullName,
                requested_object: requestedObject,
                requested_department: requestedDepartment
            }
        }
    });

    setButtonLoading(
        registerButton,
        false,
        "Создать аккаунт",
        "Регистрация..."
    );

    if (error) {
        const message = error.message.toLowerCase().includes("already")
            ? "Аккаунт с такой почтой уже существует."
            : `Ошибка регистрации: ${error.message}`;

        showMessage(message, "error");
        return;
    }

    await supabaseClient.auth.signOut();

    registerNameInput.value = "";
    registerEmailInput.value = "";
    registerPasswordInput.value = "";
    registerPasswordConfirmInput.value = "";
    registerObjectInput.value = "";
    registerDepartmentInput.value = "";

    showLogin();
    showMessage(
        "Аккаунт создан. Если на почту пришло письмо, подтвердите её. "
        + "Затем дождитесь активации администратора.",
        "success"
    );
}

async function logout() {
    await supabaseClient.auth.signOut();
    showLogin();
    showMessage("Вы вышли из системы.", "success");
}

async function startUserSession() {
    await loadProfile();
    showApplication();
    setCurrentDateAndTime();
    await loadObjects();
    await loadRecords();
}

async function refreshData() {
    hideMessage();
    setButtonLoading(refreshButton, true, "🔄 Обновить", "⏳ Обновление...");

    try {
        await loadObjects();
        await loadRecords();
        showMessage("Данные обновлены.", "success");
    } catch (error) {
        showMessage(error.message, "error");
    } finally {
        setButtonLoading(refreshButton, false, "🔄 Обновить", "⏳ Обновление...");
    }
}

async function initialize() {
    try {
        if (!config.supabaseUrl || !config.supabaseKey) {
            throw new Error("В config.js не указаны адрес Supabase и publishable key.");
        }

        if (!window.supabase || typeof window.supabase.createClient !== "function") {
            throw new Error("Библиотека Supabase не загрузилась. Проверьте интернет.");
        }

        supabaseClient = window.supabase.createClient(
            config.supabaseUrl,
            config.supabaseKey
        );

        setCurrentDateAndTime();

        const { data, error } = await supabaseClient.auth.getSession();

        if (error) {
            throw error;
        }

        if (data.session && data.session.user) {
            currentUser = data.session.user;
            await startUserSession();
        } else {
            showLogin();
        }
    } catch (error) {
        showLogin();
        showMessage(error.message || String(error), "error");
    }
}

loginButton.addEventListener("click", login);
openRegisterButton.addEventListener("click", showRegistration);
backToLoginButton.addEventListener("click", () => {
    hideMessage();
    showLogin();
});
registerButton.addEventListener("click", register);

passwordInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
        login();
    }
});

registerPasswordConfirmInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
        register();
    }
});

logoutButton.addEventListener("click", logout);

objectSelect.addEventListener("change", async () => {
    await loadDepartments(objectSelect.value);
});

departmentSelect.addEventListener("change", async () => {
    await loadEquipment(departmentSelect.value);
});

equipmentSelect.addEventListener("change", showEquipmentInfo);
saveMeasurementButton.addEventListener("click", saveMeasurement);
refreshButton.addEventListener("click", refreshData);

initialize();
