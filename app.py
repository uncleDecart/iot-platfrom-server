from flask import Flask, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_cors import CORS
from flask_heroku import Heroku
from flask import jsonify

import datetime
import sys
import json
import ast

app = Flask( __name__ )
CORS(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
heroku = Heroku(app)
db = SQLAlchemy(app)


class DeviceLogEntry(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    d_id = db.Column(db.Integer())
    log = db.Column(db.String())
    date = db.Column(db.DateTime())

    def __init__(self, d_id, log):
        self.d_id = d_id
        self.log = log
        self.date = datetime.datetime.utcnow()


@app.route('/data', methods=['POST'])
def update():
    sel_id = int(request.form['d_id'])
    pf = DeviceLogEntry(
            sel_id,
            str(request.form.to_dict()))
    sub_q = DeviceLogEntry.query.filter_by(d_id=sel_id)
    if sub_q.count() >= 50:
        db.session.delete(sub_q.order_by(DeviceLogEntry.id).first())
    db.session.add(pf)
    db.session.commit()

    return ('', 200)

@app.route('/device_info')
def get_dev_info():
    sel_id = request.args.get('dev_id')
    res = []
    for i in DeviceLogEntry.query.filter_by(d_id=sel_id).all():
        res.append({"d_id" : i.d_id, "log" :  ast.literal_eval(i.log), "date" : i.date})
    return (jsonify(res), 200)

@app.route('/info')
def get_info():
    logs = DeviceLogEntry.query.all()
    return render_template('view_logs.html', logs=logs)

if __name__ == '__main__':
    app.run()
