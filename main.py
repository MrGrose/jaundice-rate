import asyncio
import logging
import time
from contextlib import asynccontextmanager
from functools import partial

import aiohttp
import async_timeout
import pymorphy3
from aiohttp import web
from aiohttp.web_exceptions import HTTPBadRequest
from anyio import create_task_group

from adapters.exceptions import ArticleNotFound, ProcessingStatus
from adapters.inosmi_ru import sanitize
from text_tools import calculate_jaundice_rate, split_by_words

logger = logging.getLogger(__name__)


@asynccontextmanager
async def timer():
    start_time = time.monotonic()
    try:
        yield
    finally:
        logging.info(f"Анализ закончен за {time.monotonic() - start_time:3.2f} сек")


async def fetch(session, url):
    timeout = aiohttp.ClientTimeout(total=5)
    async with session.get(url, timeout=timeout) as response:
        response.raise_for_status()
        return await response.text()


def load_words():
    words = []
    for path_text in ["negative_words.txt", "positive_words.txt"]:
        with open(path_text, "r", encoding="utf-8") as file:
            text = file.read()
            words.extend(text.split())
    return words


@timer()
async def process_article(session, morph, charged_words, url, articles, delay):
    try:
        async with async_timeout.timeout(delay):
            html = await fetch(session, url)
            text_clean = sanitize(html)
            words = await split_by_words(morph, text_clean)
            words_count = len(words)
            score = calculate_jaundice_rate(words, charged_words)
            status = ProcessingStatus.OK

    except ArticleNotFound:
        score, words_count = None, None
        status = ProcessingStatus.PARSING_ERROR
        logger.error("Статья не найдена")

    except asyncio.TimeoutError:
        score, words_count = None, None
        status = ProcessingStatus.TIMEOUT
        logger.error("Время ожидания ответа истекло")

    except aiohttp.ClientError:
        score, words_count = None, None
        status = ProcessingStatus.FETCH_ERROR
        logger.error("Ошибка ответа от сервера")

    finally:
        articles.append(
            {
                "status": status.value,
                "url": url,
                "score": score,
                "words_count": words_count,

            }
        )


async def handle(request, morph, charged_words):
    urls_param = request.query.get("urls", "")
    urls = urls_param.split(",") if urls_param else []

    if len(urls) > 10:
        raise HTTPBadRequest(reason="много URL-адресов в запросе, должно быть 10 или меньше")

    articles = []
    delay = 5
    async with aiohttp.ClientSession() as session:
        try:
            async with create_task_group() as tg:
                for url in urls:
                    tg.start_soon(process_article, session, morph, charged_words, url, articles, delay)
        except* asyncio.TimeoutError as e:
            logging.error(f"Timeout: {e}")
        except* Exception as e:
            logging.exception(f"Ошибка: {e}")

    return web.json_response({"articles": articles})


if __name__ == "__main__":
    logging.basicConfig(filename="main_log.txt", format="%(asctime)s - %(levelname)s - %(message)s", level=logging.DEBUG)

    charged_words = load_words()
    morph = pymorphy3.MorphAnalyzer()

    app = web.Application()
    app.add_routes([web.get('/', partial(handle, morph=morph, charged_words=charged_words))])
    web.run_app(app)
