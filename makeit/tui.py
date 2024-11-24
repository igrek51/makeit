from textual.app import App, ComposeResult
from textual.widgets import Label, ListItem, ListView, Static
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
        self.screen.styles.border = ("hidden", 'white')

        header = Label(f' {len(self.steps)} Makefile targets:')
        header.styles.width = '100%'
        header.styles.color = 'royalblue'

        list_children: list[ListItem] = [ListItem(Label(' ' + step.name)) for step in self.steps]
        listview = ListView(
            *list_children,
            id="steps-list",
        )
        listview.styles.height = max(len(self.steps), 1) + 1
        listview.styles.max_height = "50vh"

        summary_header = Label("", id="summary-header")
        summary_header.styles.color = 'royalblue'
        summary_header.styles.text_style = 'bold'

        summary_comment = Static("", id="summary-comment")
        summary_comment.styles.color = 'lightslategray'

        summary = Static("", id="summary")

        yield header
        yield listview
        yield summary_comment
        yield summary_header
        yield summary

    def on_list_view_highlighted(self, event: ListView.Highlighted):
        self.selected_step = self._get_selected_step()
        if self.selected_step and self.selected_step.raw_lines:

            comment_label = self.query_one("#summary-comment", Static)
            comment_label.update(self.selected_step.comment or '')
            comment_label.display = bool(self.selected_step.comment)

            summary_header = self.selected_step.raw_lines[0]
            self.query_one("#summary-header", Label).update(summary_header)
            
            summary = '\n'.join(self.selected_step.raw_lines[1:])
            summary = summary.replace('\t', '    ')
            self.query_one("#summary", Static).update(summary)

    def on_list_view_selected(self, event: ListView.Selected):
        self.chosen_step = self._get_selected_step()
        self.exit()
    
    def _get_selected_step(self) -> MakeStep | None:
        selected_index: int = self._get_listview().index or 0
        if selected_index < 0 or selected_index >= len(self.steps):
            return None
        return self.steps[selected_index]

    def _get_listview(self) -> ListView:
        return self.query_one("#steps-list", ListView)

    def _move_cursor_wrapping(self, delta: int):
        index = self._get_listview().index
        if index is not None:
            self._get_listview().index = (index + delta + len(self.steps)) % len(self.steps)

    def on_key(self, event: events.Key) -> None:
        # self.post_logs.append(str(event))
        if event.key in {'q', 'escape'}:
            self.exit()
        elif event.key == 'home':
            self._get_listview().index = 0
        elif event.key == 'end':
            self._get_listview().index = len(self.steps) - 1
        elif event.key == 'j':  # move down, wrapping around
            self._move_cursor_wrapping(1)
        elif event.key == 'k':  # move up
            self._move_cursor_wrapping(-1)
