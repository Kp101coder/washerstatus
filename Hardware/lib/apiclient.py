import requests
import time
import network
import os
from lib.dynamicResponse import DynamicResponse
from lib.controller import Pico

ssid = "utexas-iot"
password = "17981954548150055250"
#ip = "128.62.67.220" #Utexas wifi global ip of computer
#ip = "10.57.205.213" #Local ip of computer
ip = "57.132.171.87" #Home ip global -> rpi

class Client:

    def __init__(self, VERSION, controller : Pico):
        self.VERSION = VERSION
        self.pico = controller
        self.wlan = network.WLAN(network.STA_IF)
        self.connect_wifi()
        self.machineID = self.__find_ID()

    def connect_wifi(self) -> None:
        """Connect to wifi"""
        self.pico.setLED(True)
        self.wlan.active(True)
        self.wlan.connect(ssid, password)

        self.ip = self.wlan.ifconfig()[0]

        # Wait until connected
        counter = 0
        while not self.wlan.isconnected():
            counter += 1
            if(counter > 100):
                self.pico.reset()
            self.pico.displayText(f"Connecting {counter}", 0, 0)
            time.sleep(1)
        
        print("Connected to WiFi", self.wlan.ifconfig())
        self.pico.setLED(False)

    def is_connected(self) -> bool:
        """Returns whether connected to wifi or not"""
        return self.wlan.isconnected()

    def get_ID(self) -> int:
        """Returns the id of this machine"""
        return self.machineID

    def __find_ID(self) -> int:
        """Gets the machine id from the saved file on the controller\n
        If it does not exist, it will create the next id and a new machine row on the server"""
        machineID = None
        if self.file_exists("machineID.txt"):
            with open("machineID.txt", "r") as f:
                machineID = f.read()
        else:
            machineID = self.__create_machine()
            with open("machineID.txt", "w+") as f:
                f.write(str(machineID))
        return machineID

    def __create_machine(self) -> int:
        """Sends a request to create a new machine row and returns the id"""
        data = {
            'version' : self.VERSION,
            'ip' : self.ip
        }
        return int(self.__post("/machines/", data).get('id'))

    def __request(self, request) -> DynamicResponse:
        """Returns a JSON formatted dictionary of a get request"""
        if not self.is_connected():
            self.connect_wifi()
        elif request == None:
            raise Exception("Request must not be null")
        
        self.pico.setLED(True)

        try:
            url = f"http://{ip}:7106{request}"
            response = requests.get(url)
            dynResponse = DynamicResponse(response.json(), response.status_code)         
            response.close()  # Close the response object
            self.pico.setLED(False)
            return dynResponse
        except Exception as e:
            print("Error:", str(e))
            self.pico.setLED(False)
            return DynamicResponse({'detail' : str(e)}, -1)

    def __set(self, request) -> DynamicResponse:
        """Returns a JSON formatted dictionary of a put request"""
        if not self.is_connected():
            self.connect_wifi()
        elif request == None:
            raise Exception("Request must not be null")

        self.pico.setLED(True)

        try:
            url = f"http://{ip}:7106{request}"
            response = requests.put(url)
            dynResponse = DynamicResponse(response.json(), response.status_code)         
            response.close()  # Close the response object
            self.pico.setLED(False)
            return dynResponse
        except Exception as e:
            print("Error:", str(e))
            self.pico.setLED(False)
            return DynamicResponse({'Error' : str(e)}, -1)

    def __post(self, request, data) -> DynamicResponse:
        """Returns a JSON formatted dictionary"""
        if not self.is_connected():
            self.connect_wifi()
        elif request == None:
            raise Exception("Request must not be null")
        
        self.pico.setLED(True)

        try:
            url = f"http://{ip}:7106{request}"
            response = requests.post(url, json=data)
            dynResponse = DynamicResponse(response.json(), response.status_code)         
            response.close()  # Close the response object
            self.pico.setLED(False)
            return dynResponse
        except Exception as e:
            print("Error:", str(e))
            self.pico.setLED(False)
            return DynamicResponse({'detail' : str(e)}, -1)

    def get_isRunning(self) -> bool:
        """Returns the status of isRunning on the server"""
        return self.get_machine().get('isRunning')
    
    def get_hasClothes(self) -> bool:
        """Returns the status of hasClothes on the server"""
        return self.get_machine().get('hasClothes')
    
    def set_isRunning(self, status : bool) -> DynamicResponse:
        """Updates the status of isRunning on the server and returns the status of isRunning on the server"""
        return self.__set(f"/machines/{self.machineID}/update/running/{status}")
    
    def set_hasClothes(self, status : bool) -> DynamicResponse:
        """Updates the status of hasClothes on the server and returns the status of hasClothes on the server"""
        return self.__set(f"/machines/{self.machineID}/update/clothes/{status}")

    def set_doorOpen(self, status : bool) -> DynamicResponse:
        """Updates the status of doorOpen on the server and returns the status of doorOpen on the server"""
        return self.__set(f"/machines/{self.machineID}/update/doorOpen/{status}")

    def get_doorOpen(self) -> bool:
        """Returns the status of doorOpen on the server"""
        return self.get_machine().get('doorOpen')

    def set_ip(self, ip) -> str:
        """Updates the machines ip on the server and returns the new mahcine ip on the server"""
        return self.__set(f"/machines/{self.machineID}/update/ip/{ip}").get("ip")

    def set_version(self, version) -> float:
        """Updates the machines version on the server and returns the new mahcine version on the server"""
        return self.__set(f"/machines/{self.machineID}/update/ip/{version}").get('version')

    def get_machine(self) -> DynamicResponse:
        """Gets the full machine data and returns it as a dynamic response object"""
        return self.__request(f"/machines/{self.machineID}")

    def get_software_update(self) -> DynamicResponse:
        """Gets the latest update data and returns it as a dynamic response object"""
        return self.__request(f"/updates/last")

    def get_last_update(self) -> str:
        update = self.get_machine().get('lastUpdate')
        while(update == None):
            self.wlan.disconnect()
            self.connect_wifi()
            update = self.get_machine().get('lastUpdate')
        return update

    def file_exists(self, filepath) -> bool:
        """Returns if a file exists or not using the os.stat method"""
        try:
            os.stat(filepath)
            return True
        except OSError:
            return False