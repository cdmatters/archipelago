
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import  Column, Integer, String, Boolean

Base = declarative_base()

class MPCommons(Base):
    __tablename__ = 'MPCommons'

    Name = Column(String)
    Constituency = Column(String, primary_key=True)
    MP = Column(Boolean, default=0)
    Party = Column(String)
    ImageUrl = Column(String)
    MemberId = Column(Integer, default=0)
    PersonId = Column(Integer, default=0)
    OfficialId = Column(Integer, index=True, default=0)

    # def __repr__(self):
    #    pass

class Office(Base):
    __tablename__ = 'Offices'

    PersonId = Column(Integer, primary_key=True)
    Office = Column(String, primary_key=True)
    StartDate = Column(String, primary_key=True)
    EndDate = Column(String, primary_key=True)
    Name = Column(String, primary_key=True)
    Title = Column(String, primary_key=True)

    def __repr__(self):
        return "<Office Type ( Name:'%s', Title:'%s', Office:'%s', StartDate'%s', EndDate:'%s')>" % (
                        self.Name, self.Title, self.Office, self.StartDate, self.EndDate)

class Address(Base):
    __tablename__ = 'Addresses'

    OfficialId = Column(Integer)
    AddressType = Column(String)
    Address = Column(String, primary_key=True) 

    # def __repr__(self):
    #     pass

if __name__ == '__main__':
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine("sqlite:///parl.db", echo=True)

    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine) # or sessionmaker(); Session.configure(bind=engine)

    session = Session() # now have a conversation w the database
    
    # sqlalchemy example...
    # 
    # ed_user= User(name='ed', fullname='ed balls', password='pwud')
    # session.add(ed_user)
    # session.commit()

    # for instance in session.query(User).order_by(User.id):
    #     print (instance.name, instance.fullname)


