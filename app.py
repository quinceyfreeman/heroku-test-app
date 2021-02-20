import os
import config
from random import randint
from flask import Flask, abort, request, url_for
from mongoengine import connect, StringField, IntField, DateTimeField, Document
from datetime import datetime
app = Flask(__name__)


# app.config.from_object(config.Config)
# app.config.from_envvar('WOLFIT_SETTINGS')

dbname = (os.environ.get('MONGODB_URI'))
connect(host=dbname)

class ActivityLog(Document):
    user_id = IntField(required=True)
    username = StringField(required=True, max_length=64)
    timestamp = DateTimeField(default=datetime.utcnow())
    details = StringField(required=True)
    location = StringField(default='/api/activities')

    def to_json(self):
        return {
            "id": str(self.id),
            "user_id": self.user_id,
            "username": self.username,
            "timestamp": self.timestamp,
            "details": self.details,
            "location": self.location
        }


@app.route('/api/activities', methods=["GET"])
def get_activities():
    activities = []
    for log in ActivityLog.objects:
        ins = (log.to_json())
        activities.append(ins)
    return {"activities": activities}


@app.route('/api/activities/<string:log_id>', methods=["GET"])
def get_activity(log_id):
    try:
        log = ActivityLog.objects.get(id=log_id)
        return log.to_json()
    except AssertionError:
        abort(404)


@app.route('/api/activities', methods=["POST"])
def create_activity():
    if not request.json:
        abort(400)
    new_activity = request.get_json()
    if 'username' not in new_activity or 'details' not in new_activity or 'id' in new_activity:
        abort(400)

    new_activity['timestamp'] = datetime.utcnow()
    s = ActivityLog(**new_activity)
    s.save()

    url_endpoint = url_for('get_activity', log_id=str(s.id))
    new_activity['location'] = s.location = url_endpoint
    s.save()
    return new_activity, 201
