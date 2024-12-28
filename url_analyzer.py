import json

def handle(params):
    """Обрабатывает параметры и загружает файл на Яндекс.Диск"""
    data = json.loads(params)
    url = data['url']
    return json.dumps({'res': url.split('disk')[-1]}, ensure_ascii=False)

# params = {'url':"https://disk.yandex.ru/client/disk/test"}
# print(handle(params))