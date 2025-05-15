from collections.abc import Iterable


class TextService:

    @staticmethod
    def write_list(target, list_data):
        assert (isinstance(list_data, Iterable))
        with open(target, "w") as f:
            for item in list_data:
                f.write(item)
                f.write("\n")
