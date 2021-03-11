import requests,json,time,random,re

from fb_login import fbLogin


class fbSearch(fbLogin):

	"""
	search fb for groups,people and pages using a keyword. 

	Dependencies: AUTHED HEADERS via the fbLogin class.

	init: path to authed_headers

	main methods get_fb_full_serp,get_all_fb_results
	use them to get all results for fb search. 

	both return JSON to dump / save to db.
	"""

	graphql_url = 'https://web.facebook.com/api/graphql/'

	def __init__(self,headers_path):
		super().__init__()
		self.headers_path = headers_path
		try:
			with open(self.headers_path,'r') as inputfile:
				self.headers = json.load(inputfile)
		except Exception:
			raise 'cant get headers'


	def get_fb_full_serp(self,keyword):
		groups = self.get_all_fb_results(keyword)
		pages = self.get_all_fb_results(keyword,search_type='PAGES_TAB')
		people = self.get_all_fb_results(keyword,search_type='PEOPLE_TAB')
		return {
			'keyword'	   : keyword,
			'groups_data'  : groups,
			'pages_data'   : pages,
			'people_data'  : people,
			'headers' 	   : self.headers,
			'headers_path' : self.headers_path
		}



	
	def get_all_fb_results(self,keyword,search_type='GROUPS_TAB',max_depth=50,start_depth=1):
		# for pages ->> search_type='PAGES_TAB'
		# for people ->> search_type='PEOPLE_TAB'
		__user,fb_dtsg = self.get_user_av_and_dtsg()
		data = self.create_request_data(keyword,__user,fb_dtsg,search_type)
		
		serp_response = self.get_serp_page(data)
		print(serp_response)
		
		collected_data = self.parse_serp_results(serp_response,keyword)
		# has_next_page,next_cursor = self.get_next_page_and_cursor(serp_response)
		# while has_next_page:
		# 	print(len(collected_data))
		# 	print(f'depth status: {start_depth}/{max_depth}')
		# 	if start_depth >= max_depth:
		# 		break
		# 	else:
		# 		data = self.create_request_data(keyword,__user,fb_dtsg,search_type,cursor=next_cursor)
		# 		serp_response = self.get_serp_page(data)
		# 		collected_data += self.parse_serp_results(serp_response,keyword)
		# 		has_next_page,next_cursor = self.get_next_page_and_cursor(serp_response)
		# 		start_depth += 1    
		# return {
		# 'keyword'  	   : keyword,
		# 'search_type'  : search_type,
		# 'results' 	   : collected_data,
		# }

	def get_user_av_and_dtsg(self):
		search_url = 'https://web.facebook.com/search/'
		search_page_response = requests.get(search_url,headers=self.headers)
		# print(search_page_response)
		__user = self.get_user_av(search_page_response)
		dtsg = self.get_dtsg(search_page_response)
		return __user,dtsg


	def get_serp_page(self,data):
		sleep_time = random.uniform(5,15)
		response = requests.post(self.graphql_url, headers=self.headers, data=data)
		# print(response.text)
		print(f'sleeping for {sleep_time}')
		time.sleep(sleep_time)
		try:
			res = response.text
			return json.loads(res.splitlines()[0])
		except Exception as err:
			# print(response.text)
			exit('failed to parse JSON')

	def create_request_data(self,keyword,__user,fb_dtsg,search_type,cursor='null'):
		variables = self.create_variables_for_data(keyword,cursor,search_type)
		data = {
			"av": __user, # taken from search page
			"__user": __user, # taken from search page
			"fb_dtsg": fb_dtsg, # taken from search page
			"fb_api_caller_class": "RelayModern",
			"fb_api_req_friendly_name": "SearchCometResultsPaginatedResultsQuery",
			"variables": {},#json.dumps(json.loads(f'{variables}')),
			"server_timestamps": "true",
			"doc_id": "4044805855551767"
		}
		print(data)
		return data

	@staticmethod
	def get_user_av(search_page_response):
		__user_regex = r'__user=([0-9+]+)&'
		# print(search_page_response)
		return re.findall(__user_regex,search_page_response.text)[0]

	@staticmethod
	def get_dtsg(search_page_response):
		regext_dtsg = r'\"DTSGInitData\",\[\],{\"token\":"(.+)\",\"async_get_token'
		return re.findall(regext_dtsg,search_page_response.text)[0]

	@staticmethod
	def create_variables_for_data(keyword,cursor,search_type):
	    variables = """{
	        "UFI2CommentsProvider_commentsKey": "SearchCometResultsInitialResultsQuery",
	        "allow_streaming": false,
	        "args": {
	            "callsite": "COMET_GLOBAL_SEARCH",
	            "config": {
	                "bootstrap_config": null,
	                "exact_match": false,
	                "high_confidence_config": null,
	                "sts_disambiguation": null,
	                "watch_config": null
	            },
	            "experience": {
	                "encoded_server_defined_params": null,
	                "fbid": null,
	                "type": "%s"
	            },
	            "filters": [],
	            "text": "%s"
	        },
	        "count": 5,
	        "cursor": "%s",
	        "displayCommentsContextEnableComment": false,
	        "displayCommentsContextIsAdPreview": false,
	        "displayCommentsContextIsAggregatedShare": false,
	        "displayCommentsContextIsStorySet": false,
	        "displayCommentsFeedbackContext": null,
	        "feedLocation": "SEARCH",
	        "fetch_filters": true
	      }""" % (search_type,keyword,cursor)
	    return variables

	@staticmethod
	def parse_serp_results(serp_response,keyword):
	    new_list = list()
	    edges = serp_response['data']['serpResponse']['results']['edges']
	    for edge in edges:
	        edge_to_append = dict()
	        edge_model = edge['relay_rendering_strategy']['view_model']
	        if 'profile' in edge_model.keys():
	            if keyword.lower() in edge_model['profile']['name'].lower():
	                edge_to_append['page_info'] = edge_model['profile']
	                if 'body_snippet_configs' in edge_model.keys():
	                    edge_to_append['body_snippet'] = edge_model['body_snippet_configs']
	                else:
	                    edge_to_append['body_snippet'] = None
	                if 'meta_snippet_configs' in edge_model.keys():
	                    edge_to_append['metadata'] = edge_model['meta_snippet_configs']
	                else:
	                    edge_to_append['metadata'] = None
	                new_list.append(edge_to_append)
	            else:
	                print(edge_model['profile']['name'])
	    return new_list

	@staticmethod
	def get_next_page_and_cursor(serp_response):
	    next_cursor = serp_response['data']['serpResponse']['results']['page_info']['end_cursor']
	    has_next_page = serp_response['data']['serpResponse']['results']['page_info']['has_next_page']
	    return has_next_page,next_cursor

if __name__ == '__main__':
	keyword = 'clp'
	fb = fbSearch('/home/allen/Desktop/scrapy-test/fb_getter/header_files/gyedidigitalqr.json')
	j_data = fb.get_all_fb_results(keyword)
	with open(f'{keyword}.json','w') as output:
	    json.dump(j_data, output,indent=4)

	