from pathlib import Path

from sqlalchemy import create_engine, String, Boolean, Integer, select, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session, relationship

from werkzeug.security import generate_password_hash, check_password_hash

from datetime import datetime

current_folder = Path(__file__).parent
PATH_TO_BD = current_folder / 'bd_users.sqlite'


class Base(DeclarativeBase):
    pass

class UserVacation(Base):
    __tablename__ = 'user_vacation'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    password: Mapped[str] = mapped_column(String(128))
    email: Mapped[str] = mapped_column(String(30))
    admin_access: Mapped[bool] = mapped_column(Boolean(), default=False)
    entry_date: Mapped[str] = mapped_column(String(30))
    vacation_event: Mapped[list["VacationEvent"]] = relationship(
        back_populates="parent",
        lazy="subquery"
    )

    def __repr__(self):
        return f"User({self.id=}, {self.name=})"

    def defines_password(self, password):
        self.password = generate_password_hash(password)

    def checks_password(self, password):
        return check_password_hash(self.password, password)

    def add_vacation(self, start_vacation, end_vacation):
        total_days = (datetime.strptime(end_vacation, 'Y%-%m-%d')
                      - datetime.strptime(start_vacation, 'Y%-%m-%d')
        ).days + 1
        with Session(bind=engine) as session:
            vacation = VacationEvent(parent_id=self.id,
                                     start_vacation=start_vacation,
                                     end_vacation=end_vacation,
                                     total_days=total_days)
            session.add(vacation)
            session.commit()

    def vacation_list(self):
        events_list=[]
        for event in self.vacation_event:
            events_list.append({"title": f"{self.name} vacation",
                                "start": event.start_vacation,
                                "end": event.end_vacation,
                                "resourceId": self.id})
            return events_list

    def days_to_require(self):
        total_days = (datetime.now() - datetime.strptime(self.entry_date, '%Y-%m%d')).days * (30/365)
        used_days = 0
        for event in self.vacation_event:
            used_days += event.total_days
        return int(total_days - used_days)

class VacationEvent(Base):
    __tablename__ = 'vacation_event'

    id: Mapped[int] = mapped_column(primary_key=True)
    parent_id: Mapped[int] = mapped_column(ForeignKey('user_vacation.id'))
    parent: Mapped["UserVacation"] = relationship(lazy='subquery')
    start_vacation: Mapped[str] = mapped_column(String(30))
    end_vacation: Mapped[str] = mapped_column(String(30))
    total_days: Mapped[int] = mapped_column(Integer())


engine = create_engine(f'sqlite:///{PATH_TO_BD}')
Base.metadata.create_all(bind=engine)


#--------------- CRUD -------------------

def creates_users(name, password, email, **kwargs):
    with Session(bind=engine) as session:
        user = UserVacation(
            name=name,
            email=email,
            **kwargs
        )
        user.defines_password(password)
        session.add(user)
        session.commit()


def reads_all_users():
    with Session(bind=engine) as session:
        command_sql = select(UserVacation)
        users = session.execute(command_sql).fetchall()
        return [user[0] for user in users]


def reads_user_by_id(user_id):
    with Session(bind=engine) as session:
        command_sql = select(UserVacation).filter_by(id=user_id)
        users = session.execute(command_sql).fetchall()
        return users[0][0] if users else None


def updates_user(user_id, **kwargs):
    with Session(bind=engine) as session:
        command_sql = select(UserVacation).filter_by(id=user_id)
        users = session.execute(command_sql).fetchall()
        if users:
            user = users[0][0]
            for key, value in kwargs.items():
                if key == 'password':
                    user.defines_password(value)
                else:
                    setattr(user, key, value)
            session.commit()


def deletes_user(user_id):
    with Session(bind=engine) as session:
        command_sql = select(UserVacation).filter_by(id=user_id)
        users = session.execute(command_sql).fetchall()
        if users:
            session.delete(users[0][0])
            session.commit()


if __name__ == '__main__':
    pass

 #   creates_users(
  #      'John Doe',
   #     password='doessecretpassword',
    #    email='doesmail@example.com',
     #   entry_date = 'yyyy-mm-dd'
     #   admin_access=True,
    #)
