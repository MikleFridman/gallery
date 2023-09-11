import os

import boto3
from flask import abort, flash, current_app
from sqlalchemy import inspect
from sqlalchemy.orm import ONETOMANY, MANYTOMANY
from datetime import datetime

from app import db, cache


artworks_tags = db.Table('artworks_tags',
                         db.Column('artwork_id',
                                   db.Integer,
                                   db.ForeignKey('artwork.id'),
                                   primary_key=True),
                         db.Column('tag_id',
                                   db.Integer,
                                   db.ForeignKey('tag.id'),
                                   primary_key=True))


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


class ArtworkType(Entity, db.Model):
    artworks = db.relationship('Artwork', backref='type')
    features = db.relationship('Feature', backref='type')


class Feature(Entity, db.Model):
    type_id = db.Column(db.Integer, db.ForeignKey('artwork_type.id'),
                        nullable=False)
    values = db.relationship('FeaturesValue', backref='feature', cascade='all, delete')


class FeaturesValue(Entity, db.Model):
    artwork_id = db.Column(db.Integer, db.ForeignKey('artwork.id'),
                           primary_key=True)
    feature_id = db.Column(db.Integer, db.ForeignKey('feature.id'),
                           primary_key=True)
    value = db.Column(db.String(32))


class Artwork(Entity, db.Model):
    type_id = db.Column(db.Integer, db.ForeignKey('artwork_type.id'), nullable=False)
    author = db.Column(db.String(32))
    year = db.Column(db.String(10))
    buy_price = db.Column(db.Integer)
    info = db.Column(db.Text)
    files = db.relationship('Attachment', backref='artwork', cascade='all, delete')
    features_values = db.relationship('FeaturesValue', backref='artwork', cascade='all, delete')
    offers = db.relationship('Offer', backref='artwork')
    tags = db.relationship('Tag', secondary=artworks_tags, lazy='subquery',
                           backref=db.backref('artwork', lazy=True))

    def get_feature_value(self, feature_id):
        for item in self.features_values:
            if item.feature_id == int(feature_id):
                return item

    def add_feature_value(self, feature_id, value):
        feature_value = FeaturesValue(artwork_id=self.id,
                                      feature_id=feature_id,
                                      value=value)
        db.session.add(feature_value)

    def update_feature_value(self, feature_id, value):
        feature_value = self.get_feature_value(feature_id)
        if feature_value:
            feature_value.value = value

    @property
    def main_image(self):
        if not len(self.files):
            return None
        for file in self.files:
            if file.main_image:
                return file
        return self.files[0]

    def add_tag(self, tag):
        if tag not in self.tags:
            self.tags.append(tag)

    def delete_tag(self, tag):
        if tag in self.tags:
            self.tags.remove(tag)


class Tag(Entity, db.Model):
    pass


class Client(Entity, db.Model):
    name = db.Column(db.String(64), index=True, nullable=False)
    phone = db.Column(db.String(16), index=True, nullable=False)
    birthday = db.Column(db.Date)
    info = db.Column(db.Text)
    offers = db.relationship('Offer', backref='client')


class Attachment(Entity, db.Model):
    artwork_id = db.Column(db.Integer, db.ForeignKey('artwork.id'),
                           nullable=False)
    path = db.Column(db.String(128))
    hash = db.Column(db.String(64))
    main_image = db.Column(db.Boolean, default=False)
    info = db.Column(db.Text)

    @property
    def is_video(self):
        extension = os.path.splitext(self.name)[1]
        return extension in ['.avi', '.mov', '.mp4', '.webm']

    @staticmethod
    def create_file_name(artwork, extension):
        if not artwork:
            return ''
        return ('attachment_' +
                str(artwork.id) + '_' +
                str(len(artwork.files) + 1) +
                extension)

    @staticmethod
    def allowed_file_ext(extension):
        allow_ext = current_app.config['UPLOAD_EXTENSIONS']
        return extension in allow_ext

    @staticmethod
    def get_aws_client():
        return boto3.client(service_name='s3',
                            aws_access_key_id=current_app.config['AWS_KEY_ID'],
                            aws_secret_access_key=current_app.config['AWS_SECRET_KEY'],
                            region_name=current_app.config['AWS_REGION'])

    @cache.memoize()
    def get_aws_public_url(self, thumbnail=False):
        filename = self.name
        if thumbnail:
            filename = 'thumb_' + filename
        s3_client = Attachment.get_aws_client()
        return s3_client.generate_presigned_url(
            'get_object', Params={'Bucket': self.path, 'Key': filename})

    def aws_upload_file(self, path, thumbnail=False):
        filename = self.name
        if thumbnail:
            filename = 'thumb_' + filename
        s3_client = Attachment.get_aws_client()
        s3_client.upload_file(Filename=path,
                              Bucket=current_app.config['AWS_BUCKET_NAME'],
                              Key=filename)

    def delete_file(self):
        s3_client = Attachment.get_aws_client()
        s3_client.delete_object(Bucket=current_app.config['AWS_BUCKET_NAME'],
                                Key=self.name)
        db.session.delete(self)
        db.session.commit()

    def set_main_image(self):
        for file in self.artwork.files:
            if not file.id == self.id:
                file.main_image = False
        self.main_image = True


class Status(Entity, db.Model):
    offers = db.relationship('Offer', backref='status')


class Offer(Entity, db.Model):
    artwork_id = db.Column(db.Integer, db.ForeignKey('artwork.id'),
                           nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'),
                          nullable=False)
    price = db.Column(db.Integer)
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'))
    info = db.Column(db.Text)
