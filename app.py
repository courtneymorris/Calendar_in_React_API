from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://rrokorvhgxwyyx:09333481a898f8c97ae6866a3d3dcdc73d1474fd77b80289ad27251db11890e3@ec2-44-197-40-76.compute-1.amazonaws.com:5432/d57rstqtfdhqoc"

db = SQLAlchemy(app)
ma = Marshmallow(app)
CORS(app)


class Month(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    start_day = db.Column(db.Integer, nullable=False)
    days_in_month = db.Column(db.Integer, nullable=False)
    days_in_previous_month = db.Column(db.Integer, nullable=False)

    def __init__(self, name, year, start_day, days_in_month, days_in_previous_month):
        self.name = name
        self.year = year
        self.start_day = start_day
        self.days_in_month = days_in_month
        self.days_in_previous_month = days_in_previous_month

class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String, nullable=False)
    date = db.Column(db.Integer, nullable=False)
    month_id = db.Column(db.Integer, nullable=False)

    def __init__(self, text, date, month_id):
        self.text = text
        self.date = date
        self.month_id = month_id

class MonthSchema(ma.Schema):
    class Meta:
        fields = ("id", "name", "year", "start_day", "days_in_month", "days_in_previous_month")

month_schema = MonthSchema()
multi_month_schema = MonthSchema(many=True)

class ReminderSchema(ma.Schema):
    class Meta:
        fields = ("id", "text", "date", "month_id")

reminder_schema = ReminderSchema()
multi_reminder_schema = ReminderSchema(many=True)

@app.route("/month/add", methods=["POST"])
def add_month():
    if request.content_type != "application/json":
        return jsonify("Error: Please send data as JSON")

    post_data = request.get_json()
    name = post_data.get("name")
    year = post_data.get("year")
    start_day = post_data.get("start_day")
    days_in_month = post_data.get("days_in_month")
    days_in_previous_month = post_data.get("days_in_previous_month")

    existing_month_check = db.session.query(Month).filter(Month.name == name).filter(Month.year == year).first()
    if existing_month_check is not None:
        return jsonify("Error: Month already exists")

    new_record = Month(name, year, start_day, days_in_month, days_in_previous_month)
    db.session.add(new_record)
    db.session.commit()

    return jsonify(month_schema.dump(new_record))

@app.route("/month/add/multi", methods=["POST"])
def add_multi_months():
    if request.content_type != "application/json":
        return jsonify("Error: Please send data as JSON")

    post_data = request.get_json()
    data = post_data.get("data")

    new_records = []

    for month in data:
        name = month.get("name")
        year = month.get("year")
        start_day = month.get("start_day")
        days_in_month = month.get("days_in_month")
        days_in_previous_month = month.get("days_in_previous_month")

        existing_month_check = db.session.query(Month).filter(Month.name == name).filter(Month.year == year).first()
        if existing_month_check is None:
            new_record = Month(name, year, start_day, days_in_month, days_in_previous_month)
            db.session.add(new_record)
            db.session.commit()
            new_records.append(new_record)

    return jsonify(multi_month_schema.dump(new_records))

@app.route("/month/get", methods=["GET"])
def get_months():
    all_months = db.session.query(Month).all()
    return jsonify(multi_month_schema.dump(all_months))

if __name__ == "__main__":
    app.run(debug=True)