import requests
import json

def create_folder(token, folder_path):
    """Создаёт папку на Яндекс.Диске"""
    headers = {'Authorization': f'OAuth {token}'}
    base_url = 'https://cloud-api.yandex.net/v1/disk/resources'
    response = requests.put(base_url, headers=headers, params={'path': folder_path})
    if response.status_code in (201, 409):  # Папка создана или уже существует
        print(f'Папка {folder_path} готова.')
    else:
        print(f'Ошибка создания папки {folder_path}: {response.status_code} {response.text}')

def upload_file_from_url(token, file_url, remote_path):
    """Загружает файл из URL напрямую на Яндекс.Диск"""
    headers = {'Authorization': f'OAuth {token}'}
    base_url = 'https://cloud-api.yandex.net/v1/disk/resources'
    upload_url = f'{base_url}/upload'

    # Получаем URL для загрузки на Яндекс.Диск
    params = {'path': remote_path, 'overwrite': 'true'}
    response = requests.get(upload_url, headers=headers, params=params)

    if response.status_code == 200:
        upload_link = response.json().get('href')
        if not upload_link:
            print('Не удалось получить ссылку для загрузки файла.')
            return False

        # Потоковая загрузка файла из URL на Яндекс.Диск
        file_stream = requests.get(file_url, stream=True)
        if file_stream.status_code == 200:
            upload_response = requests.put(
                upload_link,
                data=file_stream.iter_content(chunk_size=1024),
                headers={'Content-Type': 'application/octet-stream'}
            )
            if upload_response.status_code == 201:
                print('Файл успешно загружен на Яндекс.Диск.')
                return True
            else:
                print(f'Ошибка загрузки файла: {upload_response.status_code} {upload_response.text}')
                return False
        else:
            print(f'Ошибка загрузки файла из URL: {file_stream.status_code} {file_stream.text}')
            return False
    elif response.status_code == 409:
        print(f'Путь {remote_path} не существует.')
        folder_path = remote_path.rsplit('/', 1)[0]  # Извлекаем путь к папке
        create_folder(token, folder_path)
        return upload_file_from_url(token, file_url, remote_path)  # Повторная загрузка
    else:
        print(f'Ошибка получения URL для загрузки: {response.status_code} {response.text}')
        return False

def handle(params):
    """Обрабатывает параметры и загружает файл на Яндекс.Диск"""
    data = json.loads(params)
    token = data['TOKEN']
    main_dir = data['main_dir'].replace('%20', ' ')
    file_url = data['file_path']
    file_name = data['file_name']
    if file_name == '':
        remote_path = f"disk:{main_dir}{file_url.split('.')[-2][-5:]}.{file_url.split('.')[-1]}"
        # Загружаем файл
        result = upload_file_from_url(token, file_url, remote_path)
        return json.dumps({'res': result})

    else:
        remote_path = f"disk:{main_dir}{file_name}"
        # Загружаем файл
        result = upload_file_from_url(token, file_url, remote_path)
        return json.dumps({'res': result})
