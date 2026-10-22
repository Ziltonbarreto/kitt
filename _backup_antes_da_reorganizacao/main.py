from interpreter import identify, strip_wake_word
from commands import BANNER, greet, CONTEXT, routine_suggestion
from logging.handlers import RotatingFileHandler
from database import init_db, log_event
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)-8s | %(message)s",
    datefmt="%d/%m/%Y %H:%M:%S",
    handlers=[
        RotatingFileHandler(
            "kitt.log",
            maxBytes=1_000_000,
            backupCount=10,
            encoding="utf-8",
        )
    ],
)

logger = logging.getLogger("main")

def main() -> None:
    logger.info("KITT iniciado")
    init_db()
    print(BANNER)
    print("KITT: Sistemas online. Digite 'ajuda' para ver o que sei fazer ou 'sair' para encerrar.")

    suggestion = routine_suggestion()
    if suggestion:
        print("KITT:", suggestion)

    while True:
        try:
            text = input("Você: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nKITT: Encerrando. Até mais!")
            logger.info("KITT encerrado")
            break
        text = strip_wake_word(text)

        if not text:
            continue
        if text.lower() == "sair":
            print("KITT: Até mais!")
            logger.info("KITT encerrado")
            break

        command = identify(text)
        if command is None or command["name"] not in ("confirm", "cancel"):
            CONTEXT["pending_action"] = None

        if command is None:
            logger.warning(f'Não reconheceu: "{text}"')
            log_event(text, None, False)
            print("KITT: Desculpe, não reconheci esse comando. Digite 'ajuda'.")
            continue

        logger.info(f'Pedido: "{text}" -> comando {command["name"]}')
        success = True
        try:
            response = command["function"](text)
        except Exception:
            logger.exception(f'Erro inesperado no comando {command["name"]}')
            response = "Ops, tive um problema interno. Detalhes no kitt.log."    
            success = False

        print("KITT:", response)
        log_event(text, command["name"], success)


if __name__ == "__main__":
    main()
