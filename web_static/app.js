// Глобальные переменные
let ladderCount = 0;
let marchCount = 0;
let currentProtocolType = 'vertical';

// Инициализация
document.addEventListener('DOMContentLoaded', function() {
    try {
        console.log('Инициализация приложения...');
        
        // Проверка существования основных элементов
        const dateInput = document.getElementById('date');
        const protocolTypeSelect = document.getElementById('protocolType');
        const reportForm = document.getElementById('reportForm');
        const projectCompliantCheckbox = document.getElementById('projectCompliant');
        const projectNumberInput = document.getElementById('projectNumber');
        const customerInput = document.getElementById('customer');
        
        if (!reportForm) {
            console.error('ОШИБКА: Форма reportForm не найдена!');
            return;
        }
        console.log('✓ Форма reportForm найдена');
        
        // Установка текущей даты
        if (dateInput) {
            const today = new Date().toISOString().split('T')[0];
            dateInput.value = today;
            console.log('✓ Дата установлена:', today);
        } else {
            console.warn('Предупреждение: поле date не найдено');
        }
        
        // Обработчик изменения типа протокола
        if (protocolTypeSelect) {
            protocolTypeSelect.addEventListener('change', onProtocolTypeChange);
            console.log('✓ Обработчик изменения типа протокола привязан');
        } else {
            console.warn('Предупреждение: select protocolType не найден');
        }
        
        // Обработчик отправки формы - КРИТИЧЕСКИ ВАЖНО
        reportForm.addEventListener('submit', function(e) {
            console.log('Событие submit перехвачено на форме');
            handleSubmit(e);
        }, false);
        console.log('✓ Обработчик submit привязан к форме');
        
        // Дополнительная привязка к кнопке на случай, если форма не перехватывается
        const submitButton = reportForm.querySelector('button[type="submit"]');
        if (submitButton) {
            submitButton.addEventListener('click', function(e) {
                console.log('Кнопка submit нажата (обработчик click)');
                e.preventDefault();
                e.stopPropagation();
                // Создаем фиктивное событие submit и вызываем handleSubmit напрямую
                const fakeEvent = {
                    preventDefault: function() {},
                    stopPropagation: function() {},
                    target: reportForm,
                    currentTarget: reportForm
                };
                handleSubmit(fakeEvent);
            });
            console.log('✓ Дополнительный обработчик на кнопке привязан');
        }
        
        // Обработчик для соответствия проекту
        if (projectCompliantCheckbox && projectNumberInput) {
            projectCompliantCheckbox.addEventListener('change', function() {
                projectNumberInput.disabled = !this.checked;
            });
            console.log('✓ Обработчик соответствия проекту привязан');
        }
        
        // Обработчик выбора заказчика
        if (customerInput) {
            customerInput.addEventListener('change', onCustomerChange);
            customerInput.addEventListener('input', onCustomerInput);
            console.log('✓ Обработчики заказчика привязаны');
        }
        
        // Загрузка списка заказчиков
        loadCustomers();
        
        // Автоматическая загрузка погоды
        loadWeather();
        
        // Инициализация: добавляем первую лестницу для вертикального протокола
        onProtocolTypeChange();
        if (currentProtocolType === 'vertical') {
            addLadder();
        }
        
        console.log('✓ Инициализация завершена успешно');
    } catch (error) {
        console.error('КРИТИЧЕСКАЯ ОШИБКА при инициализации:', error);
        console.error('Stack trace:', error.stack);
        alert('Ошибка инициализации приложения. Проверьте консоль браузера (F12) для деталей.');
    }
});

// Загрузка списка заказчиков
async function loadCustomers() {
    try {
        const response = await fetch('/api/customers');
        const data = await response.json();
        const datalist = document.getElementById('customersList');
        datalist.innerHTML = '';
        data.customers.forEach(customer => {
            const option = document.createElement('option');
            option.value = customer;
            datalist.appendChild(option);
        });
    } catch (error) {
        console.error('Ошибка загрузки списка заказчиков:', error);
    }
}

// Обработчик изменения заказчика (при потере фокуса)
async function onCustomerChange(e) {
    const customer = e.target.value.trim();
    if (customer) {
        await loadCustomerContract(customer);
    }
}

