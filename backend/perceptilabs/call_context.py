class CallContext(dict):
    @classmethod
    def from_flask_request(cls, request):
        auth_token = request.environ.get("auth_token")
        email = None
        user_id = None
        if auth_token:
            email = auth_token.get("email")
            user_id = auth_token.get("sub")

        d = {
            "auth_token": auth_token,
            "auth_token_raw": request.environ.get("auth_token_raw"),
            "user_email": email,
            "user_id": user_id,
        }

        # TODO: infer the project id when it's not in the request
        # .... or just the require project id every time

        body = request.get_json()
        if body:
            if "project_id" in body:
                d["project_id"] = body["project_id"]
            if "projectId" in body:
                d["project_id"] = body["projectId"]

        return cls(d)

    def push(self, **additions):
        return CallContext(
            {
                **self,
                **additions,
            }
        )

    # if we received the email in the call_context (e.g. with Keycloak), then use that. Otherwise use the user's id
    @property
    def user_unique_id(self):
        return self.get("user_email") or self.get("user_id")
