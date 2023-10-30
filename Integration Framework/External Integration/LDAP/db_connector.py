from sqlalchemy import create_engine, Column, Integer, String, Sequence, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

# Define ORM models for the database
Base = declarative_base()


class UserLog(Base):
    __tablename__ = 'user_log'
    id = Column(Integer, Sequence('user_log_id_seq'), primary_key=True)
    action = Column(String(50))
    user_dn = Column(String(255))
    timestamp = Column(DateTime)


class DBConnector:
    def __init__(self, db_url):
        # Create an engine and session factory
        self.engine = create_engine(db_url)
        self.SessionFactory = sessionmaker(bind=self.engine)

    def create_tables(self):
        # Create tables in the database (if they don't already exist)
        Base.metadata.create_all(self.engine)

    def log_user_action(self, action, user_dn):
        # Log a user action to the database
        session = self.SessionFactory()
        try:
            log_entry = UserLog(action=action, user_dn=user_dn)
            session.add(log_entry)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def query_logs(self):
        # Query the user_log table
        session = self.SessionFactory()
        try:
            logs = session.query(UserLog).order_by(UserLog.timestamp)
            return logs.all()
        except Exception as e:
            raise e
        finally:
            session.close()



if __name__ == "__main__":
    db_url = 'sqlite:///user_log.db'  # Replace with your desired database URL
    db_connector = DBConnector(db_url)
    db_connector.create_tables()

    # Log an LDAP user addition action for the user "Rohit Tambakhe"
    ldap_user_dn = "cn=Rohit Tambakhe,ou=users,dc=tam-range,dc=com"
    db_connector.log_user_action('add', ldap_user_dn)

    # Query and print logs
    logs = db_connector.query_logs()
    for log_entry in logs:
        print(f"{log_entry.timestamp} - {log_entry.action} - {log_entry.user_dn}")