// Обработчик ввода заказчика (с задержкой для автокомплита)
let customerInputTimeout;
function onCustomerInput(e) {
    clearTimeout(customerInputTimeout);
    customerInputTimeout = setTimeout(() => {
        const customer = e.target.value.trim();
        if (customer && document.activeElement === e.target) {
            loadCustomerContract(customer);
        }
    }, 500);
}

// Загрузка договора по заказчику
async function loadCustomerContract(customer) {
    try {
        const response = await fetch(`/api/customer/${encodeURIComponent(customer)}`);
        const data = await response.json();
        if (data.found && data.object_full_address) {
            document.getElementById('objectFullAddress').value = data.object_full_address;
        }
    } catch (error) {
        console.error('Ошибка загрузки договора:', error);
    }
}

// Загрузка погоды
async function loadWeather() {
    try {
        const response = await fetch('/api/weather');
        const data = await response.json();
        if (data.success) {
            document.getElementById('temperature').value = data.temperature;
            document.getElementById('windSpeed').value = data.wind_speed;
        }
    } catch (error) {
        console.error('Ошибка загрузки погоды:', error);
    }
}

// Переключение типа протокола
function onProtocolTypeChange() {
    currentProtocolType = document.getElementById('protocolType').value;
    
    // Скрываем все секции
    document.getElementById('verticalSection').style.display = 'none';
    document.getElementById('stairSection').style.display = 'none';
    document.getElementById('roofSection').style.display = 'none';
    document.getElementById('visualInspectionSection').style.display = 'none';
    document.getElementById('complianceSection').style.display = 'none';
    
    // Показываем нужные секции
    if (currentProtocolType === 'vertical') {
        document.getElementById('verticalSection').style.display = 'block';
        document.getElementById('visualInspectionSection').style.display = 'block';
        document.getElementById('complianceSection').style.display = 'block';
        if (ladderCount === 0) {
            addLadder();
        }
    } else if (currentProtocolType === 'stair') {
        document.getElementById('stairSection').style.display = 'block';
        document.getElementById('visualInspectionSection').style.display = 'block';
        document.getElementById('complianceSection').style.display = 'block';
        if (marchCount === 0) {
            addMarch();
        }
    } else if (currentProtocolType === 'roof') {
        document.getElementById('roofSection').style.display = 'block';
        document.getElementById('visualInspectionSection').style.display = 'block';
        document.getElementById('complianceSection').style.display = 'block';
    }
}

// Добавление лестницы
function addLadder() {
    ladderCount++;
    const container = document.getElementById('laddersContainer');
    const ladderDiv = document.createElement('div');
    ladderDiv.className = 'ladder-item';
    ladderDiv.id = `ladder-${ladderCount}`;
    
    ladderDiv.innerHTML = `
        <h3>Лестница №${ladderCount}</h3>
        ${ladderCount > 1 ? `<button type="button" class="delete-btn" onclick="removeLadder(${ladderCount})">✖ Удалить</button>` : ''}
        <div class="form-group">
            <label>Название:</label>
            <input type="text" name="ladder-${ladderCount}-name" placeholder="Лестница №${ladderCount}">
        </div>
        <div class="form-group">
            <label>Высота (м):</label>
            <input type="number" name="ladder-${ladderCount}-height" step="0.01" min="0.1" required>
        </div>
        <div class="form-group">
            <label>Ширина (м):</label>
            <input type="number" name="ladder-${ladderCount}-width" step="0.01" min="0.1" required>
        </div>
        <div class="form-group">
            <label>Количество ступеней:</label>
            <input type="number" name="ladder-${ladderCount}-steps_count" min="1" required>
        </div>
        <div class="form-group">
            <label>Количество точек крепления:</label>
            <input type="number" name="ladder-${ladderCount}-mount_points" min="1" required>
        </div>
        <div class="form-group">
            <label>Расстояние между ступенями (м):</label>
            <input type="number" name="ladder-${ladderCount}-step_distance" step="0.01" min="0.01" required>
        </div>
        <div class="form-group">
            <label>Длина площадки (м):</label>
            <input type="number" name="ladder-${ladderCount}-platform_length" step="0.01">
        </div>
        <div class="form-group">
            <label>Ширина площадки (м):</label>
            <input type="number" name="ladder-${ladderCount}-platform_width" step="0.01">
        </div>
        <div class="form-group">
            <label>Высота ограждения площадки (м):</label>
            <input type="number" name="ladder-${ladderCount}-fence_height" step="0.01">
        </div>
        <div class="form-group">
            <label>Расстояние от стены (м):</label>
            <input type="number" name="ladder-${ladderCount}-wall_distance" step="0.01">
        </div>
        <div class="form-group">
            <label>Расстояние от земли (м):</label>
            <input type="number" name="ladder-${ladderCount}-ground_distance" step="0.01">
        </div>
    `;
    
    container.appendChild(ladderDiv);
}

