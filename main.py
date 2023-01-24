from app import create_app, create_database,db
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

DB_NAME = "database.db"
app = create_app(DB_NAME,db)
# db.init_app(app)
create_database(app,db)
#init migrate   

if __name__ == '__main__':
    app.run(debug=False,threaded=True,host="0.0.0.0", port=8080)