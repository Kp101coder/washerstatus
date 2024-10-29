from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Float, BigInteger
from database import Base
from sqlalchemy.orm import relationship

class Organization(Base):
    __tablename__ = "organizations"
    id = Column("ID", Integer, primary_key = True, index = True)
    orgName = Column("Organization Name", String(50), unique = True)

    locations = relationship("Location", back_populates="organization")

class Location(Base):
    __tablename__ = "locations"
    id = Column("ID", Integer, primary_key = True, index = True)
    locationName = Column("Location Name", String(50), unique = True)
    orgID = Column("Organization ID", Integer, ForeignKey('organizations.ID'))  # Foreign key to Organization

    organization = relationship("Organization", back_populates="locations")
    buildings = relationship("Building", back_populates="location")

class Building(Base):
    __tablename__ = "buildings"
    id = Column("ID", Integer, primary_key = True, index = True)
    buildName = Column("Building Name", String(50), unique = True)
    locationID = Column("Location ID", Integer, ForeignKey('locations.ID'))  # Foreign key to Location

    location = relationship("Location", back_populates="buildings")
    floors = relationship("Floor", back_populates="building")

class Floor(Base):
    __tablename__ = "floors"
    id = Column("ID", Integer, primary_key = True, index = True)
    floorName = Column("Floor Name", String(50), unique = True)
    buildingID = Column("Building ID", Integer, ForeignKey('buildings.ID'))  # Foreign key to Building

    building = relationship("Building", back_populates="floors")
    rooms = relationship("Room", back_populates="floor")
    posts = relationship("Post", back_populates="floor") #Floors can have many posts tied to them

class Room(Base):
    __tablename__ = "rooms"
    id = Column("ID", Integer, primary_key = True, index = True)
    roomName = Column("Room Name", String(50), unique = True)
    floorID = Column("Floor ID", Integer, ForeignKey('floors.ID'))  # Foreign key to Floor

    floor = relationship("Floor", back_populates="rooms")
    machines = relationship("Machine", back_populates="room")

class Machine(Base):
    __tablename__ = "machines"
    id = Column("ID", Integer, primary_key = True, index = True)
    roomID = Column("Room ID", Integer, ForeignKey('rooms.ID'))  # Foreign key to Room
    relLoc = Column("Relative Location", String(100), unique=True)
    isRunning = Column("Is Running", Boolean)
    hasClothes = Column("Has Clothes", Boolean)
    doorOpen = Column("Door Open", Boolean)
    lastUpdate = Column("Last Update", String(30))
    version = Column("Version", Float)
    timeRun = Column("Time Running", BigInteger)
    ip = Column("Machine IP", String(15))

    room = relationship("Room", back_populates="machines")
    
class User(Base):
    __tablename__ = "users"
    id = Column("ID", Integer, primary_key = True, index = True)
    userName = Column("User Name", String(30), unique = True)
    userPassword = Column("User Password", String(30))
    lastSignIn = Column("Last Sign In", String(30))
    
    # Relationship: One user can have many posts
    posts = relationship("Post", back_populates="user")

class Post(Base):
    __tablename__ = 'posts'
    id = Column("ID", Integer, primary_key = True, index = True)
    title = Column("Post Title", String(30))
    content = Column("Post Content", String(200))

    # Foreign key to User
    userID = Column("User ID", Integer, ForeignKey('users.ID'))
    # Foreign key to Floor
    floorID = Column("Floor ID", Integer, ForeignKey('floors.ID'))

    # Relationships
    user = relationship("User", back_populates="posts")
    floor = relationship("Floor", back_populates="posts")

class Updates(Base):
    __tablename__ = "Updates"
    id = Column("ID", Integer, primary_key = True, index = True)
    filename = Column("Filename", String(30))
    version = Column("Version" , Float)