// Удаление лестницы
function removeLadder(num) {
    const ladderDiv = document.getElementById(`ladder-${num}`);
    if (ladderDiv) {
        ladderDiv.remove();
    }
}

// Добавление марша/площадки
function addMarch() {
    marchCount++;
    const container = document.getElementById('marchesContainer');
    const marchDiv = document.createElement('div');
    marchDiv.className = 'march-item';
    marchDiv.id = `march-${marchCount}`;
    
    marchDiv.innerHTML = `
        <h3>Элемент №${marchCount}</h3>
        ${marchCount > 1 ? `<button type="button" class="delete-btn" onclick="removeMarch(${marchCount})">✖ Удалить</button>` : ''}
        <div class="form-group">
            <label>
                <input type="checkbox" name="march-${marchCount}-has_march" checked onchange="toggleMarchFields(${marchCount})">
                Есть марш
            </label>
        </div>
        <div class="form-group">
            <label>
                <input type="checkbox" name="march-${marchCount}-has_platform" checked onchange="togglePlatformFields(${marchCount})">
                Есть площадка
            </label>
        </div>
        <div id="march-fields-${marchCount}">
            <h4>Параметры марша</h4>
            <div class="form-group">
                <label>Ширина марша (м):</label>
                <input type="number" name="march-${marchCount}-march_width" step="0.01" min="0.5" required>
            </div>
            <div class="form-group">
                <label>Длина марша (м):</label>
                <input type="number" name="march-${marchCount}-march_length" step="0.01" min="0.5" required>
            </div>
            <div class="form-group">
                <label>Ширина ступени (м):</label>
                <input type="number" name="march-${marchCount}-step_width" step="0.01" min="0.15" required>
            </div>
            <div class="form-group">
                <label>Расстояние между ступенями (м):</label>
                <input type="number" name="march-${marchCount}-step_distance" step="0.01" min="0.15" required>
            </div>
            <div class="form-group">
                <label>Количество ступеней:</label>
                <input type="number" name="march-${marchCount}-steps_count" min="1" required>
            </div>
            <div class="form-group">
                <label>Высота ограждений марша (м):</label>
                <input type="number" name="march-${marchCount}-march_fence_height" step="0.01" min="0.5" required>
            </div>
        </div>
        <div id="platform-fields-${marchCount}">
            <h4>Параметры площадки</h4>
            <div class="form-group">
                <label>Длина площадки (м):</label>
                <input type="number" name="march-${marchCount}-platform_length" step="0.01" min="0.5" required>
            </div>
            <div class="form-group">
                <label>Ширина площадки (м):</label>
                <input type="number" name="march-${marchCount}-platform_width" step="0.01" min="0.5" required>
            </div>
            <div class="form-group">
                <label>Высота ограждений площадки (м):</label>
                <input type="number" name="march-${marchCount}-platform_fence_height" step="0.01" min="0.5" required>
            </div>
            <div class="form-group">
                <label>Расстояние от площадки до земли (м):</label>
                <input type="number" name="march-${marchCount}-platform_ground_distance" step="0.01" min="0">
            </div>
        </div>
    `;
    
    container.appendChild(marchDiv);
}

// Удаление марша
function removeMarch(num) {
    const marchDiv = document.getElementById(`march-${num}`);
    if (marchDiv) {
        marchDiv.remove();
    }
}

// Переключение полей марша
function toggleMarchFields(num) {
    const checkbox = document.querySelector(`input[name="march-${num}-has_march"]`);
    const fields = document.getElementById(`march-fields-${num}`);
    const inputs = fields.querySelectorAll('input[type="number"]');
    
    inputs.forEach(input => {
        input.required = checkbox.checked;
        input.disabled = !checkbox.checked;
    });
}

// Переключение полей площадки
function togglePlatformFields(num) {
    const checkbox = document.querySelector(`input[name="march-${num}-has_platform"]`);
    const fields = document.getElementById(`platform-fields-${num}`);
    const inputs = fields.querySelectorAll('input[type="number"]');
    
    inputs.forEach(input => {
        input.required = checkbox.checked;
        input.disabled = !checkbox.checked;
    });
}

