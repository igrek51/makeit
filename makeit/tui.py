from textual.app import App, ComposeResult
from textual.widgets import Label, ListItem, ListView
from textual.containers import Horizontal
from textual import events

from makeit.make import MakeStep


class ListViewExample(App):
    def __init__(self, steps: list[MakeStep], *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.steps: list[MakeStep] = steps
        self.selected_step: MakeStep | None = None
        self.chosen_step: MakeStep | None = None
        self.post_logs: list[str] = []

    def compose(self) -> ComposeResult:
        list_children: list[ListItem] = [ListItem(Label(step.name)) for step in self.steps]
        listview = ListView(
            *list_children,
            id="steps-list",
        )
        listview.styles.height = max(len(self.steps), 3) + 1

        summary_header = Label("", id="summary-header")
        summary_header.styles.color = 'royalblue'
        summary_header.styles.text_style = 'bold'

        summary_comment = Label("", id="summary-comment")
        summary_comment.styles.color = 'lightslategray'

        summary = Label("", id="summary")

        yield Label('Makefile targets:')
        yield listview
        yield summary_comment
        yield Horizontal(summary_header)
        yield summary

    def on_list_view_highlighted(self, event: ListView.Highlighted):
        self.selected_step = self._get_selected_step()
        if self.selected_step and self.selected_step.raw_lines:

            comment_label = self.query_one("#summary-comment", Label)
            comment_label.update(self.selected_step.comment or '')
            comment_label.display = bool(self.selected_step.comment)

            summary_header = self.selected_step.raw_lines[0]
            self.query_one("#summary-header", Label).update(summary_header)
            
            summary = '\n'.join(self.selected_step.raw_lines[1:])
            summary = summary.replace('\t', '    ')
            self.query_one("#summary", Label).update(summary)

    def on_list_view_selected(self, event: ListView.Selected):
        self.chosen_step = self._get_selected_step()
        self.exit()
    
    def _get_selected_step(self) -> MakeStep | None:
        listview: ListView = self.query_one("#steps-list", ListView)
        selected_index: int = listview.index or 0
        if selected_index < 0 or selected_index >= len(self.steps):
            return None
        return self.steps[selected_index]

    def on_key(self, event: events.Key) -> None:
        # self.post_logs.append(str(event))
        if event.key in {'q', 'escape'}:
            self.exit()
        elif event.key == 'home':
            listview: ListView = self.query_one("#steps-list", ListView)
            listview.index = 0
        elif event.key == 'end':
            listview: ListView = self.query_one("#steps-list", ListView)
            listview.index = len(self.steps) - 1
