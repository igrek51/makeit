from nuclear.sublog import logger, error_handler

from makeit.make import read_make_steps, render_steps_list, run_make_step, MakeStep
from makeit.tui import ListViewExample


def main():
    with error_handler():
        steps: list[MakeStep] = read_make_steps()

        app = ListViewExample(steps)
        app.run(inline=False, mouse=False)
        chosen_step: MakeStep | None = app.chosen_step

        render_steps_list(steps, chosen_step)
        for log in app.post_logs:
            logger.debug(log)
        if chosen_step:
            run_make_step(chosen_step)
