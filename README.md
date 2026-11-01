# РиМРС: корзина с расширением на Lua

Лабораторная работа «Программа с расширениями». Основная программа на Python
показывает корзину и вызывает Lua-скрипт, который определяет скидку.
Сохранение скрипта меняет итоговую стоимость без перекомпиляции и перезапуска.

## Установка и запуск

Нужен Python 3.12. Выполняйте команды из каталога проекта.
Lua 5.4 встроен в библиотеку Lupa; устанавливать отдельный Lua не требуется.
Для установки зависимости нужен интернет. Собирать основную программу не нужно:
Python запускает исходный код, а Lupa устанавливается через pip.

Windows (PowerShell):

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

Linux/macOS:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python main.py
```

В PyCharm выберите интерпретатор созданного окружения и запустите `main.py`.
Путь к стандартному расширению считается от `main.py`, поэтому рабочий каталог
при запуске из IDE не важен. Все файлы сохраняйте в UTF-8.

Дополнительные режимы (здесь и далее `python` — интерпретатор окружения):

```bash
python main.py --once
python main.py --extension extensions/discount.lua
python -m unittest discover -s tests -v
```

`--once` делает один расчёт и завершает процесс: код 0 при успехе, 1 при ошибке
расширения. Без него программа проверяет файл каждые 0,5 секунды. Выход — Ctrl+C.