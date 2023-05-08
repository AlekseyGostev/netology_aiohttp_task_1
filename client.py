import asyncio
import aiohttp
from aiohttp import ClientConnectorError


async def main():
    async with aiohttp.ClientSession() as session:
        # POST
        try:
            response = await session.post(
                'http://127.0.0.1:8080/ads/',
                json={
                    'title': 'Стол 26',
                    'description': 'Удобный стол',
                    'owner': 'Иванов'
                }
            )
        except ClientConnectorError as err:
            print(err)
        else:
            print(response.status)
            data = await response.text()
            print(data)

        # GET
        try:
            response = await session.get('http://127.0.0.1:8080/ads/5/')
        except ClientConnectorError as err:
            print(err)
        else:
            print(response.status)
            data = await response.text()
            print(data)

        # DELETE
        try:
            response = await session.delete('http://127.0.0.1:8080/ads/5/')
        except ClientConnectorError as err:
            print(err)
        else:
            print(response.status)
            data = await response.text()
            print(data)

asyncio.run(main())