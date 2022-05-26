# Game "rock Paper Scissors"
### Installation
- Клонируйте репозиторий на локальную машину и перейдите в рабочую директорию:
```
git clone https://github.com/Dert2/Game.git && cd Game
```
- Создайте и активируйте виртуальное окружение:
```
python -m venv venv
venv/scripts/activate
```
- Установите зависимости:
```
pip install -r requirements.txt
```
- Запустите сервер:
```
uvicorn main:app --reload 
```
Результаты игр и матчей будут приходить на весокет ендпоинты вида: ws://localhost:8000/ws/1 (где 1 - это battleId игры)
