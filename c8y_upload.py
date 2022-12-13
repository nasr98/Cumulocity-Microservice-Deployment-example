import requests as rq
import subprocess
import configparser


class build_push:
    def __init__ (self,url,token,app_name):
        self.url = url
        self.token = token
        self.app_name = app_name
    
    def build_ms(self,app_name):
        build_cmd = "docker build -t {x} .".format(x=self.app_name)
        save_cmd = "docker save {x} > 'image.tar'".format(x=self.app_name)
        zip_cmd = "zip {x} cumulocity.json image.tar".format(x=self.app_name)

        subprocess.call(build_cmd, shell=True)
        subprocess.call(save_cmd, shell=True)
        subprocess.call(zip_cmd, shell=True)

    def push_ms(self,url,token,app_name):
        u1 = self.url + "/application/applications"
        b1 = {"key": "{x}-key".format(x=self.app_name),"name": "{x}".format(x=self.app_name),"type": "MICROSERVICE","requiredRoles": [ "ROLE_INVENTORY_READ" ],"roles": [ "ROLE_CUSTOM_MICROSERVICE" ]}
        u2 = self.url + "/application/applicationsByName/{x}".format(x=self.app_name)
        u3 = self.url + "/application/applications/{x}/binaries".format(x=self.app_name)
        fileobj = open('{x}.zip'.format(x=self.app_name), 'rb')

        req1 = rq.post(u1,json=b1,headers={'Authorization': self.token})
        req2 = rq.get(u2,headers={'Authorization': self.token})
        app_id = req2.json()['applications'][0]['id']

        u3 = self.url + "/application/applications/{x}/binaries".format(x=app_id)
        req3 = rq.post(u3,headers={'Authorization': self.token},files={"file": ("file.zip", fileobj)})

        if req3.status_code == 201:
            print("Successfully Uploaded Microservice to platform")
        else: 
            print("Upload Failed")
    
    def main(self):
        self.build_ms(self.app_name)
        self.push_ms(self.url,self.token,self.app_name)

if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('conf.ini')
    url = config['C8Y_Details']['url']
    token = config['C8Y_Details']['token']
    app_name = config['C8Y_Details']['app_name']
    build_push(url,token,app_name).main()