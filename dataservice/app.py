from flask import Flask, render_template, jsonify, request
import requests
from flask_sqlalchemy import SQLAlchemy
import json
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)

class Marker(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    lat = db.Column(db.Float, nullable=False)
    lng = db.Column(db.Float, nullable=False)
    name = db.Column(db.String(80))
    people = db.Column(db.Integer, nullable=False)
    time = db.Column(db.Integer, nullable=False)

    def serialize(self):
        return {
            'id': self.id, 
            'lat': self.lat,
            'lng': self.lng,
            'name':self.name,
            'people':self.people,
            'time':self.time,
            'color':self.color
        }

    def __repr__(self):
        return '<Marker %r>' % self.username


@app.route('/farmacie', methods = ['GET', 'PUT'])
def users():
    if request.method == 'GET':
        #result = Marker.query.filter_by(name='curotuttoio').first()
        result = Marker.query.order_by(Marker.people).all()
        n = len(result)
        for i,res in enumerate(result) :
            if i <= 0.25 * n :
                res.color = 'green'
            elif i <= 0.5 * n :
                res.color = 'yellow'
            elif i <= 0.75 * n :
                res.color = 'orange'
            else :
                res.color = 'red'
        d = [e.serialize() for e in result] 
        return jsonify(d)
    else :
        d = request.json
        result = Marker.query.filter_by(id=d['id']).first()
        result.people = d['people']
        result.time = d['time']
        db.session.commit()
        return jsonify(d)

if __name__ == '__main__':
    app.run(debug = True, host='0.0.0.0', port='5000')    
