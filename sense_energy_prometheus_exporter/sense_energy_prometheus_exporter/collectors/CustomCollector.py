import pprint


class CustomCollector(object):
    namespace: str
    pp = pprint.PrettyPrinter(indent=4)

    def __init__(self, namespace: str):
        self.namespace = namespace

    def build_name(self, name, subsystem):
        full_name = ''
        if self.namespace:
            full_name += f"{self.namespace}_"
        if subsystem:
            full_name += f"{subsystem}_"
        if name:
            full_name += name

        return full_name
