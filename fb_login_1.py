from seleniumwire import webdriver           
from webdriver_manager.chrome import ChromeDriverManager

import time,os,json

email = 'niknolti1@yandex.com'
password = 'nim12345'

class fbLogin:


	"""

	Use this to login to fb with 
	a Selenium like tool.

	Dependencies: Chrome driver, active user on FB
	and his credentials. 

	Main method is create_headers. 
	It will create authed_headers 
	and will save them in the header_files dir.

	
	"""	


	headers = {
		'authority': 'www.facebook.com', 
		'pragma': 'no-cache', 
		'cache-control': 'no-cache', 
		'sec-ch-ua-mobile': '?0', 
		'viewport-width': '881', 
		'content-type': 'application/x-www-form-urlencoded', 
		'accept': '*/*', 'origin': 'https://www.facebook.com', 
		'sec-fetch-site': 'same-origin', 'sec-fetch-mode': 
		'cors', 'sec-fetch-dest': 'empty', 
		'referer': 'https://www.facebook.com/', 
		'accept-language': 'en-US,en;q=0.9', 
	}
	
	BASE = os.getcwd()
	driver_path = BASE + '/chromedriver'
	headers_path = BASE + '/header_files/'

	def create_headers(self,email,password):

		options = webdriver.ChromeOptions()
		options.add_argument("--headless")
		with webdriver.Chrome(executable_path=ChromeDriverManager().install(),options=options) as driver:
			
			cookie,ua = self.login_to_fb(driver,email,password)
		  	# self.headers['cookie'] = cookie
		  	# self.headers['user-agent'] = ua
		  	# filename = email[:email.index('@')]
		  	export_file_path = self.headers_path + filename + '.json'
		  	with open(export_file_path,'w') as outputfile:
				json.dump(self.headers, outputfile,indent=4)


	@staticmethod
	def login_to_fb(driver,email,password):
		url = 'https://www.facebook.com/login'
		login_page = driver.get(url);time.sleep(2)
		inputElement = driver.find_element_by_id("email")
		inputElement.send_keys(email);time.sleep(1)
		inputElement = driver.find_element_by_id("pass")
		inputElement.send_keys(password)
		inputElement.submit();time.sleep(10)
		for request in driver.requests:
			if 'https://www.facebook.com/?sk=welcome' in request.url:
				return request.headers['Cookie'],request.headers['user-agent']


if __name__ == '__main__':

	fbLogin().create_headers(email,password)
