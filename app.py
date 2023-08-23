from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import class_mapper
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # temp fix

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

def model_to_dict(model):
    if isinstance(model, list):
        return [model_to_dict(item) for item in model]
    return {col.name: getattr(model, col.name) for col in class_mapper(model.__class__).mapped_table.c}


class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    crunchbase_url = db.Column(db.String(200))
    image_url = db.Column(db.String(200))
    tagline = db.Column(db.String(200))
    year_founded = db.Column(db.Integer)
    year_ipo = db.Column(db.Integer)
    number_of_employees = db.Column(db.Integer)
    market_category = db.Column(db.String(100))
    address = db.Column(db.String(200))
    description = db.Column(db.String(500))
    website = db.Column(db.String(200))
    longitude = db.Column(db.Float)
    latitude = db.Column(db.Float)

class Acquisition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    purchased_company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    purchasing_company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    purchased_company = db.relationship('Company', foreign_keys=[purchased_company_id], backref='acquisitions_as_purchased', lazy=True)
    purchasing_company = db.relationship('Company', foreign_keys=[purchasing_company_id], backref='acquisitions_as_purchasing', lazy=True)
    deal_date = db.Column(db.DateTime)
    deal_value = db.Column(db.Integer)
    deal_status = db.Column(db.String(100))
    deal_terms = db.Column(db.String(500))
    news_url = db.Column(db.String(200))
    news_title = db.Column(db.String(200))
    
@app.route('/companies', methods=['GET'])
def get_companies():
    with app.app_context():
        companies = Company.query.filter(Company.latitude.isnot(None)).limit(200).all()
        return jsonify(model_to_dict(companies))

@app.route('/companies/<int:id>', methods=['GET'])
def get_company(id):
    with app.app_context():
        company = Company.query.get(id)
        return jsonify(model_to_dict(company))
    
@app.route('/acquisitions', methods=['GET'])
def get_acquisitions():
    with app.app_context():
        acquisitions = Acquisition.query.limit(50).all()
        purchased_companies = Company.query.filter(Company.id.in_([acquisition.purchased_company_id for acquisition in acquisitions])).all()
        purchasing_companies = Company.query.filter(Company.id.in_([acquisition.purchasing_company_id for acquisition in acquisitions])).all()
        return jsonify({
            'acquirers': model_to_dict(purchasing_companies),
            'acquired': model_to_dict(purchased_companies),
            'acquisitions': [
                {
                    **model_to_dict(Acquisition.query.get(acquisition.id)),
                    'purchased_company': model_to_dict(Company.query.get(acquisition.purchased_company_id)),
                    'purchasing_company': model_to_dict(Company.query.get(acquisition.purchasing_company_id))
                } for acquisition in acquisitions
            ]
        })
        

@app.route('/acquisitions/<int:id>', methods=['GET'])
def get_acquisition(id):
    with app.app_context():
        acquisition = Acquisition.query.get(id)
        purchased_company = Company.query.get(acquisition.purchased_company_id)
        purchasing_company = Company.query.get(acquisition.purchasing_company_id)
        return jsonify({
            **model_to_dict(acquisition),
            'purchased_company': model_to_dict(purchased_company),
            'purchasing_company': model_to_dict(purchasing_company)
        })
    
    

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True, port=8000)
