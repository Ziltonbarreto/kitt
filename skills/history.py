from core.database import last_events, most_used_commands, success_rate, today_summary, unknown_phrases


def tell_stats(text):
    rows = most_used_commands()
    if not rows:
        return "Ainda não tenho dados. Me peça algumas coisas primeiro!"
    lines = ["Seus comandos mais usados:"]
    for command, total in rows:
        lines.append(f"  {command}: {total}x")
    return "\n".join(lines)


def tell_unknown(text):
    rows = unknown_phrases()
    if not rows:
        return "Até agora entendi tudo o que você pediu! 😎"
    lines = ["Frases que não entendi:"]
    for phrase, total in rows:
        lines.append(f"  {phrase}: {total}x")
    return "\n".join(lines)


def tell_success_rate(text):
    total, rate = success_rate()
    if total == 0:
        return "Ainda não tenho pedidos para calcular"
    else:
        return f"Entendi {int(rate)}% dos seus {total} pedidos"


def tell_today(text):
    total, first, top = today_summary()
    if total == 0:
        return "Você ainda não me pediu nada!"
    summary = f"Hoje foram {total} pedidos desde as {first[11:16]}."
    if top is None:
        return summary
    command, count = top
    return f"{summary} Seu comando favorito: {command} ({count}x)."


def tell_history(text):
    rows = last_events()
    if not rows:
        return "Você ainda não me pediu nada"

    lines = ["Seus últimos pedidos:"]
    for created_at, phrase, success in rows:
        icon = "✅" if success else "❌"
        lines.append(f"  {created_at[11:16]}  {icon} {phrase}")
    return "\n".join(lines)
