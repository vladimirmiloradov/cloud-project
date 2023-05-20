from flask_login import current_user

class UsersPolicy:
    def __init__(self, record=None):
        self.record = record

    def create(self):
        return current_user.is_admin

    def delete(self):
        return current_user.is_admin

    def update(self):
        return current_user.is_admin or current_user.is_moder
    
    def assign_role(self):
        return current_user.is_admin

    def view(self):
        return current_user.is_admin
    
    def create_selection(self):
        return current_user.is_user or current_user.is_moder or current_user.is_admin