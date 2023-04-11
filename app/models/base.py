#!/usr/bin/env python3
# coding=UTF-8
from datetime import datetime
from contextlib import contextmanager
from sqlalchemy import Column, Integer, SmallInteger
from flask import current_app
from flask_sqlalchemy import SQLAlchemy as _SQLAlchemy, BaseQuery

__all__ = ['db', 'Base']


class SQLAlchemy(_SQLAlchemy):
    @contextmanager
    def auto_commit(self, throw=True):
        try:
            yield
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            current_app.logger.exception('%r' % e)
            if throw:
                raise e


class Query(BaseQuery):
    def filter_by(self, **kwargs):
        if 'status' not in kwargs.keys():
            kwargs['status'] = 1
        return super(Query, self).filter_by(**kwargs)


db = SQLAlchemy(query_class=Query)


class Base(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    createDate = Column('createDate', Integer)
    updateDate = Column('updateDate', Integer)
    status = Column('status', SmallInteger, default=1)

    def __init__(self):
        self.createDate = int(datetime.now().timestamp())
        self.updateDate = int(datetime.now().timestamp())

    @property
    def create_datetime(self):
        if self.createDate:
            return datetime.fromtimestamp(self.createDate)
        else:
            return None

    @property
    def update_datetime(self):
        if self.updateDate:
            return datetime.fromtimestamp(self.updateDate)
        else:
            return None

    def to_json(self):

        dict = self.__dict__
        if "_sa_instance_state" in dict:
            del dict["_sa_instance_state"]

        return dict

    def obj2json(self, obj):
        result = {}
        for i in dir(obj):
            val = obj.__getattribute__(i)
            # 过滤不需要的属性
            if (not i.startswith('_') and hasattr(val, '__call__') == False
                    and i != 'metadata' and not isinstance(val, Query)):
                try:
                    if isinstance(val, datetime):
                        result[i] = '{}'.format(val)
                    elif isinstance(val, datetime):
                        result[i] = datetime.fromtimestamp(val).strftime(
                            '%Y-%m-%d %H:%M:%S')
                    elif isinstance(val, str) or isinstance(
                            val, int) or isinstance(val, bool):
                        result[i] = val
                    else:
                        result[i] = '%s' % val
                except:
                    result[i] = None
        return result

    def delete(self):
        self.status = 0

    def set_attrs(self, attrs):
        for key, value in attrs.items():
            if hasattr(self, key) and key != 'id':
                setattr(self, key, value)

    def check_required_fields(self, form):
        return [i for i in self.required_fields if not form.get(i)]

    def add_object(self, obj, data):
        # 验证必填参数是否有是否空值
        if self.check_required_fields(data):
            return False
        # 取提交参数里面用户属性包含的参数
        form = {key: value for key, value in data.items() if hasattr(obj, key)}
        obj = obj()
        obj.set_attrs(form)
        obj.id = obj.query.filter_by(obj.id.desc()).first().id + 1
        db.session.add(obj)
        db.session.commit()
        return True


class BaseNoCreateTime(db.Model):
    __abstract__ = True
    status = Column(SmallInteger, default=1)
