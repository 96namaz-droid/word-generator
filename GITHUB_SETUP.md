# Инструкция по загрузке в GitHub

## Шаг 1: Настройка Git (если еще не настроено)

Выполните следующие команды для настройки вашего имени и email:

```bash
git config --global user.name "Ваше Имя"
git config --global user.email "ваш@email.com"
```

Или только для этого репозитория:

```bash
git config user.name "Ваше Имя"
git config user.email "ваш@email.com"
```

## Шаг 2: Создание коммита

После настройки выполните:

```bash
git add .
git commit -m "Initial commit: Генератор Word-отчётов"
```

## Шаг 3: Создание репозитория на GitHub

1. Перейдите на https://github.com
2. Нажмите кнопку "New" или "+" → "New repository"
3. Введите название репозитория (например: `word-generator`)
4. Выберите Public или Private
5. НЕ добавляйте README, .gitignore или лицензию (они уже есть)
6. Нажмите "Create repository"

## Шаг 4: Подключение к GitHub и загрузка

После создания репозитория GitHub покажет инструкции. Выполните:

```bash
git remote add origin https://github.com/ВАШ_USERNAME/word-generator.git
git branch -M main
git push -u origin main
```

Или если используете SSH:

```bash
git remote add origin git@github.com:ВАШ_USERNAME/word-generator.git
git branch -M main
git push -u origin main
```

**Замените `ВАШ_USERNAME` на ваш GitHub username и `word-generator` на название вашего репозитория.**

## Готово!

После выполнения всех шагов ваш проект будет загружен в GitHub.

