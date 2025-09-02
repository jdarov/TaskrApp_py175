

MIN_TITLE_LEN = 1
MAX_TITLE_LEN = 100

def error_for_list_title(title, lists):
    if any(lst['title'] == title for lst in lists):
        return "The title must be unique"
    
    if not MIN_TITLE_LEN <= len(title) <= MAX_TITLE_LEN:
        return "The title must be between 1 and 100 characters"
    
    return None

def error_for_todo_title(todo_title):
    if not MIN_TITLE_LEN <= len(todo_title) <= MAX_TITLE_LEN:
        return "The todo title must be between 1 and 100 characters"
    return None

def find_list_by_id(list_id, lists):
    return next((todo_list for todo_list in lists
                 if todo_list['id'] == list_id), None)

def find_todo_by_id(todo_id, todos):
    if todos:
        return next((todo for todo in todos
                     if todo['id'] == todo_id), None)
    return None

def complete_all_todos(todos):
    (todo.update(completed=True) for todo in todos)

def remove_todo_list(todo_list, lst):
    lst.remove(todo_list)

def todos_remaining(lst):
    return sum(1 for todo in lst['todos'] if not todo['completed'])

def list_completed(lst):
    return (lst['todos'] and not todos_remaining(lst))

def todo_complete(todo):
    return todo['completed']

def sort_items(lst, select_completed):
    return sorted(
        lst,
        key = lambda item: (bool(select_completed(item)), item['title'].lower())
        )