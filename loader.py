import json

from flask import request
from flask_restx import Namespace, Resource
from CTFd.api.v1.helpers.request import validate_args
from CTFd.models import db
from CTFd.plugins.personal_challenges import IndividualFlag

loader_namespace = Namespace("loader", description="Endpoint to retrieve Users")

@loader_namespace.route("")
class LoaderList(Resource):
    @validate_args({},"query",)
    def get(self,comment_id):
        if not len(request.args):
            return '404 Error Not Found'

        challange_id = str(request.args.get('challenge_id'))
        flag = str(request.args.get('flag'))
        user_id = str(request.args.get('user_id'))

        req = json.loads("{}")
        req["challenge_id"] = challange_id
        req["content"] = flag
        req["data"] = "Case Sensitive"
        req["type"] = "individual"
        req["user_id"] = user_id

        try:
            # fill IndividualFlags and Flags table
            FlagModel = IndividualFlag
            f = FlagModel(**req)
            db.session.add(f)
            db.session.commit()
            db.session.close()

        except Exception as e:
            return {"success": False, "message" : "Database Error :" + str(e)}

        return {"success": True, "Flag_data": req}
