import requests
import os
import re
from time import localtime, strftime


def get_cur_dir():
    """Возвращает путь к рабочей директории"""
    current_directory = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(current_directory, "tasks")
    return folder_path


def create_work_directory():
    """Создаёт рабочую директорию, если та не существует"""
    folder_path = get_cur_dir()
    if not os.path.isdir(folder_path):
        os.mkdir(folder_path)


def get_data():
        """Получает данные из json"""
        try:
            todos = requests.get("https://json.medrocket.ru/todos")
            users = requests.get("https://json.medrocket.ru/users")
            create_work_directory()
            return todos,users
        except requests.exceptions.RequestException:
            print('Проверьте подключение к интернету!')
            exit()


def form_sorted_user_info(users):
    """Форматирует полученную информацию о пользователях в виде списка словарей"""
    sorted_users = {}
    for d in users.json():                                          #Перебор данных user
        sorted_users[d.get('id')] = {'completed':[], 
                    'uncompleted': [], 
                    'name_company':(d.get('company').get('name')), 
                    'username': (d.get('username')), 
                    'name_user': (d.get('name')), 
                    'email': (d.get('email'))}
    return sorted_users


def sort_tasks_by_completion(todos,sorted_users):
    """Сортирует задачи на completed и uncompleted"""
    for u in todos.json():                                          #Перебор данных todo листа
        title = u.get('title')
        userId = u.get('userId')
        if None in (userId,title):
            continue
        title = title if len(title) <= 46 else title[:46] + '...'
        completed = u.get('completed')
        if completed:
            sorted_users[userId]['completed'].append(title)
        else:
            sorted_users[userId]['uncompleted'].append(title)
    return sorted_users


def create_files_and_add_info(sorted_users):
    """Создает файлы и добавляет информацию о пользователе и его задачах"""
    try:
        folder_path = get_cur_dir()
        for user_id in sorted_users:
            user_info = sorted_users[user_id]
            with open(f"{folder_path}\\{user_info['username']}.txt", "w") as file:
                file.write(f"# Отчёт для {user_info['name_company']}.\n")
                file.write(f"{user_info['name_user']} <{user_info['email']}> {strftime('%d.%m.%Y %H:%M', localtime())}\n")
                file.write(f"Всего задач: {len(user_info['completed']) + len(user_info['uncompleted'])}\n")
                file.write('\n')
                file.write(f"## Актуальные задачи ({len(user_info['uncompleted'])}):\n")
                for task in user_info['uncompleted']:
                    file.write(f'- {task}\n')
                file.write('\n')
                file.write(f"## Завершённые задачи ({len(user_info['completed'])}):\n")
                for task in user_info['completed']:
                    file.write(f'- {task}\n')
                file.write('\n')
    except Exception:
        print('Возникла ошибка при записи отчётов!')
        exit()
    

def rename_files(sorted_users):
    """Переименовывает файлы, если такие уже имеются"""
    try:
        folder_path = get_cur_dir()
        for user_id in sorted_users:
            user_info = sorted_users[user_id]
            if os.path.isfile(f"{folder_path}\\{user_info['username']}.txt") == True:
                with open(f"{folder_path}\\{user_info['username']}.txt", 'r') as file:
                        content = file.read()
                        date_pattern = r'\d{2}[.]\d{2}[.]\d{4}'                                     # Ищем дату и время в формате dd.mm.yyyy или hh:mm
                        time_pattern = r'\d{2}[:]\d{2}'
                        time = (re.search(time_pattern, content)).group()
                        date = (re.search(date_pattern, content)).group()
                        time = time.replace(':','.')                                                # Windows не разрешает ставить ":" в названии файла
                        date = str('-'.join(reversed(date.split('.'))) + 'T' + time)
                os.rename(f"{folder_path}\\{user_info['username']}.txt", f"{folder_path}\\old_{user_info['username']}_{date}.txt")
    except Exception:
        print('Возникла ошибка при переименовывании файла!')    


if __name__ == '__main__':
    todos, users =  get_data()
    sorted_users = form_sorted_user_info(users)
    sorted_todos = sort_tasks_by_completion(todos,sorted_users)
    rename_files(sorted_todos)
    create_files_and_add_info(sorted_todos)
    print('Программа успешно завершила свою работу!')



