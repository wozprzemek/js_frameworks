import httpx
from config import *
from typing import Dict
import asyncio
import time
import json
import re
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('API_KEY')

DEFAULT_MAX_QUOTA = 10000
SLEEP_TIME = 0.1
FRAMEWORK = 'react' # TODO change it to a script parameter

default_wrapper = [
    '.backoff',
    '.error_id',
    '.error_message',
    '.error_name',
    '.has_more',
    '.items',
    '.quota_max',
    '.quota_remaining',
]

filter_include_fields = [
    'question.score',
    'question.title',
    'question.body', 
    'question.view_count',
]

async def stack_api_wrapper(client, url, params={}):
    return await client.get(url, params={**params, 'key': ''})


async def create_filter(client: httpx.AsyncClient, include=[], exclude=[], base='none', unsafe='false'):
    response = await stack_api_wrapper(client, f'{STACK_API_URL}/filters/create', {
        **({'include': ';'.join(include)} if len(include) else {}),
        **({'exclude': ';'.join(exclude)} if len(exclude) else {}),
        'base': base,
        'unsafe': unsafe,
    })

    return response


async def fetch_asset(client: httpx.AsyncClient, asset: str, params: Dict[str, str], path: str = None):
    path_suffix = f'/{path}' if path is not None else ''
    return await stack_api_wrapper(client, f'{STACK_API_URL}/{asset}{path_suffix}', params=params)


def remove_code_blocks(body):
    pattern = re.compile(r'<pre.*?><code>.*?</code></pre>', re.DOTALL)
    return re.sub(pattern, '', body)


def remove_html_tags(body):
    soup = BeautifulSoup(body, 'html.parser')
    return soup.get_text()


def parse_response_items(items):
    return [{**item, 'body': remove_html_tags(remove_code_blocks(item['body']))} for item in items]


async def main():
    items = []
    async with httpx.AsyncClient() as client:
        filter_object = await create_filter(client, include=default_wrapper+filter_include_fields)
        filter = filter_object.json()['items'][0]['filter']

        has_more = True
        quota_remaining = DEFAULT_MAX_QUOTA
        fetched_items = ['placeholder']

        page_number = 1

        # loop to fetch all the data matching the parameters
        while len(fetched_items) > 0 and quota_remaining > 0:
            # fetch a page from the api
            result = (await fetch_asset(client, 'questions', {
                'tagged': FRAMEWORK,
                'order': 'desc',
                'sort': 'votes',
                'min': 0,                          # only positive score questions
                'pagesize': 100,                    # max page size in the stack api
                'page': page_number,
                'site': 'stackoverflow',
                'key': 'o8NPexS7k1uJzaaFQ)3wHg((',
                'filter': filter
            })).json()
            
            fetched_items = parse_response_items(result['items'])
            items += fetched_items
            has_more = result['has_more']
            quota_remaining = result['quota_remaining']

            # sleep to not exceed the api rate limit of 30 req/s
            print(f'page number: {page_number}; quota remaining: {quota_remaining}; has more: {has_more}')
            page_number += 1
            time.sleep(result['backoff'] if 'backoff' in result else SLEEP_TIME)

    with open(f'{FRAMEWORK}_stackoverflow.json', 'a') as fp:
        json.dump(items, fp)


if __name__ == '__main__':
    asyncio.run(main())