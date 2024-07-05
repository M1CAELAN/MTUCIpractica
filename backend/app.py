import os
import requests
from dotenv import load_dotenv
from flask import Flask, request
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy


load_dotenv()

app = Flask(__name__)
api = Api()
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://postgres:{os.getenv('POSTGRES_PASSWORD')}@db:5432/{os.getenv('POSTGRES_DB')}"

db = SQLAlchemy(app)
migrate = Migrate(app, db)
ma = Marshmallow(app)


class VacancyModel(db.Model):
    __tablename__ = 'Vacancy'

    id = db.Column(db.Integer(), primary_key=True)
    vacancy = db.Column(db.String(200), nullable=False)
    employer = db.Column(db.String(300), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    salaryFrom = db.Column(db.Integer(), nullable=False)
    salaryTo = db.Column(db.Integer(), nullable=False)
    requirement = db.Column(db.String(350), nullable=False)
    responsibility = db.Column(db.String(350), nullable=False)
    alternate_url = db.Column(db.String(120), default=False)
    time = db.Column(db.String(70), default=False)
    timeDay = db.Column(db.String(70), default=False)

    def __init__(self, id, vacancy, employer, address, salaryFrom, salaryTo, requirement, responsibility, alternate_url,
                 time, timeDay):
        self.id = id
        self.vacancy = vacancy
        self.employer = employer
        self.address = address
        self.salaryFrom = salaryFrom
        self.salaryTo = salaryTo
        self.requirement = requirement
        self.responsibility = responsibility
        self.alternate_url = alternate_url
        self.time = time
        self.timeDay = timeDay

    def __repr__(self):
        return [self.vacancy, self.employer, self.address, self.salaryFrom, self.salaryTo, self.requirement,
                self.responsibility, self.alternate_url, self.time, self.timeDay]


class VacancyModelShema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = VacancyModel


def get_data_from_hh(url):
    user = get_headers()
    data = requests.get(url, headers=user['headers'], timeout=5).json()
    return data


def get_headers():
    headers = {
        'user-agent': os.getenv('USER_AGENT')}
    persona = {
        'headers': headers
    }
    return persona

def reset_table():
    al = VacancyModel.query.all()
    for a in range(len(al)):
        x = VacancyModel.query.get(al[a].id)
        db.session.delete(x)
        db.session.commit()


def add_name(text, area):
    reset_table()
    url = f'https://api.hh.ru/vacancies?text={text}&search_field=name&per_page=100&area={area}'
    data = get_data_from_hh(url)
    parser(data, text, area)


def parser(data, text, area):
    quantity_pagination = round(data['found'] / 100, 0) + 1
    page = 0
    id = 1
    while page < quantity_pagination and page < 20:
        url = f'https://api.hh.ru/vacancies?text={text}&search_field=name&per_page=100&page={page}&area={area}'
        data = get_data_from_hh(url)
        for vacancy in data['items']:
            if vacancy['address'] is None:
                adress = 'Нет адресса'
            else:
                adress = str(vacancy['address']['raw'])
            if vacancy.get('salary') is not None:
                if vacancy.get('salary').get('to') is not None:
                    salaryTo = vacancy['salary']['to']
                else:
                    salaryTo = 0
                if vacancy.get('salary').get('from') is not None:
                    salaryFrom = vacancy['salary']['from']
                else:
                    salaryFrom = 0
            else:
                salaryFrom = 0
                salaryTo = 0
            if vacancy['snippet']['requirement'] is not None:
                requirement = vacancy['snippet']['requirement'].replace('<highlighttext>', '')
            else:
                requirement = ''

            if vacancy['snippet']['responsibility'] is not None:
                responsibility = vacancy['snippet']['responsibility'].replace('<highlighttext>', '')
            else:
                responsibility = ''

            resume = VacancyModel(id=id, vacancy=vacancy['name'], employer=vacancy['employer']['name'], address=adress,
                                  salaryFrom=salaryFrom, salaryTo=salaryTo,
                                  requirement=requirement, responsibility=responsibility,
                                  alternate_url=vacancy['alternate_url'], time=vacancy['published_at'][:10],
                                  timeDay=vacancy['employment']['name'])
            db.session.add(resume)
            db.session.commit()
            id += 1
        page += 1


def serch(regs, area):
    for reg in regs:
        if reg['name'].lower() == area.lower():
            reg_id = reg['id']
            return reg_id
        else:
            if reg['areas'] is not None:
                reg_id = serch(reg['areas'], area)
                if reg_id != 0:
                    return reg_id
    return 0


class Vacancy(Resource):
    @staticmethod
    def get():
        vacancy = request.args.get('vacancy')
        salary_from = request.args.get('salaryFrom')
        salary_to = request.args.get('salaryTo')
        time_day = request.args.get('timeDay', '')
        area = request.args.get('area')
        add_name(vacancy, area)
        vacancy_shema = VacancyModelShema(many=True)
        if time_day in ["Полная занятость", "Частичная занятость"]:
            return vacancy_shema.dump(VacancyModel.query.filter(VacancyModel.salaryFrom >= salary_from)
                                      .filter(VacancyModel.salaryTo <= salary_to)
                                      .filter(VacancyModel.timeDay == time_day).all())
        else:
            return vacancy_shema.dump(VacancyModel.query.filter(VacancyModel.salaryFrom >= salary_from)
                                      .filter(VacancyModel.salaryTo <= salary_to).all())


class region(Resource):
    @staticmethod
    def get(area):
        url = 'https://api.hh.ru/areas'
        response = requests.get(url)
        if response.status_code == 200:
            regs = response.json()
        reg_id = serch(regs, area)
        if reg_id != 0:
            return {"id": reg_id}
        else:
            return {"mesenge": "region not found"}


api.add_resource(Vacancy, '/vacancy')
api.add_resource(region, '/region/<string:area>')

api.init_app(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
