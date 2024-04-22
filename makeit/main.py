from textual.app import App, ComposeResult
from textual.widgets import Footer, Label, ListItem, ListView


class ListViewExample(App):
    CSS_PATH = "list_view.tcss"

    def compose(self) -> ComposeResult:
        yield ListView(
            ListItem(Label("One")),
            ListItem(Label("Two")),
            ListItem(Label("Three")),
        )
        yield Footer()


def main():
    app = ListViewExample()
    app.run()
