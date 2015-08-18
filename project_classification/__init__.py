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
    cr.execute("SELECT id FROM project_project LIMIT 1")
    if not cr.fetchone():
        return

    cr.execute("select exists(select * from information_schema.tables "
               "where table_name = 'project_classification')")
    exi = cr.fetchone()
    if not exi[0]:
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
            "(select id from project_project limit 1)) RETURNING id;"
            )
        cr.execute(query)
        # 3. assign this classification to all projects
        classification_id = cr.fetchone()[0]
        if classification_id:
            query = (
                'UPDATE project_project '
                'set classification_id=%d;' % classification_id
                )
            cr.execute(query)
        # 4. alter column from nullable to not null
        query = (
            'ALTER TABLE project_project '
            'ALTER COLUMN classification_id SET NOT NULL;')
        cr.execute(query)
        return