// Преобразование даты из YYYY-MM-DD в DD.MM.YYYY
function formatDate(dateStr) {
    if (!dateStr) return '';
    // Если дата уже в формате DD.MM.YYYY, возвращаем как есть
    if (dateStr.match(/^\d{2}\.\d{2}\.\d{4}$/)) {
        return dateStr;
    }
    // Преобразуем из YYYY-MM-DD в DD.MM.YYYY
    const parts = dateStr.split('-');
    if (parts.length === 3) {
        return `${parts[2]}.${parts[1]}.${parts[0]}`;
    }
    return dateStr;
}

// Сбор данных формы
function collectFormData() {
    const formData = new FormData(document.getElementById('reportForm'));
    const dateStr = formData.get('date');
    const data = {
        protocol_type: currentProtocolType,
        date: formatDate(dateStr),
        customer: formData.get('customer'),
        object_full_address: formData.get('object_full_address'),
        test_time: formData.get('test_time') || 'дневное время',
        temperature: formData.get('temperature') || '',
        wind_speed: formData.get('wind_speed') || '',
        project_compliant: formData.get('project_compliant') === 'on',
        project_number: formData.get('project_number') || '',
    };
    
    if (currentProtocolType === 'vertical') {
        data.ladders = [];
        for (let i = 1; i <= ladderCount; i++) {
            const ladderDiv = document.getElementById(`ladder-${i}`);
            if (ladderDiv) {
                data.ladders.push({
                    number: i,
                    name: formData.get(`ladder-${i}-name`) || '',
                    height: formData.get(`ladder-${i}-height`) || '',
                    width: formData.get(`ladder-${i}-width`) || '',
                    steps_count: formData.get(`ladder-${i}-steps_count`) || '',
                    mount_points: formData.get(`ladder-${i}-mount_points`) || '',
                    step_distance: formData.get(`ladder-${i}-step_distance`) || '',
                    platform_length: formData.get(`ladder-${i}-platform_length`) || '',
                    platform_width: formData.get(`ladder-${i}-platform_width`) || '',
                    fence_height: formData.get(`ladder-${i}-fence_height`) || '',
                    wall_distance: formData.get(`ladder-${i}-wall_distance`) || '',
                    ground_distance: formData.get(`ladder-${i}-ground_distance`) || '',
                    damage_found: formData.get('damage_found') === 'on',
                    mount_violation_found: formData.get('mount_violation_found') === 'on',
                    weld_violation_found: formData.get('weld_violation_found') === 'on',
                    paint_compliant: formData.get('paint_compliant') === 'on',
                });
            }
        }
        data.ladders_compliance = {};
    } else if (currentProtocolType === 'stair') {
        data.ladder_name = formData.get('ladder_name') || '';
        data.mount_points = formData.get('mount_points') || '';
        data.marches = [];
        for (let i = 1; i <= marchCount; i++) {
            const marchDiv = document.getElementById(`march-${i}`);
            if (marchDiv) {
                const hasMarch = formData.get(`march-${i}-has_march`) === 'on';
                const hasPlatform = formData.get(`march-${i}-has_platform`) === 'on';
                data.marches.push({
                    number: i,
                    has_march: hasMarch,
                    has_platform: hasPlatform,
                    march_width: hasMarch ? (formData.get(`march-${i}-march_width`) || '') : '',
                    march_length: hasMarch ? (formData.get(`march-${i}-march_length`) || '') : '',
                    step_width: hasMarch ? (formData.get(`march-${i}-step_width`) || '') : '',
                    step_distance: hasMarch ? (formData.get(`march-${i}-step_distance`) || '') : '',
                    steps_count: hasMarch ? (formData.get(`march-${i}-steps_count`) || '') : '',
                    march_fence_height: hasMarch ? (formData.get(`march-${i}-march_fence_height`) || '') : '',
                    platform_length: hasPlatform ? (formData.get(`march-${i}-platform_length`) || '') : '',
                    platform_width: hasPlatform ? (formData.get(`march-${i}-platform_width`) || '') : '',
                    platform_fence_height: hasPlatform ? (formData.get(`march-${i}-platform_fence_height`) || '') : '',
                    platform_ground_distance: hasPlatform ? (formData.get(`march-${i}-platform_ground_distance`) || '') : '',
                });
            }
        }
        data.damage_found = formData.get('damage_found') === 'on';
        data.mount_violation_found = formData.get('mount_violation_found') === 'on';
        data.weld_violation_found = formData.get('weld_violation_found') === 'on';
        data.paint_compliant = formData.get('paint_compliant') === 'on';
        data.project_compliant = formData.get('project_compliant') === 'on';
        data.project_number = formData.get('project_number') || '';
    } else if (currentProtocolType === 'roof') {
        data.fence_name = formData.get('fence_name') || '';
        data.length = formData.get('length') || '';
        data.height = formData.get('height') || '';
        data.mount_points_roof = formData.get('mount_points_roof') || '';
        data.mount_pitch = formData.get('mount_pitch') || '';
        data.parapet_height = formData.get('parapet_height') || '';
        data.damage_found = formData.get('damage_found') === 'on';
        data.mount_violation_found = formData.get('mount_violation_found') === 'on';
        data.weld_violation_found = formData.get('weld_violation_found') === 'on';
        data.paint_compliant = formData.get('paint_compliant') === 'on';
        data.project_compliant = formData.get('project_compliant') === 'on';
        data.project_number = formData.get('project_number') || '';
    }
    
    return data;
}

