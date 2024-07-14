# initialize database

# ensure the database schema is created to create tables defined by SQLAlchemy models

from app import app, db
from app import User

#create an application context
with app.app_context(): # application context is necessary for any operation that requires the current application instance, such as database operations
    
    #create the database and database table
    db.create_all()

    #commit the changes
    db.session.commit()