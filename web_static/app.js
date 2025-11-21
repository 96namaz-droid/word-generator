// Состояние приложения
let laddersCount = 0;
// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Устанавливаем текущую дату
    document.getElementById('date').valueAsDate = new Date();
    
    // Загружаем заказчиков
    loadCustomers();
    
    // Добавляем первую лестницу
    addLadder();
    
    // Обработчик изменения заказчика
    document.getElementById('customer').addEventListener('change', onCustomerChange);
    
    // Обработчик чекбокса "Соответствует проекту"
    document.getElementById('projectCompliant').addEventListener('change', function() {
        document.getElementById('projectNumberGroup').style.display = this.checked ? 'block' : 'none';
    });
    
    // Обработчик отправки формы
    document.getElementById('reportForm').addEventListener('submit', handleSubmit);
    
    updateStatus('Готов к работе');
});

// Загрузка списка заказчиков
async function loadCustomers() {
    try {
        const response = await fetch('/api/customers');
        const data = await response.json();
        
        if (data.success) {
            const datalist = document.getElementById('customersList');
            datalist.innerHTML = '';
            
            data.customers.forEach(customer => {
                const option = document.createElement('option');
                option.value = customer;
                datalist.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Ошибка загрузки заказчиков:', error);
    }
}

// Обработчик изменения заказчика
async function onCustomerChange(e) {
    const customer = e.target.value;
    if (!customer) return;
    
    try {
        updateStatus('Загрузка данных договора...');
        const response = await fetch(`/api/contract/${encodeURIComponent(customer)}`);
        const data = await response.json();
        
        if (data.success && data.data) {
            document.getElementById('objectAddress').value = data.data.object_full_address || '';
            updateStatus('Данные договора загружены');
        } else {
            updateStatus('Договор не найден');
        }
    } catch (error) {
        console.error('Ошибка загрузки договора:', error);
        updateStatus('Ошибка загрузки договора');
    }
}

// Добавление лестницы
function addLadder() {
    laddersCount++;
    const container = document.getElementById('laddersContainer');
    
    const ladderCard = document.createElement('div');
    ladderCard.className = 'ladder-card';
    ladderCard.id = `ladder-${laddersCount}`;
    ladderCard.innerHTML = `
        <div class="ladder-header">
            <h3 class="ladder-title">Вертикальная лестница №${laddersCount}</h3>
            ${laddersCount > 1 ? `<button type="button" class="btn btn-danger" onclick="removeLadder(${laddersCount})">✖ Удалить</button>` : ''}
        </div>
        
        <div class="form-group">
            <label>Название</label>
            <input type="text" name="ladder_${laddersCount}_name" class="ladder-name">
        </div>
        
        <div class="ladder-fields" id="ladder-fields-${laddersCount}">
            ${getVerticalFieldsTemplate()}
        </div>
        
        <div class="inspection-section">
            <h4>Визуальный осмотр</h4>
            <div class="checkbox-grid">
                <label class="checkbox-label">
                    <input type="checkbox" name="ladder_${laddersCount}_damage" class="ladder-damage">
                    Внешние повреждения
                </label>
                <label class="checkbox-label">
                    <input type="checkbox" name="ladder_${laddersCount}_mount_viol" class="ladder-mount-viol">
                    Нарушение крепления
                </label>
                <label class="checkbox-label">
                    <input type="checkbox" name="ladder_${laddersCount}_weld_viol" class="ladder-weld-viol">
                    Нарушение сварных швов
                </label>
                <label class="checkbox-label">
                    <input type="checkbox" name="ladder_${laddersCount}_paint" class="ladder-paint" checked>
                    Покрытие соответствует ГОСТ
                </label>
            </div>
        </div>
    `;
    
    container.appendChild(ladderCard);
    
    updateComplianceSection();
}

function getVerticalFieldsTemplate() {
    return `
        <div class="form-group">
            <label>Высота (м) <span class="required">*</span></label>
            <input type="number" step="0.01" class="ladder-height" required>
        </div>
        <div class="form-group">
            <label>Ширина (м) <span class="required">*</span></label>
            <input type="number" step="0.01" class="ladder-width" required>
        </div>
        <div class="form-group">
            <label>Кол-во ступеней <span class="required">*</span></label>
            <input type="number" class="ladder-steps" required>
        </div>
        <div class="form-group">
            <label>Точки крепления <span class="required">*</span></label>
            <input type="number" class="ladder-mounts" required>
        </div>
        <div class="form-group">
            <label>Между ступенями (м) <span class="required">*</span></label>
            <input type="number" step="0.01" class="ladder-step-dist" required>
        </div>
        <div class="form-group">
            <label>Площадка длина (м)</label>
            <input type="number" step="0.01" class="ladder-platform-l">
        </div>
        <div class="form-group">
            <label>Площадка ширина (м)</label>
            <input type="number" step="0.01" class="ladder-platform-w">
        </div>
        <div class="form-group">
            <label>Высота ограждения (м)</label>
            <input type="number" step="0.01" class="ladder-fence">
        </div>
        <div class="form-group">
            <label>Расст. от стены (м)</label>
            <input type="number" step="0.01" class="ladder-wall-dist">
        </div>
        <div class="form-group">
            <label>Расст. от земли (м)</label>
            <input type="number" step="0.01" class="ladder-ground-dist">
        </div>
    `;
}

// Удаление лестницы
function removeLadder(number) {
    const ladderCard = document.getElementById(`ladder-${number}`);
    if (ladderCard) {
        ladderCard.remove();
        updateComplianceSection();
    }
}

// Обновление секции соответствия нормам
function updateComplianceSection() {
    const container = document.getElementById('complianceContainer');
    container.innerHTML = '';
    
    const ladderCards = document.querySelectorAll('.ladder-card');
    
    ladderCards.forEach((card, index) => {
        const ladderId = card.id.replace('ladder-', '');
        const ladderNum = index + 1;
        const ladderName = card.querySelector('.ladder-name').value || `Лестница №${ladderNum}`;
        
        const violationsHTML = `
            <label class="checkbox-label">
                <input type="checkbox" class="violation-check" data-type="ladder_width">
                Ширина лестницы
            </label>
            <label class="checkbox-label">
                <input type="checkbox" class="violation-check" data-type="step_distance">
                Расстояние между ступенями
            </label>
            <label class="checkbox-label">
                <input type="checkbox" class="violation-check" data-type="wall_distance">
                Расстояние от стены
            </label>
            <label class="checkbox-label">
                <input type="checkbox" class="violation-check" data-type="ground_distance">
                Расстояние от земли
            </label>
            <label class="checkbox-label">
                <input type="checkbox" class="violation-check" data-type="platform_length">
                Длина площадки
            </label>
            <label class="checkbox-label">
                <input type="checkbox" class="violation-check" data-type="platform_width">
                Ширина площадки
            </label>
            <label class="checkbox-label">
                <input type="checkbox" class="violation-check" data-type="fence_height">
                Высота ограждения площадки
            </label>
            <label class="checkbox-label">
                <input type="checkbox" class="violation-check" data-type="ladder_fence">
                Ограждение лестницы
            </label>
            <label class="checkbox-label">
                <input type="checkbox" class="violation-check" data-type="mount_distance">
                Расстояние между упорами
            </label>
            <label class="checkbox-label">
                <input type="checkbox" class="violation-check" data-type="paint_coating">
                Защитное покрытие
            </label>
        `;
        
        const complianceItem = document.createElement('div');
        complianceItem.className = 'compliance-item';
        complianceItem.id = `compliance-${ladderId}`;
        complianceItem.innerHTML = `
            <h4>Лестница №${ladderNum}: ${ladderName}</h4>
            <label class="checkbox-label">
                <input type="checkbox" class="compliance-check" data-ladder="${ladderId}" checked>
                Соответствует ГОСТ Р 54253-2009
            </label>
            <div class="violations-section" id="violations-${ladderId}" style="display: none;">
                <h4 style="font-size: 0.875rem; margin-bottom: 0.5rem;">Что не соответствует:</h4>
                <div class="checkbox-grid">
                    ${violationsHTML}
                </div>
            </div>
        `;
        
        container.appendChild(complianceItem);
        
        // Обработчик чекбокса соответствия
        const complianceCheck = complianceItem.querySelector('.compliance-check');
        complianceCheck.addEventListener('change', function() {
            const violationsSection = document.getElementById(`violations-${this.dataset.ladder}`);
            violationsSection.style.display = this.checked ? 'none' : 'block';
        });
    });
}

// Получение погоды
async function updateWeather() {
    const statusSpan = document.getElementById('weatherStatus');
    statusSpan.textContent = '⏳ Получение данных...';
    updateStatus('Запрос погоды...');
    
    try {
        const response = await fetch('/api/weather');
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('temperature').value = data.data.temperature;
            document.getElementById('windSpeed').value = data.data.wind_speed;
            statusSpan.textContent = `✅ Обновлено: ${data.data.temperature}°C, ${data.data.wind_speed} м/с`;
            updateStatus('Погода обновлена');
        } else {
            statusSpan.textContent = '❌ Ошибка';
            alert('Не удалось получить данные о погоде');
        }
    } catch (error) {
        statusSpan.textContent = '❌ Ошибка';
        console.error('Ошибка получения погоды:', error);
        alert('Ошибка при получении погоды');
    }
}

// Обновление базы договоров
async function updateContracts() {
    updateStatus('Обновление базы договоров...');
    
    try {
        const response = await fetch('/api/contracts/update', { method: 'POST' });
        const data = await response.json();
        
        if (data.success) {
            alert(`База обновлена!\nДоговоров: ${data.stats.total_contracts}\nЗаказчиков: ${data.stats.unique_customers}`);
            await loadCustomers();
            updateStatus('База договоров обновлена');
        } else {
            alert(`Ошибка: ${data.error}`);
            updateStatus('Ошибка обновления базы');
        }
    } catch (error) {
        console.error('Ошибка обновления базы:', error);
        alert('Ошибка при обновлении базы договоров');
    }
}

// Сбор данных формы
function collectFormData() {
    const data = {
        date: document.getElementById('date').value,
        customer: document.getElementById('customer').value,
        object_full_address: document.getElementById('objectAddress').value,
        test_time: document.getElementById('testTime').value,
        temperature: document.getElementById('temperature').value || '',
        wind_speed: document.getElementById('windSpeed').value || '',
        ladders: [],
        ladders_compliance: {},
        project_compliant: document.getElementById('projectCompliant').checked,
        project_number: document.getElementById('projectNumber').value || ''
    };
    
    // Собираем данные лестниц
    const ladderCards = document.querySelectorAll('.ladder-card');
    ladderCards.forEach((card, index) => {
        const ladderId = card.id.replace('ladder-', '');
        
        const ladder = {
            number: index + 1,
            name: card.querySelector('.ladder-name').value || '',
            ladder_type: 'vertical',
            damage_found: card.querySelector('.ladder-damage').checked,
            mount_violation_found: card.querySelector('.ladder-mount-viol').checked,
            weld_violation_found: card.querySelector('.ladder-weld-viol').checked,
            paint_compliant: card.querySelector('.ladder-paint').checked
        };
        
        ladder.height = card.querySelector('.ladder-height')?.value || '';
        ladder.width = card.querySelector('.ladder-width')?.value || '';
        ladder.steps_count = card.querySelector('.ladder-steps')?.value || '';
        ladder.mount_points = card.querySelector('.ladder-mounts')?.value || '';
        ladder.step_distance = card.querySelector('.ladder-step-dist')?.value || '';
        ladder.platform_length = card.querySelector('.ladder-platform-l')?.value || '';
        ladder.platform_width = card.querySelector('.ladder-platform-w')?.value || '';
        ladder.fence_height = card.querySelector('.ladder-fence')?.value || '';
        ladder.wall_distance = card.querySelector('.ladder-wall-dist')?.value || '';
        ladder.ground_distance = card.querySelector('.ladder-ground-dist')?.value || '';
        
        data.ladders.push(ladder);
        
        // Собираем данные соответствия
        const complianceItem = document.getElementById(`compliance-${ladderId}`);
        if (complianceItem) {
            const complianceCheck = complianceItem.querySelector('.compliance-check');
            const compliant = complianceCheck.checked;
            
            const violations = {};
            if (!compliant) {
                complianceItem.querySelectorAll('.violation-check').forEach(checkbox => {
                    violations[checkbox.dataset.type] = checkbox.checked;
                });
            }
            
            data.ladders_compliance[index + 1] = {
                compliant: compliant,
                violations: violations,
                name: ladder.name
            };
        }
    });
    
    return data;
}

// Обработка отправки формы
async function handleSubmit(e) {
    e.preventDefault();
    
    updateStatus('Генерация отчёта...');
    
    const data = collectFormData();
    
    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            updateStatus('Отчёт успешно создан!');
            showSuccessModal(result.filename);
        } else {
            updateStatus('Ошибка валидации');
            showErrorModal(result.errors);
        }
    } catch (error) {
        console.error('Ошибка генерации:', error);
        updateStatus('Ошибка генерации');
        alert('Ошибка при генерации отчёта: ' + error.message);
    }
}

