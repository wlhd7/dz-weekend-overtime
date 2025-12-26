from .index import index, select_department
from .info import info
from .edit_names import edit_names
from .toggle_sat import toggle_sat
from .preset import preset_add, preset_delete

views = [index, info, select_department, edit_names, toggle_sat, preset_add, preset_delete]


def init_route(app, views):
    app.add_url_rule(
        '/',
        view_func=views[0],
        methods=['GET', 'POST']
    )

    app.add_url_rule(
        '/info',
        view_func=views[1],
        methods=['GET', 'POST']
    )

    app.add_url_rule(
        '/select-department',
        view_func=views[2],
        methods=['GET', 'POST']
    )

    app.add_url_rule(
        '/edit-names',
        view_func=views[3],
        methods=['POST']
    )

    app.add_url_rule(
        '/toggle-sat',
        view_func=views[4],
        methods=['POST']
    )

    app.add_url_rule(
        '/preset/add',
        view_func=views[5],
        methods=['GET', 'POST']
    )

    app.add_url_rule(
        '/preset/delete',
        view_func=views[6],
        methods=['POST']
    )