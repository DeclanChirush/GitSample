class User:
    def __init__(self, id, name, email, password, user_type):
        self.id = id
        self.name = name
        self.email = email
        self.password = password
        self.user_type = user_type

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_email(self):
        return self.email

    def get_password(self):
        return self.password

    def get_user_type(self):
        return self.user_type
