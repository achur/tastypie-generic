from tastypie.authorization import Authorization

class UserAuthorization(Authorization):
    def __init__(self, userattr):
        self.userattr = userattr

    def is_authorized(self, request, object=None, **kwargs):
        return True

    def apply_limits(self, request, object_list):
        if request and request.method != 'GET' and hasattr(request, 'user'):
            kwargs = {}
            kwargs[self.userattr] = request.user
            return object_list.filter(**kwargs)
        return object_list
