import json

from aiohttp import web
from pydantic import ValidationError

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models import Session, Ad, engine, Base
from schema import CreateAd, PatchAd


async def orm_context(app):
    print("START")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()
    print("SHUT DOWN")


@web.middleware
async def session_middleware(request: web.Request, handler):
    async with Session() as session:
        request['session'] = session
        response = await handler(request)
        return response


app = web.Application()
app.cleanup_ctx.append(orm_context)
app.middlewares.append(session_middleware)

def validate_ad(json_data: dict, model_class):
    try:
        model_item = model_class(**json_data)
        return model_item.dict(exclude_none=True)
    except ValidationError as err:
        raise web.HTTPBadRequest(
            text=json.dumps({'error': err.errors()}),
            content_type='application/json'
        )


async def get_ad(ad_id: int, session: Session) -> Ad:
    ad = await session.get(Ad, ad_id)
    if ad is None:
        raise web.HTTPNotFound(
            text=json.dumps({'error': 'Ad not found'}),
            content_type='application/json'
        )
    return ad


class AdView(web.View):

    @property
    def session(self) -> AsyncSession:
        return self.request['session']

    @property
    def ad_id(self) -> int:
        return int(self.request.match_info['ad_id'])

    async def get(self):
        ad = await get_ad(self.ad_id, self.session)
        return web.json_response({
                'id': ad.id,
                'title': ad.title,
                'description': ad.description,
                'creation_time': ad.creation_time.isoformat(),
                'owner': ad.owner,
            })

    async def delete(self):
        ad = await get_ad(self.ad_id, self.session)
        await self.session.delete(ad)
        self.session.commit()
        return web.json_response({'status': 'success'})

    async def patch(self):
        json_data = validate_ad(await self.request.json(), PatchAd)

        ad = await get_ad(self.ad_id, self.session)
        for field, value in json_data.items():
            setattr(ad, field, value)
        try:
            await self.session.commit()
        except IntegrityError as err:
            raise web.HTTPConflict(
                text=json.dumps({'error': 'title is busy'}),
                content_type='application/json'
            )

        return web.json_response({'id': ad.id})

    async def post(self):
        json_data = validate_ad(await self.request.json(), CreateAd)

        new_ad = Ad(**json_data)
        self.session.add(new_ad)
        try:
            await self.session.commit()
        except IntegrityError as err:
            raise web.HTTPConflict(
                text=json.dumps({'error': 'ad already exists'}),
                content_type='application/json'
            )

        return web.json_response({'id': new_ad.id})


app.add_routes([
    web.post('/ads/', AdView),
    web.get('/ads/{ad_id:\d+}/', AdView),
    web.patch('/ads/{ad_id:\d+}/', AdView),
    web.delete('/ads/{ad_id:\d+}/', AdView)
])


if __name__ == '__main__':
    web.run_app(app)


