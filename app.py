from werkzeug.exceptions import NotFound

from uuid import uuid4
from functools import wraps
import os

from flask import (
    flash,
    Flask,
    g, 
    redirect, 
    render_template, 
    request,
    session,
    url_for, 
)

from todos.utils import (
    complete_all_todos,
    error_for_list_title,
    error_for_todo_title,
    find_list_by_id,
    find_todo_by_id,
    list_completed,
    remove_todo_list,
    sort_items,
    todo_complete,
    todos_remaining,
)

MIN_TITLE_LEN = 1
MAX_TITLE_LEN= 100


app = Flask(__name__, template_folder='templates')
app.secret_key = 'secret1'

def require_list(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        list_id = kwargs.get('list_id')
        lst = find_list_by_id(list_id, session['lists'])
        if not lst:
            raise NotFound(description="List Not Found")
        return f(lst=lst, *args, **kwargs)
    
    return decorated_function

def require_todo(f):
    @wraps(f)
    @require_list
    def decorated_function(lst, *args, **kwargs):
        todo_id = kwargs.get('todo_id')
        todo = find_todo_by_id(todo_id, lst['todos'])
        if not todo:
            raise NotFound(description="Todo Not Found")
        return f(lst=lst, todo=todo, *args, **kwargs)
    
    return decorated_function

@app.before_request
def initialize_session():
    if 'lists' not in session:
        session['lists'] = []

@app.context_processor
def list_utilities_processor():
    return dict(todos_remaining = todos_remaining)

@app.context_processor
def list_utilities_processor():
    return dict(list_completed = list_completed)

@app.route("/lists/new")
def add_todo_list():
    return render_template("new_list.html")

@app.route("/lists")
def get_lists():
    lists = sort_items(session['lists'], list_completed)
    return render_template("lists.html", 
                           lists=lists,
                           todos_remaining=todos_remaining)

@app.route("/lists", methods=["POST"])
def create_list():
    title = request.form["list_title"].strip()

    error = error_for_list_title(title, session['lists'])
    if error:
        flash(error, "error")
        return render_template('new_list.html', title=title)
    
    session['lists'].append({
        'id': str(uuid4()),
        'title': title,
        'todos': [],
    })

    flash("The list has been created", "success")
    session.modified = True
    return redirect(url_for('get_lists'))

@app.route("/list/<list_id>/todos", methods=["POST"])
@require_todo
def create_todo(lst, list_id):
    todo_title = request.form['todo'].strip()

    error = error_for_todo_title(todo_title)
    if error:
        flash(error, "error")
        return render_template('list.html', lst=lst)

    lst['todos'].append({
        'id': str(uuid4()),
        'title': todo_title,
        'completed': False,
    })

    flash("The todo was added", "success")
    session.modified = True
    return redirect(url_for('show_list', list_id=list_id))

@app.route("/lists/<list_id>/todos/<todo_id>/toggle", methods=['POST'])
@require_todo
def update_todo_status(lst, todo, list_id, todo_id):

    todo['completed'] = (request.form['completed'] == 'True')
    flash("The todo was updated successfully", "success")
    session.modified = True

    return redirect(url_for('show_list', list_id=list_id))

@app.route("/lists/<list_id>/todos/<todo_id>/delete", methods=["POST"])
@require_todo
def delete_todo(lst, todo, list_id, todo_id):

    lst['todos'].remove(todo)
    flash("The todo was sucessfully removed", "success")
    session.modified = True

    return redirect(url_for('show_list', list_id=list_id))

@app.route("/lists/<list_id>/complete_all", methods=["POST"])
@require_list
def mark_all_complete(lst, list_id):
    
    complete_all_todos(lst)
    flash("All todos have updated to completed successfully", "success")
    session.modified = True

    return redirect(url_for('show_list', list_id=list_id))


@app.route("/lists/<list_id>")
@require_list
def show_list(lst, list_id):

    lst['todos'] = sort_items(lst['todos'], todo_complete)
    return render_template('list.html', lst=lst)

@app.route("/lists/<list_id>/edit")
@require_list
def edit_list(lst, list_id):
    
    return render_template('edit_list.html', lst=lst)

@app.route("/lists/<list_id>/delete", methods=["POST"])
@require_list
def delete_list(lst, list_id):
    
    remove_todo_list(lst, session['lists'])
    flash("Todo List successfully removed", "success")
    session.modified = True

    return redirect(url_for('get_lists'))

@app.route("/lists/<list_id>", methods=['POST'])
@require_list
def edit_list_name(lst, list_id):
    title = request.form['list_title'].strip()
    
    error = error_for_list_title(title, session['lists'])
    if error:
        flash(error, "error")
        return render_template('edit_list.html', lst=lst, title=title)
    
    lst.update(title=title)

    flash("The title has been succesfully changed", "success")
    session.modified = True
    return redirect(url_for('show_list', list_id=list_id))

    
@app.route("/")
def index():
    return redirect(url_for("get_lists"))


if __name__ == "__main__":
    if os.environ.get('FLASK_ENV') == 'production':
        app.run(debug=False)
    else:
        app.run(debug=True, port=5003)