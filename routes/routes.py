import quart

blueprint = quart.Blueprint('my_blueprint', __name__)


@blueprint.route('/')
async def hello():
    return {'key': 'value'}
