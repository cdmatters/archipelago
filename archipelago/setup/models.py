
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import  Column, Integer, String, Boolean, ForeignKey

Base = declarative_base()

# Note NO NICE PRINTING. Smarter schema: todo.

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
    Addresses = relationship("Address",
                            backref="mp",
                            primaryjoin="Address.OfficialId==MPCommons.OfficialId")
    Offices = relationship("Office", 
                            backref='mp',
                            primaryjoin="Office.PersonId==MPCommons.PersonId")

    # def __repr__(self):
    #     pass

class Office(Base):
    __tablename__ = 'Offices'

    PersonId = Column(Integer, ForeignKey(MPCommons.PersonId), primary_key=True)
    Office = Column(String, primary_key=True)
    StartDate = Column(String, primary_key=True)
    EndDate = Column(String)
    Name = Column(String)
    Title = Column(String, primary_key=True)

    def __repr__(self):
        return "<Office Type ( Name:'%s', Title:'%s', Office:'%s', StartDate'%s', EndDate:'%s')>" % (
                        self.Name, self.Title, self.Office, self.StartDate, self.EndDate)

class Address(Base):
    __tablename__ = 'Addresses'

    OfficialId = Column(Integer, ForeignKey(MPCommons.OfficialId), primary_key=True)
    AddressType = Column(String)
    Address = Column(String, primary_key=True) 

    # def __repr__(self):
    #     pass

if __name__ == '__main__':
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine("sqlite:///parl.db", echo=True)

    Base.metadata.create_all(engine)