// Показать модальное окно ошибок
function showErrorModal(errors) {
    const modal = document.getElementById('errorModal');
    const errorList = document.getElementById('errorList');
    
    errorList.innerHTML = '';
    errors.forEach(error => {
        const li = document.createElement('li');
        li.textContent = error;
        errorList.appendChild(li);
    });
    
    modal.classList.add('active');
}

// Закрыть модальное окно ошибок
function closeErrorModal() {
    document.getElementById('errorModal').classList.remove('active');
}

// Показать модальное окно успеха
function showSuccessModal(filename) {
    const modal = document.getElementById('successModal');
    const message = document.getElementById('successMessage');
    const downloadLink = document.getElementById('downloadLink');
    
    message.textContent = `Документ успешно создан: ${filename}`;
    downloadLink.href = `/api/download/${filename}`;
    downloadLink.download = filename;
    
    modal.classList.add('active');
}

// Закрыть модальное окно успеха
function closeSuccessModal() {
    document.getElementById('successModal').classList.remove('active');
}

// Очистить форму
function clearForm() {
    if (confirm('Очистить все поля?')) {
        // Удаляем все лестницы
        const container = document.getElementById('laddersContainer');
        container.innerHTML = '';
        
        // Сбрасываем счетчик
        laddersCount = 0;
        
        // Очищаем основную форму
        document.getElementById('reportForm').reset();
        document.getElementById('date').valueAsDate = new Date();
        
        // Добавляем одну пустую лестницу
        addLadder();
        
        updateStatus('Форма очищена');
    }
}

// Обновить статус
function updateStatus(text) {
    document.getElementById('statusText').textContent = text;
}

