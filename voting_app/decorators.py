# voting_app/decorators.py
from django.shortcuts import redirect

from accounts.models import Voter


def voter_required(view_func):
    def wrapper(request, *args, **kwargs):
        voter_id = request.session.get("voter_id")
        if not voter_id:
            return redirect("login")
        try:
            voter = Voter.objects.get(id=voter_id)

            if voter.current_session_key != request.session.session_key:
                if "voter_id" in request.session:
                    del request.session["voter_id"]
                return redirect("login")

            request.voter = voter
        except Voter.DoesNotExist:
            return redirect("login")

        return view_func(request, *args, **kwargs)

    return wrapper
