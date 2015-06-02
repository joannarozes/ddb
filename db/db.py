from sqlalchemy.orm import sessionmaker

import models

Session = sessionmaker(bind=models.engine, autocommit=True)
session = Session()
