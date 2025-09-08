# Фильтр желтушных новостей

Пока поддерживается только один новостной сайт - [ИНОСМИ.РУ](https://inosmi.ru/). Для него разработан специальный адаптер, умеющий выделять текст статьи на фоне остальной HTML разметки. Для других новостных сайтов потребуются новые адаптеры, все они будут находиться в каталоге `adapters`. Туда же помещен код для сайта ИНОСМИ.РУ: `adapters/inosmi_ru.py`.

В перспективе можно создать универсальный адаптер, подходящий для всех сайтов, но его разработка будет сложной и потребует дополнительных времени и сил.

# Как установить

Вам понадобится Python версии 3.7 или старше. Для установки пакетов рекомендуется создать виртуальное окружение.

Первым шагом установите пакеты:

```python3
pip install -r requirements.txt
```

# Как запустить

1. Запускаете скрипт: `python python main.py`

2. В браузере вставляете (либо какие статьи вам нужны, после *urls=*): `http://127.0.0.1:8080/?urls=https://inosmi.ru/politic/20190629/245376799.html,https://inosmi.ru/20250904/svo-274525966.html,https://lenta.ru/brief/2021/08/26/afg_terror/,https://inosmi.rr/`

3. Кол-во url ссылок ограничено 10.

## Пример овтета:
```json
{
  "articles": [
    {
      "status": "PARSING_ERROR",
      "url": "https://lenta.ru/brief/2021/08/26/afg_terror/",
      "score": null,
      "words_count": null
    },
    {
      "status": "OK",
      "url": "https://inosmi.ru/politic/20190629/245376799.html",
      "score": 3.5,
      "words_count": 571
    },
    {
      "status": "OK",
      "url": "https://inosmi.ru/20250904/svo-274525966.html",
      "score": 1.07,
      "words_count": 657
    },
    {
      "status": "FETCH_ERROR",
      "url": "https://inosmi.rr/",
      "score": null,
      "words_count": null
    }
  ]
}
```

# Как запустить тесты

Для тестирования используется [pytest](https://docs.pytest.org/en/latest/), тестами покрыты фрагменты кода сложные в отладке: text_tools.py и адаптеры. Команды для запуска тестов:

```
python -m pytest adapters/inosmi_ru.py
```

```
python -m pytest text_tools.py
```

```
python -m pytest test_articles.py
```

# Цели проекта

Код написан в учебных целях. Это урок из курса по веб-разработке — [Девман](https://dvmn.org).
