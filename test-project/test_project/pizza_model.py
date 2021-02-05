from microcosm_postgres.models import EntityMixin, Model
from sqlalchemy import String, Column

class Pizza(EntityMixin, Model):
    __tablename__ = "pizza"

    toppings = Column(String(), nullable=True)

    @property
    def random_topping(self):
        return "cheese"