from models import Base, engine, MetricType
from sqlalchemy.orm import Session

# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.create_all(engine)

session = Session(engine)
