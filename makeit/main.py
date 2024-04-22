from textual.app import App, ComposeResult
from textual.widgets import Footer, Label, ListItem, ListView
from nuclear.sublog import error_handler

from makeit.make import read_make_steps, run_make_step, MakeStep


class ListViewExample(App):
    def __init__(self, steps: list[MakeStep], *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.steps: list[MakeStep] = steps
        self.selected_step: MakeStep | None = None
        self.chosen_step: MakeStep | None = None
        self.styles.height = 10

    def compose(self) -> ComposeResult:
        list_children: list[ListItem] = [ListItem(Label(step.name)) for step in self.steps]
        listview = ListView(
            *list_children,
            id="steps-list",
        )
        listview.styles.height = max(len(self.steps), 3) + 1

        summary = Label("Summary", id="summary")

        yield listview
        yield summary
        yield Footer()

    def on_list_view_highlighted(self, event: ListView.Highlighted):
        self.selected_step = self._get_selected_step()
        if self.selected_step:
            summary = '\n'.join(self.selected_step.raw_lines)
            summary = summary.replace('\t', '    ')
            self.query_one("#summary", Label).update(summary)

    def on_list_view_selected(self, event: ListView.Selected):
        self.chosen_step = self._get_selected_step()
        self.exit()
    
    def _get_selected_step(self) -> MakeStep | None:
        listview: ListView = self.query_one("#steps-list", ListView)
        selected_index: int = listview.index
        if selected_index < 0 or selected_index >= len(self.steps):
            return None
        return self.steps[selected_index]


def main():
    with error_handler():
        steps: list[MakeStep] = read_make_steps()

        app = ListViewExample(steps)
        app.run(inline=True, inline_no_clear=True, mouse=False, size=None)
        
        chosen_step: MakeStep | None = app.chosen_step
        if chosen_step:
            run_make_step(chosen_step)
