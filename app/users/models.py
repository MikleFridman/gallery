from flask import abort, flash, current_app
from flask_login import UserMixin
from sqlalchemy import inspect
from sqlalchemy.orm import ONETOMANY, MANYTOMANY
from datetime import datetime

from app import db, login


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Entity:
    table_link = ''
    sort = 'id'
    sort_mode = 'asc'
    search = []
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), default='')
    no_active = db.Column(db.Boolean, default=False)
    timestamp_create = db.Column(db.DateTime(), default=datetime.utcnow())
    timestamp_update = db.Column(db.DateTime(), default=datetime.utcnow(),
                                 onupdate=datetime.utcnow())

    @staticmethod
    def get_class(class_name):
        cls_name = class_name.strip()
        cls_name = cls_name.replace('_', ' ').title()
        cls_name = cls_name.replace(' ', '')
        if cls_name in globals():
            return globals()[cls_name]
        else:
            abort(500)

    @classmethod
    def get_subclasses(cls):
        return list(c.__name__ for c in cls.__subclasses__())

    @classmethod
    def get_items(cls, tuple_mode=False, data_filter=None, data_search=None):
        param = {'no_active': False}
        if data_filter:
            param = {**param, **data_filter}
        items = cls.query.filter_by(**param)
        if data_search:
            items = items.filter(*data_search)
        if cls.sort_mode == 'asc':
            items = items.order_by(getattr(cls, cls.sort).asc())
        else:
            items = items.order_by(getattr(cls, cls.sort).desc())
        if tuple_mode:
            items = [(i.id, i.name) for i in items]
            items.insert(0, (0, '-Select-'))
        else:
            items = [i for i in items]
        return items

    @classmethod
    def get_pagination(cls, page, data_filter=None, data_search=None):
        param = {'no_active': False}
        if data_filter:
            param = {**param, **data_filter}
        items = cls.query.filter_by(**param)
        if data_search:
            items = items.filter(*data_search)
        if cls.sort_mode == 'asc':
            items = items.order_by(getattr(cls, cls.sort).asc())
        else:
            items = items.order_by(getattr(cls, cls.sort).desc())
        items = items.paginate(page, current_app.config['ROWS_PER_PAGE'], False)
        return items

    @classmethod
    def get_object(cls, id, mode_404=True):
        param = {'no_active': False, 'id': id}
        if mode_404:
            obj = cls.query.filter_by(**param).first_or_404()
        else:
            obj = cls.query.filter_by(**param).first()
        return obj

    @classmethod
    def find_object(cls, data_filter, mode_404=False, overall=False):
        if overall:
            param = {'no_active': False, **data_filter}
        else:
            param = {'no_active': False, **data_filter}
        if mode_404:
            obj = cls.query.filter_by(**param).first_or_404()
        else:
            obj = cls.query.filter_by(**param).first()
        return obj

    def delete_object(self):
        for attr in self.get_relationships():
            if len(getattr(self, attr.split('.')[1])) > 0:
                flash('Unable to delete the selected object')
                return False
        db.session.delete(self)
        db.session.commit()
        flash('Object successfully deleted')
        return True

    def get_relationships(self):
        rel_list = []
        for r in inspect(type(self)).relationships:
            if r.direction == ONETOMANY and 'delete' not in r.cascade:
                rel_list.append(r.__str__())
            elif (r.direction == MANYTOMANY and
                  r.secondary.name.split('_')[1] == r.back_populates):
                rel_list.append(r.__str__())
        return rel_list

    def __repr__(self):
        return self.name


class User(Entity, UserMixin, db.Model):
    pass
