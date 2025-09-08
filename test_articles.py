import aiohttp
import pymorphy3
import pytest

from main import load_words, process_article


@pytest.mark.asyncio
async def test_process_article():
    morph = pymorphy3.MorphAnalyzer()
    charged_words = load_words()

    async def call_process_article(url, delay=5):
        articles = []
        async with aiohttp.ClientSession() as session:
            await process_article(session, morph, charged_words, url, articles, delay)
            return articles

    url = "https://inosmi.ru/politic/20190629/245376799.html"
    result = await call_process_article(url)
    assert result[0]["status"] == "OK"

    url = "https://inosmi.ru/20250904/svo-274525966.html"
    result = await call_process_article(url, delay=0.1)
    assert result[0]["status"] == "TIMEOUT"

    url = "https://lenta.ru/brief/2021/08/26/afg_terror/"
    result = await call_process_article(url)
    assert result[0]['status'] == 'PARSING_ERROR'

    url = "https://inosmi.rr/"
    result = await call_process_article(url)
    assert result[0]['status'] == "FETCH_ERROR"
