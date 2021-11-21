class BaseFixture():
    # This class can be used to store test inputs (e.g
    # sqlalchemy objects, uris for different routes, UUIDs etc.).
    # Two methods (`add_attr`, `add_attrs`) for adding single / multiple attributes have
    # been included to make it easier to add test inputs

    def add_attr(self, key, value):
        setattr(self, key, value)

    def add_attrs(self, **kw):
        for key, value in kw.items():
            setattr(self, key, value)
