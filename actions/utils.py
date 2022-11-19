from .models import Action

def create_action(user, verb, target=None):
    action = Action(user, verb, target=target)
    action.save()