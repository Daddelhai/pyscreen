from .textbox import Textbox


class Passwordbox(Textbox):
    @property
    def _show_value(self) -> str:
        return "*" * len(self.value)