// Обработка отправки формы
async function handleSubmit(e) {
    console.log('=== ОБРАБОТЧИК SUBMIT ВЫЗВАН ===');
    console.log('Событие:', e);
    console.log('Target:', e.target);
    console.log('CurrentTarget:', e.currentTarget);
    
    // КРИТИЧЕСКИ ВАЖНО: предотвращаем стандартную отправку формы
    if (e && typeof e.preventDefault === 'function') {
        e.preventDefault();
    }
    if (e && typeof e.stopPropagation === 'function') {
        e.stopPropagation();
    }
    console.log('✓ preventDefault() вызван');
    
    // Объявляем переменные в области видимости функции для использования в finally
    let form, submitBtn, errorDiv, successDiv;
    
    // Получаем форму - может быть e.target или e.currentTarget
    form = e.target.tagName === 'FORM' ? e.target : e.currentTarget;
    if (!form || form.tagName !== 'FORM') {
        console.error('ОШИБКА: Не удалось найти форму!');
        const formById = document.getElementById('reportForm');
        if (!formById) {
            alert('Критическая ошибка: форма не найдена!');
            return;
        }
        form = formById;
    }
    console.log('✓ Форма найдена:', form.id);
    
    errorDiv = document.getElementById('errorMessage');
    successDiv = document.getElementById('successMessage');
    if (errorDiv) errorDiv.style.display = 'none';
    if (successDiv) successDiv.style.display = 'none';
    
    // Блокируем кнопку - ищем в форме
    submitBtn = form.querySelector('button[type="submit"]');
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = '⏳ Генерация...';
        console.log('✓ Кнопка заблокирована');
    } else {
        console.warn('Предупреждение: кнопка submit не найдена');
    }
    
    console.log('=== НАЧАЛО СБОРА ДАННЫХ ===');
    const data = collectFormData();
    console.log('=== СОБРАННЫЕ ДАННЫЕ ===');
    console.log(JSON.stringify(data, null, 2));
    
    // Проверка базовых полей
    if (!data.date || !data.customer || !data.object_full_address) {
        errorDiv.innerHTML = '<strong>Ошибка:</strong> Заполните обязательные поля: дата, заказчик, объект';
        errorDiv.style.display = 'block';
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = '📄 Сгенерировать отчёт';
        }
        return;
    }
    
    try {
        // Валидация
        console.log('=== НАЧАЛО ВАЛИДАЦИИ ===');
        const validateResponse = await fetch('/api/validate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });
        
        console.log('Статус валидации:', validateResponse.status);
        
        if (!validateResponse.ok) {
            let errorMessage = '';
            try {
                const errorData = await validateResponse.json();
                console.error('Ошибка валидации (JSON):', errorData);
                if (errorData.detail) {
                    if (Array.isArray(errorData.detail)) {
                        errorMessage = errorData.detail.map(err => {
                            if (typeof err === 'object' && err.loc && err.msg) {
                                return `${err.loc.join('.')}: ${err.msg}`;
                            }
                            return String(err);
                        }).join('\n');
                    } else if (typeof errorData.detail === 'object' && errorData.detail.errors) {
                        errorMessage = Array.isArray(errorData.detail.errors) 
                            ? errorData.detail.errors.join('\n')
                            : String(errorData.detail.errors);
                    } else {
                        errorMessage = String(errorData.detail);
                    }
                } else if (errorData.errors) {
                    errorMessage = Array.isArray(errorData.errors) 
                        ? errorData.errors.join('\n')
                        : String(errorData.errors);
                } else {
                    errorMessage = JSON.stringify(errorData);
                }
            } catch (e) {
                const errorText = await validateResponse.text();
                errorMessage = `Ошибка ${validateResponse.status}: ${errorText.substring(0, 500)}`;
            }
            throw new Error(errorMessage || `Ошибка валидации: ${validateResponse.status}`);
        }
        
        const validateResult = await validateResponse.json();
        console.log('=== РЕЗУЛЬТАТ ВАЛИДАЦИИ ===');
        console.log(JSON.stringify(validateResult, null, 2));
        
        if (!validateResult.valid) {
            const errorList = Array.isArray(validateResult.errors) 
                ? validateResult.errors 
                : [validateResult.errors || 'Неизвестная ошибка валидации'];
            errorDiv.innerHTML = '<strong>Ошибки валидации:</strong><ul>' + 
                errorList.map(err => `<li>${err}</li>`).join('') + 
                '</ul>';
            errorDiv.style.display = 'block';
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.textContent = '📄 Сгенерировать отчёт';
            }
            return;
        }
        
        // Генерация документа
        console.log('=== НАЧАЛО ГЕНЕРАЦИИ ===');
        const generateResponse = await fetch('/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });
        
        console.log('Статус генерации:', generateResponse.status, generateResponse.statusText);
        
        console.log('Ответ генерации:', generateResponse.status, generateResponse.statusText);
        
        if (!generateResponse.ok) {
            let errorMessage = 'Ошибка генерации документа';
            try {
                const errorData = await generateResponse.json();
                console.error('Детали ошибки генерации:', errorData);
                if (errorData.detail) {
                    if (Array.isArray(errorData.detail)) {
                        errorMessage = errorData.detail.map(err => {
                            if (typeof err === 'object' && err.loc && err.msg) {
                                return `${err.loc.join('.')}: ${err.msg}`;
                            }
                            return String(err);
                        }).join('\n');
                    } else if (typeof errorData.detail === 'object') {
                        if (errorData.detail.errors) {
                            errorMessage = Array.isArray(errorData.detail.errors)
                                ? errorData.detail.errors.join('\n')
                                : String(errorData.detail.errors);
                        } else if (errorData.detail.error) {
                            errorMessage = errorData.detail.error;
                        } else {
                            errorMessage = JSON.stringify(errorData.detail);
                        }
                    } else {
                        errorMessage = String(errorData.detail);
                    }
                } else if (errorData.errors) {
                    errorMessage = Array.isArray(errorData.errors)
                        ? errorData.errors.join('\n')
                        : String(errorData.errors);
                } else if (errorData.error) {
                    errorMessage = errorData.error;
                }
            } catch (e) {
                const errorText = await generateResponse.text();
                errorMessage = `Ошибка ${generateResponse.status}: ${errorText.substring(0, 500)}`;
            }
            throw new Error(errorMessage);
        }
        
        // Проверяем Content-Type ДО создания blob (headers доступны всегда)
        const contentType = generateResponse.headers.get('Content-Type') || '';
        console.log('Content-Type:', contentType);
        
        // Получаем blob ПЕРВЫМ делом (пока response еще не использован)
        console.log('Получение файла...');
        const blob = await generateResponse.blob();
        console.log('Размер файла:', blob.size, 'байт');
        
        // Проверяем, что это действительно файл Word или хотя бы бинарный
        if (blob.size === 0) {
            console.error('Получен пустой файл');
            throw new Error('Получен пустой файл от сервера');
        }
        
        // Проверяем Content-Type (но не критично, если blob не пустой и больше 0)
        if (contentType && !contentType.includes('application/vnd.openxmlformats') && !contentType.includes('application/octet-stream')) {
            // Если это не Word файл, проверим первые байты (DOCX файлы начинаются с PK\03\04 - это ZIP архив)
            const blobStart = await blob.slice(0, 4).arrayBuffer();
            const uint8Array = new Uint8Array(blobStart);
            // DOCX файлы начинаются с "PK" (50 4B в hex) - это ZIP архив
            const isZipFile = uint8Array[0] === 0x50 && uint8Array[1] === 0x4B;
            
            if (!isZipFile) {
                // Похоже на JSON или HTML ошибку - попробуем прочитать как текст
                // Клонируем blob для чтения текста (чтобы не потерять оригинальный blob)
                const textBlob = blob.slice();
                const text = await textBlob.text();
                if (text.trim().startsWith('{') || text.trim().startsWith('<')) {
                    console.error('Сервер вернул не файл:', text.substring(0, 500));
                    throw new Error('Сервер вернул ошибку вместо файла документа');
                }
            }
            // Иначе продолжаем - возможно браузер не передал правильный Content-Type
            console.warn('Неожиданный Content-Type, но продолжаем скачивание (похоже на DOCX)');
        }
        
        // Получаем имя файла из заголовка (headers доступны всегда)
        const contentDisposition = generateResponse.headers.get('Content-Disposition') || '';
        let filename = 'report.docx';
        
        if (contentDisposition) {
            // Сначала пробуем RFC 5987 формат (filename*=UTF-8''encoded_name)
            const rfc5987Match = contentDisposition.match(/filename\*=([^']+)''(.+?)(?:;|$)/i);
            if (rfc5987Match && rfc5987Match[2]) {
                try {
                    filename = decodeURIComponent(rfc5987Match[2]);
                    console.log('Имя файла из RFC 5987:', filename);
                } catch (e) {
                    console.warn('Ошибка декодирования RFC 5987 имени файла:', e);
                }
            } else {
                // Пробуем обычный формат (filename="file.docx" или filename=file.docx)
                const filenameMatch = contentDisposition.match(/filename=([^;]+)/i);
                if (filenameMatch && filenameMatch[1]) {
                    filename = filenameMatch[1].trim();
                    // Убираем кавычки если есть
                    filename = filename.replace(/^["']|["']$/g, '');
                    // Пробуем декодировать URL-encoding если есть
                    try {
                        filename = decodeURIComponent(filename);
                    } catch (e) {
                        // Если не URL-encoded, оставляем как есть
                    }
                    console.log('Имя файла из обычного формата:', filename);
                }
            }
        }
        
        console.log('Имя файла для скачивания:', filename);
        
        // Создаем ссылку для скачивания
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.style.display = 'none';
        
        // Добавляем в DOM, кликаем, удаляем
        document.body.appendChild(a);
        
        // Используем setTimeout для гарантии что элемент добавлен
        setTimeout(() => {
            a.click();
            
            // Очищаем после небольшой задержки
            setTimeout(() => {
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
            }, 100);
        }, 0);
        
        successDiv.innerHTML = '✓ Документ успешно сгенерирован и скачан!<br>✓ Отчет отправлен на email: 2728941@list.ru';
        successDiv.style.display = 'block';
        console.log('✓ Файл успешно скачан:', filename);
        
    } catch (error) {
        console.error('Ошибка генерации:', error);
        let errorMessage = error.message || 'Неизвестная ошибка';
        if (error.stack) {
            console.error('Stack trace:', error.stack);
        }
        errorDiv.innerHTML = '<strong>Ошибка:</strong><br>' + errorMessage.replace(/\n/g, '<br>');
        errorDiv.style.display = 'block';
    } finally {
        // Разблокируем кнопку - ищем её снова на случай, если переменная не была установлена
        if (!submitBtn && form) {
            submitBtn = form.querySelector('button[type="submit"]');
        }
        if (!submitBtn) {
            submitBtn = document.querySelector('#reportForm button[type="submit"]');
        }
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = '📄 Сгенерировать отчёт';
            console.log('✓ Кнопка разблокирована');
        } else {
            console.warn('Предупреждение: не удалось найти кнопку для разблокировки');
        }
    }
}

// Очистка формы
function clearForm() {
    if (confirm('Очистить все поля?')) {
        document.getElementById('reportForm').reset();
        document.getElementById('laddersContainer').innerHTML = '';
        document.getElementById('marchesContainer').innerHTML = '';
        ladderCount = 0;
        marchCount = 0;
        const today = new Date().toISOString().split('T')[0];
        document.getElementById('date').value = today;
        onProtocolTypeChange();
    }
}

