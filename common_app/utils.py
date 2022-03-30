from django.shortcuts import redirect


def permission_required(func):
    def wrapper(request, *args, **kwargs):
        if not request.user.user_type <= 2:
            return redirect('/permission-warning/')

        return func(request, *args, **kwargs)
    return wrapper
