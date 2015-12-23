class User(object):
    user_id = None
    email = None
    auth_source = None

    def pretty_print(self):
        return "user_id: {}, email: {}, auth_source: {}".format(
            self.user_id, self.email, self.auth_source)