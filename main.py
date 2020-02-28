import json
from datetime import datetime

from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application

# TODO Get Clockify API key and enter here
#   https://clockify.me/developers-api
api_key = "<secret_api_key>"
# TODO Get Clockify workspace ID and enter here
workspace_id = "<secret_workspace_id>"


async def request(url):
    req = HTTPRequest(
        url=f"https://api.clockify.me/api/v1/{url}",
        method="GET",
        headers={
            "Content-Type": "application/json",
            "X-Api-Key": api_key
        }
    )
    try:
        response = await AsyncHTTPClient().fetch(request=req)
    except Exception as e:
        print(e)
    else:
        return json.loads(response.body.decode("utf8"))


async def post(url, body):
    req = HTTPRequest(
        url=f"https://api.clockify.me/api/v1/{url}",
        method="POST",
        body=json.dumps(body),
        headers={
            "Content-Type": "application/json",
            "X-Api-Key": api_key
        }
    )
    try:
        response = await AsyncHTTPClient().fetch(request=req)
    except Exception as e:
        print(e)
    else:
        return json.loads(response.body.decode("utf8"))


class Main(RequestHandler):
    async def get(self):
        projects = await request(f"workspaces/{workspace_id}/projects")
        project_data = []
        for p in projects:
            project_data.append(dict(name=p["name"], client=p["clientName"], key=p["id"]))

        await self.render("clockify.html", projects=project_data)

    async def post(self):
        args = json.loads(self.request.body.decode("utf8"))
        await post(f"workspaces/{workspace_id}/time-entries",
                   dict(start=f"{datetime.utcnow().isoformat()}Z",
                        projectId=args["project"]))


def make_app():
    return Application([(r"/", Main)], **dict(compiled_template_cache=False))


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    print("Serving on http://localhost:8888/")
    IOLoop.current().start()
