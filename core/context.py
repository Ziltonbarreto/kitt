"""Memória de curto prazo do KITT: o último buscador e a pergunta pendente (sim / cancela)."""
from datetime import datetime, timedelta


CONTEXT = {"last_engine": None, "pending_action": None}


CONFIRM_TIMEOUT = timedelta(minutes=1)


def set_pending(function, argument):
    CONTEXT["pending_action"] = (function, argument, datetime.now())


def confirm(text):
    action = CONTEXT["pending_action"]
    CONTEXT["pending_action"] = None
    if action is None:
        return "Não tenho nada para confirmar agora."

    function, argument, created_at = action
    if datetime.now() - created_at > CONFIRM_TIMEOUT:
        return "Essa pergunta expirou. Me peça de novo."
    return function(argument)


def cancel(text):
    if CONTEXT["pending_action"] is None:
        return "Não tem nada para cancelar."
    CONTEXT["pending_action"] = None
    return "Ok, cancelado."
