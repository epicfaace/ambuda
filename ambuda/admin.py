from flask import abort, url_for, request
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib import sqla
from flask_login import current_user

import ambuda.database as db
import ambuda.queries as q


class AmbudaIndexView(AdminIndexView):
    @expose("/")
    def index(self):
        if not current_user.is_admin:
            # Abort so that a malicious scraper can't infer that there's an
            # interesting page here.
            abort(404)
        return super(AmbudaIndexView, self).index()


class BaseView(sqla.ModelView):
    def is_accessible(self):
        return current_user.is_admin

    def inaccessible_callback(self, name, **kw):
        abort(404)


class UserView(BaseView):
    column_list = form_columns = ["id", "username", "password_hash", "email"]


class TextView(BaseView):
    column_list = form_columns = ["id", "slug", "title"]


class ProjectView(BaseView):
    column_list = form_columns = ["id", "slug", "title"]


def create_admin_manager(app):
    session = q.get_session_class()
    admin = Admin(app, name="Ambuda", index_view=AmbudaIndexView())
    admin.add_view(UserView(db.User, session))
    admin.add_view(TextView(db.Text, session))
    admin.add_view(ProjectView(db.Project, session))
    return admin
