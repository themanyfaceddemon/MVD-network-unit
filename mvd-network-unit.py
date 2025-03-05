import argparse
import logging
import os
import platform
import re
from typing import Any, Type

from app import App, AppInitializer, AuthWindow
from colorama import Fore, Style, init
from error_message_tk import show_error_message_with_traceback
from systems import AppConfig
from tools import TimerManager, ViewportResizeManager


class ColoredFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": Fore.CYAN,
        "INFO": Fore.GREEN,
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED,
        "CRITICAL": Fore.RED + Style.BRIGHT,
    }

    def format(self, record):
        color = self.COLORS.get(record.levelname, "")
        record.levelname = f"{color}{record.levelname:<7}{Style.RESET_ALL}"
        return super().format(record)


def configure_logging(debug: bool) -> None:
    log_level = logging.DEBUG if debug else logging.INFO

    log_format = "[%(asctime)s][%(levelname)s] %(name)s: %(message)s"

    console_handler = logging.StreamHandler()
    console_formatter = ColoredFormatter(log_format)
    console_handler.setFormatter(console_formatter)

    logging.basicConfig(level=log_level, handlers=[console_handler], encoding="utf-8")


def initialize_components(debug: bool, *components: Type[Any]) -> None:
    for component in components:
        logging.debug(f"Initializing {component.__name__}...")
        init_method = getattr(component, "init", None)
        if callable(init_method):
            init_method(
                debug
            ) if "debug" in init_method.__code__.co_varnames else init_method()
            logging.debug(f"{component.__name__} initialized successfully.")

        else:
            raise AttributeError(
                f"{component.__name__} does not have a callable 'init' method."
            )


def check_path_for_cyrillic():
    script_path = os.path.abspath(__file__)
    if platform.system() == "Windows" and re.compile(r"[а-яА-Я]").search(script_path):
        raise RuntimeError(
            f"Дерриктория установки программы содержит кирилические символы. Запуск приложения невозможен.\n\nТекущий путь: {script_path}"
        )


def main(debug: bool) -> None:
    logging.debug("Starting program...")
    initialize_components(
        debug,
        AppInitializer,
        AppConfig,
        TimerManager,
        ViewportResizeManager,
        AuthWindow,
    )
    AppConfig.set("debug", debug)
    logging.debug("Initialization complete. Program is ready to run.")

    logging.debug("App instance created. Running app...")
    App.run()
    logging.debug("App run completed.")


if __name__ == "__main__":
    try:
        init(autoreset=True)
        check_path_for_cyrillic()

        parser = argparse.ArgumentParser()
        parser.add_argument("--debug", action="store_true", help="Enable debug mode")
        args = parser.parse_args()

        configure_logging(args.debug)

        os.environ["PYTHONIOENCODING"] = "utf-8"
        os.environ["PYTHONUTF8"] = "1"

        main(args.debug)

    except KeyboardInterrupt:
        logging.info("Завершение работы...")

    except Exception as e:
        # Я купил себе машину
        # Думал, круче не найти
        # Откатал на ней неделю
        # Сдохла, мать её ети
        logging.critical("Unhandled exception occurred.", exc_info=True)
        show_error_message_with_traceback("Критическая ошибка системы", e)
