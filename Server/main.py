from fastapi import FastAPI, HTTPException, Depends, status, UploadFile
from pydantic import BaseModel, Field
from typing import Annotated
from sqlalchemy.exc import IntegrityError
from models import *
from database import engine, SessionLocal, URL_DATABASE
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import time
import os
import subprocess
from databases import Database

app = FastAPI()

'''origins = [
    
]

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins
)'''

Base.metadata.create_all(bind = engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
dataBase = Database(URL_DATABASE)

SEC_TO_MIN = 60
#uvicorn main:app --reload --host 0.0.0.0 --port 7106

class PostBase(BaseModel):
    title: str = Field(alias="Post Title")
    content: str = Field(alias="Post Content")
    userID: int = Field(alias="User ID")
    floorID: int = Field(alias="Floor ID")

class UserBase(BaseModel):
    userName: str = Field(alias="User Name")
    userPassword: str = Field(alias="User Password")

class MachineBase(BaseModel):
    isRunning : bool = Field(False)
    hasClothes : bool = Field(False)
    doorOpen : bool = Field(False)
    version : float = Field(0.0)
    ip : str = Field("Machine IP")

class RoomBase(BaseModel):
    roomName : str = Field(alias = "Room Name")
    floorID : int = Field(alias = "Floor ID")

class FloorBase(BaseModel):
    floorName : str = Field(alias = "Floor Name")
    buildingID : int = Field(alias = "Building ID")

class BuildingBase(BaseModel):
    buildName : str = Field(alias = "Building Name")
    locationID : int = Field(alias = "Location ID")

class LocationBase(BaseModel):
    locationName : str = Field(alias = "Location Name")
    orgID : int = Field(alias = "Organization ID")

class OrganizationBase(BaseModel):
    orgName : str = Field(alias = "Organization Name")

def userFunctions():
    """User functions for API requests"""
    #Create User
    @app.post("/users/", status_code = status.HTTP_201_CREATED)
    async def create_user(postb: UserBase, db: db_dependency):
        user = User(**postb.model_dump())
        db.add(user)
        try:
            # Attempt to commit the transaction
            db.commit()
            db.refresh(user)
        except IntegrityError as e:
            db.rollback()  # Roll back the transaction in case of error
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with the same username already exists."
            )
        return user

    #Get User by ID
    @app.get("/users/{user_id}", status_code = status.HTTP_200_OK)
    async def read_user(user_id: int, db: db_dependency):
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "User not found")
        return user

    def user_by_name(user_name: str, db: db_dependency):
        user = db.query(User).filter(User.userName == user_name).first()
        if user is None:
            raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "User not found")
        return user

    #Get User by User Name
    @app.get("/users/name/{user_name}", status_code = status.HTTP_200_OK)
    async def read_user_by_name(user_name: str, db: db_dependency):
        return user_by_name(user_name, db)
    
    #Get all Users with a string in their name
    @app.get("/users/name/contain/{string}", status_code = status.HTTP_200_OK)
    async def read_user_by_string(string: str, db: db_dependency):
        users = db.query(User).filter(User.userName.contains(string)).all()
        if not users:
            raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Users with Names were not found")
        return users

    #Get All Posts by User ID
    @app.get("/users/posts/{user_id}", status_code=status.HTTP_200_OK)
    async def read_all_posts_by_userid(user_id: int, db: db_dependency):
        user = db.query(User).filter(User.id == user_id).first()
        posts = user.posts  # This gives you all related locations
        if not posts:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Posts were not found")
        return posts
    
    #Signs a user in by there username and password
    @app.put("/users/{username}/signin/{password}", status_code=status.HTTP_200_OK)
    async def sign_in_user(username : str, password: str, db : db_dependency):
        user = user_by_name(username, db)
        if not (user.userPassword == password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect Password")
        user.lastSignIn = datetime.now().strftime("%m/%d/%Y %I:%M %p")
        db.commit()
        db.refresh(user)
        return user

def postFunctions():
    """Post specific functions for API requests"""
    #Create Post
    @app.post("/posts/", status_code = status.HTTP_201_CREATED)
    async def create_post(postb: PostBase, db: db_dependency):
        post = Post(**postb.model_dump())
        db.add(post)
        db.commit()
        db.refresh(post)
        return post

    #Delete Post
    @app.delete("/posts/delete/{post_id}", status_code = status.HTTP_200_OK)
    async def delete_post(post_id: int, db: db_dependency):
        post = db.query(Post).filter(Post.id == post_id).first()
        details = post.__dict__()
        if post is None:
            raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Post was not found")
        db.delete(post)
        db.commit()
        return details

    #Get Post by ID
    @app.get("/posts/{post_id}", status_code = status.HTTP_200_OK)
    async def read_post(post_id: int, db: db_dependency):
        post = db.query(Post).filter(Post.id == post_id).first()
        if post is None:
            raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Post was not found")
        return post

    #Get All Posts that have string in title
    @app.get("/posts/titles/{title}", status_code = status.HTTP_200_OK)
    async def read_post_by_title(title: str, db: db_dependency):
        posts = db.query(Post).filter(Post.title.contains(title)).all()
        if not posts:
            raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Posts were not found")
        return posts

def updateFunctions():
    """Update functions for creating and getting the code updates.\n
    Upload or get code files that add or edit the existing files.\n
    The actual updating is handled by the update file sent over."""
    #Create a new update
    @app.post("/updates/{new_version}", status_code = status.HTTP_201_CREATED)
    async def create_update(new_version : float, file: UploadFile, db: db_dependency):
        try:
            contents = file.file.read()
            with open(file.filename, 'wb') as f:
                f.write(contents)
        except Exception:
            return {"message": "There was an error uploading the file"}
        finally:
            file.file.close()

        update = Updates(filename = file.filename, version = new_version)
        db.add(update)
        db.commit()

        db.refresh(update)
        return update

    #Get the new ipdate by id
    @app.get("/updates/{id}", status_code = status.HTTP_200_OK)
    async def get_update(id : int, db: db_dependency):
        update = None
        try:
            update_file = db.query(Updates).filter(Updates.id == id).first()

            if update_file == None:
                raise HTTPException("File not found")

            with open(update_file.filename, 'rb') as f:
                update = f.read()
        except Exception:
            return {"detail": "There was an error getting the file"}
        finally:
            return update

    #Get the latest update and return the details
    @app.get("/updates/last", status_code = status.HTTP_200_OK)
    async def get_update_details(db: db_dependency):
        update = db.query(Updates).order_by(Updates.id.desc()).first()

        if update == None:
            raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Update ID not found")

        return update
    
    #Delete Update and Stored File
    @app.delete("/updates/delete/{id}", status_code = status.HTTP_200_OK)
    async def delete_update(id: int, db: db_dependency):
        update = db.query(Updates).filter(Updates.id == id).first()
        if update is None:
            raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Post was not found")
        os.remove(update.filename)
        db.delete(update)
        db.commit()

def machineFunctions():
    """Machine functions for creating a new machine, updating the status of the machine, and changing server stored details of the machine"""
    #Create Machine
    @app.post("/machines/", status_code = status.HTTP_201_CREATED)
    async def create_machine(machineb: MachineBase, db: db_dependency):
        machine = Machine(**machineb.model_dump())
        machine.lastUpdate = datetime.now().strftime("%m/%d/%Y %I:%M %p")
        db.add(machine)
        db.commit()
        db.refresh(machine)
        return machine
    
    #Get a machine by id
    @app.get("/machines/{machine_id}", status_code=status.HTTP_200_OK)
    async def read_machine(machine_id : int, db: db_dependency):
        machine = db.query(Machine).order_by(Machine.id == machine_id).first()

        if not machine:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No machine was found")
        
        if not (machine.timeRun == None):
            machine.timeRun = int((time.time()/SEC_TO_MIN)-machine.timeRun)
        
        return machine
    
    #Set the state of isRunning of the machine
    @app.put("/machines/{machine_id}/update/running/{state}", status_code=status.HTTP_202_ACCEPTED)
    async def update_machine_running(machine_id: int, state : bool, db: db_dependency):
        # Get the machine by ID
        machine = db.query(Machine).filter(Machine.id == machine_id).first()

        if machine is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Machine not found")

        # Update the isRunning field
        machine.isRunning = state

        if state:
            machine.timeRun = int(time.time()/SEC_TO_MIN)
        else:
            machine.timeRun = None

        #Update the last updated time
        machine.lastUpdate = datetime.now().strftime("%m/%d/%Y %I:%M %p")

        db.commit()

        db.refresh(machine)
        return machine

    #Set the state of hasClothes of the machine
    @app.put("/machines/{machine_id}/update/clothes/{state}", status_code=status.HTTP_202_ACCEPTED)
    async def update_machine_clothes(machine_id: int, state : bool, db: db_dependency):
        # Get the machine by ID
        machine = db.query(Machine).filter(Machine.id == machine_id).first()

        if machine is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Machine not found")

        # Update the isRunning field
        machine.hasClothes = state

        #Update the last updated time
        machine.lastUpdate = datetime.now().strftime("%m/%d/%Y %I:%M %p")

        db.commit()

        db.refresh(machine)
        return machine

    #Update the current version of the machine's code stored on the server
    @app.put("/machines/{machine_id}/update/version/{curVersion}", status_code=status.HTTP_202_ACCEPTED)
    async def update_machine_version(machine_id: int, curVersion : float, db: db_dependency):
        # Get the machine by ID
        machine = db.query(Machine).filter(Machine.id == machine_id).first()

        if machine is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Machine not found")

        # Update the isRunning field
        machine.version = curVersion

        db.commit()

        db.refresh(machine)
        return machine

    #Update the current ip of the machine stored on server
    @app.put("/machines/{machine_id}/update/ip/{curIP}", status_code=status.HTTP_202_ACCEPTED)
    async def update_machine_ip(machine_id: int, curIP : str, db: db_dependency):
        # Get the machine by ID
        machine = db.query(Machine).filter(Machine.id == machine_id).first()

        if machine is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Machine not found")

        # Update the isRunning field
        machine.ip = curIP

        db.commit()

        db.refresh(machine)
        return machine
    
    #Update the roomID of the machine
    @app.put("/machines/{machine_id}/update/roomID/{roomID}", status_code=status.HTTP_202_ACCEPTED)
    async def update_machine_roomID(machine_id: int, roomID : int, db: db_dependency):
        # Get the machine by ID
        machine = db.query(Machine).filter(Machine.id == machine_id).first()

        if machine is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Machine not found")

        # Update the isRunning field
        machine.roomID = roomID

        db.commit()

        db.refresh(machine)
        return machine
    
    #Update the state of door open of the machine
    @app.put("/machines/{machine_id}/update/doorOpen/{isOpen}", status_code=status.HTTP_202_ACCEPTED)
    async def update_machine_doorOpen(machine_id: int, isOpen : bool, db: db_dependency):
        # Get the machine by ID
        machine = db.query(Machine).filter(Machine.id == machine_id).first()

        if machine is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Machine not found")

        # Update the isRunning field
        machine.doorOpen = isOpen

        db.commit()

        db.refresh(machine)
        return machine
    
    #Update the current location of the machine
    @app.put("/machines/{machine_id}/update/loc/{loc}", status_code=status.HTTP_202_ACCEPTED)
    async def update_machine_loc(machine_id: int, loc : str, db: db_dependency):
        # Get the machine by ID
        machine = db.query(Machine).filter(Machine.id == machine_id).first()

        if machine is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Machine not found")

        # Update the isRunning field
        machine.relLoc = loc

        db.commit()

        db.refresh(machine)
        return machine

def roomFunctions():
    """Room Functions for creating rooms and getting information on them"""
    #Create a new floor
    @app.post("/rooms/", status_code = status.HTTP_201_CREATED)
    async def create_room(roomb: RoomBase, db: db_dependency):
        room = Room(**roomb.model_dump())
        db.add(room)
        db.commit()
        db.refresh(room)
        return room

    # Get all machines that are part of an Room
    @app.get("/rooms/{id}/machines", status_code=status.HTTP_200_OK)
    def get_machines_by_room(id: int, db: db_dependency):
        
        machines = (
            db.query(Machine)
            .join(Room)
            .filter(Room.id == id)
            .all()
        )

        if not machines:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No machines found for this organization")

        for machine in machines:
            if not (machine.timeRun == None):
                machine.timeRun = int((time.time()/SEC_TO_MIN)-machine.timeRun)

        return machines

def floorFunctions():
    """Floor Functions for creating floors and getting information on them"""
    #Create a new floor
    @app.post("/floors/", status_code = status.HTTP_201_CREATED)
    async def create_floor(floorb: FloorBase, db: db_dependency):
        floor = Floor(**floorb.model_dump())
        db.add(floor)
        db.commit()
        db.refresh(floor)
        return floor

    #Get all rooms on a floor by id
    @app.get("/floors/{id}/rooms", status_code = status.HTTP_200_OK)
    async def read_all_rooms(id : int, db: db_dependency):
        floor = db.query(Floor).order_by(Floor.id == id).first()

        if not floor:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No rooms were found")
        
        return floor.rooms
    
    #Get All Posts on floor by id
    @app.get("/floors/{floor_id}/posts", status_code=status.HTTP_200_OK)
    async def read_all_posts(floor_id: int, db: db_dependency):
        floor = db.query(Floor).filter(Floor.id == floor_id).first()
        posts = floor.posts
        if not posts:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Posts were not found")
        return posts
    
    # Get all machines that are part of an Floor
    @app.get("/floors/{id}/machines", status_code=status.HTTP_200_OK)
    def get_machines_by_floor(id: int, db: db_dependency):
        
        machines = (
            db.query(Machine)
            .join(Room)
            .join(Floor)
            .filter(Floor.id == id)
            .all()
        )

        for machine in machines:
            if not (machine.timeRun == None):
                machine.timeRun = int((time.time()/SEC_TO_MIN)-machine.timeRun)

        if not machines:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No machines found for this organization")

        return machines

def buildingFunctions():
    """Building Functions for creating buildings and getting information on them"""
    #Create a new floor
    @app.post("/buildings/", status_code = status.HTTP_201_CREATED)
    async def create_building(buildb: BuildingBase, db: db_dependency):
        build = Building(**buildb.model_dump())
        db.add(build)
        db.commit()
        db.refresh(build)
        return build

    #Get all floors in a building by id
    @app.get("/buildings/{id}/floors", status_code = status.HTTP_200_OK)
    async def read_all_floors(id : int, db: db_dependency):
        build = db.query(Building).order_by(Building.id == id).first()

        if not build:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No buildings were found")
        
        return build.floors
    
    # Get all machines that are part of an Building
    @app.get("/buildings/{id}/machines", status_code=status.HTTP_200_OK)
    def get_machines_by_building(id: int, db: db_dependency):
        
        machines = (
            db.query(Machine)
            .join(Room)
            .join(Floor)
            .join(Building)
            .filter(Building.id == id)
            .all()
        )

        for machine in machines:
            if not (machine.timeRun == None):
                machine.timeRun = int((time.time()/SEC_TO_MIN)-machine.timeRun)

        if not machines:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No machines found for this organization")

        return machines

def locationFunctions():
    """Location Functions for creating Locations and getting information on them"""
    #Create a new location
    @app.post("/locations/", status_code = status.HTTP_201_CREATED)
    async def create_loc(locb: LocationBase, db: db_dependency):
        loc = Location(**locb.model_dump())
        db.add(loc)
        db.commit()
        db.refresh(loc)
        return loc

    #Get all buildings at a location by id
    @app.get("/locations/{id}/buildings", status_code = status.HTTP_200_OK)
    async def read_all_buildings(id : int, db: db_dependency):
        loc = db.query(Location).order_by(Location.id == id).first()

        if not loc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No locations were found")
        
        return loc.buildings
    
    # Get all machines that are part of an Location
    @app.get("/locations/{id}/machines", status_code=status.HTTP_200_OK)
    def get_machines_by_location(id: int, db: db_dependency):
        
        machines = (
            db.query(Machine)
            .join(Room)
            .join(Floor)
            .join(Building)
            .join(Location)
            .filter(Location.id == id)
            .all()
        )

        for machine in machines:
            if not (machine.timeRun == None):
                machine.timeRun = int((time.time()/SEC_TO_MIN)-machine.timeRun)

        if not machines:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No machines found for this organization")

        return machines

def organizationFunctions():
    """Organization Functions for creating organizations and getting information on them"""
    #Create a new organization
    @app.post("/organizations/", status_code = status.HTTP_201_CREATED)
    async def create_org(orgb: OrganizationBase, db: db_dependency):
        org = Organization(**orgb.model_dump())
        db.add(org)
        db.commit()
        db.refresh(org)
        return org

    #Get all locations within an organization by id
    @app.get("/organizations/{id}/locations", status_code = status.HTTP_200_OK)
    async def get_all_locations(id : int, db: db_dependency):
        org = db.query(Organization).order_by(Organization.id == id).first()

        if not org:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No rooms were found")
        
        return org.locations
    
    # Get all machines that are part of an organization
    @app.get("/organizations/{id}/machines", status_code=status.HTTP_200_OK)
    def get_machines_by_organization(id: int, db: db_dependency):
        
        machines = (
            db.query(Machine)
            .join(Room)
            .join(Floor)
            .join(Building)
            .join(Location)
            .join(Organization)
            .filter(Organization.id == id)
            .all()
        )

        for machine in machines:
            if not (machine.timeRun == None):
                machine.timeRun = int((time.time()/SEC_TO_MIN)-machine.timeRun)

        if not machines:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No machines found for this organization")

        # Convert to dictionary form for the response (if not using Pydantic)
        return machines

    # Get all organizations
    @app.get("/organizations/all", status_code=status.HTTP_200_OK)
    def get_all_organizations(db: db_dependency):
        orgs = db.query(Organization).all()

        if not orgs:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No machines found for this organization")

        return orgs

def serverFunctions():
    # Reboot server
    @app.delete("/server/reboot", status_code=status.HTTP_202_ACCEPTED)
    async def reboot_server(db: db_dependency):
        os.system("sudo reboot")

    @app.put("/server/run/{command}", status_code=status.HTTP_202_ACCEPTED)
    async def run_command(command: str, db: db_dependency):
        try:
            return subprocess.run(command, capture_output=True, shell=True)
        except Exception as e:
            return str(e)

    @app.delete("/server/drop/{table}", status_code=status.HTTP_202_ACCEPTED)
    async def drop_table(table : str, db: db_dependency):
        try:
            await dataBase.connect()
            await dataBase.execute(query=f"DROP TABLE {table};")
            Base.metadata.create_all(bind = engine)
            await dataBase.disconnect()
        except Exception as e:
            return str(e)

    @app.put("/server/add/{table}/{column}/{colType}", status_code=status.HTTP_202_ACCEPTED)
    async def add_column(table: str, column : str, colType : str, db: db_dependency):
        try:
            await dataBase.connect()
            await dataBase.execute(query=f"ALTER TABLE {table} ADD COLUMN {column} {colType};")
            await dataBase.disconnect()
        except Exception as e:
            return str(e)

    @app.get("/server/get/{query}", status_code=status.HTTP_200_OK)
    async def get_data(query: str, db: db_dependency):
        try:
            await dataBase.connect()
            data =  await dataBase.fetch_all(query=query)
            await dataBase.disconnect()
            return data
        except Exception as e:
            return str(e)
'''
serverFunctions()

updateFunctions()

organizationFunctions()

locationFunctions()

buildingFunctions()

floorFunctions()

roomFunctions()

machineFunctions()

userFunctions()

postFunctions()
'''