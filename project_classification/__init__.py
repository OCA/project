# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Joël Grand-guillaume (Camptocamp)
#    Copyright 2011 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from . import project_classification
import psycopg2


def fill_classification_id(cr):
        query_nb_records = 'SELECT count(id) from project_project;'
        cr.execute(query_nb_records)
        res = cr.fetchall()
        if res[0][0] != 0:
            try:
                query_classification_id = (
                    'SELECT count(id) from project_project '
                    'where classification_id is null;'
                    )
                cr.execute(query_classification_id)
                res2 = cr.fetchall()
                if res[0][0] == res2[0][0]:
                    # all project have a classification_id set
                    return

            except psycopg2.ProgrammingError:
                cr.rollback()
                # project exist but
                # classification_id column does not exist in database
                # 1. create column nullable
                query = (
                    'ALTER TABLE project_project '
                    'ADD COLUMN classification_id integer;'
                    )
                cr.execute(query)
                # 2. create default classification
                query = """CREATE TABLE project_classification (
                id serial,
                name varchar,
                project_id integer,
                primary key(id)
                );"""
                cr.execute(query)
                query = (
                    "INSERT INTO project_classification (name, project_id) "
                    "VALUES ('Unclassified', "
                    "(select id from project_project limit 1));"
                    )
                cr.execute(query)
                # 3. assign this classification to all projects
                query = 'select id from project_classification limit 1;'
                cr.execute(query)
                res_create = cr.fetchall()
                if res_create:
                    query = (
                        'UPDATE project_project '
                        'set classification_id=%d;' % res_create[0][0]
                        )
                    cr.execute(query)
                # 4. alter column from nullable to not null
                query = (
                    'ALTER TABLE project_project '
                    'ALTER COLUMN classification_id SET NOT NULL;')
                cr.execute(query)
                return
        else:
            return
