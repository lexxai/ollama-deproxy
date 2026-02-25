from starlette.requests import Request


def get_session(request: Request):
    app = request.app
    return app.state.session
