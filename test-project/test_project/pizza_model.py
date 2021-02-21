from microcosm_postgres.models import EntityMixin, Model
from sqlalchemy import Column, String


class Pizza(EntityMixin, Model):
    __tablename__ = "pizza"

    toppings = Column(String(), nullable=True)

    @property
    def price(self):
        return 5.0