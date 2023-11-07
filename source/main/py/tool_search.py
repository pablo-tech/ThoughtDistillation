import time

from langchain.agents import Tool

from langchain.utilities import SerpAPIWrapper
from serpapi import GoogleSearch

from llm_select import ToolSelect


class SerpEngine(SerpAPIWrapper):
# https://github.com/langchain-ai/langchain/blob/master/libs/langchain/langchain/utilities/serpapi.py
    
    def __init__(self):
        # https://serpapi.com/dashboard
        super().__init__(serpapi_api_key = '2c24c5acccd4ab1f8644348773293cac5aa6907314eb0685ab2d8ad3d75e528d')

    def configurable_results(self, query):
        params = self.configurable_params(query)
        engine = GoogleSearch(params)
        results = engine.get_dict()
        return results 

    def configurable_params(self, query, k=15):
        # https://serpapi.com/search-api
        return {'api_key': self.serpapi_api_key,
                'q': query,
                'num': k,                 
                'engine': 'google', 
                'google_domain': 'google.com', 
                'hl': 'en', 
                'gl': 'us', 
                'device': 'desktop'}
    

class SerpSearch(SerpEngine):

    def __init__(self):
        super().__init__()

    def organic(self, results):
        try:
          organic = results["organic_results"]
          # print(results["search_information"])
          # print(str(organic))
          # print(str(results.keys()))
          return organic
        except:
          print(str(results['error']))
          print(str(results))

    def info(self, query):
        return self.select(query)["search_information"]

    def pagination(self, query):
        return self.select(query)['serpapi_pagination']

    def select(self, query):
        return self.configurable_results(query)
    

class SearchSerpResult(ToolSelect):

    def __init__(self, completion_llm, is_verbose):
        super().__init__("SERP", completion_llm, is_verbose)
        self.search_engine = SerpSearch()
        self.completion_llm = completion_llm
        self.is_verbose = is_verbose

    def run(self, tool_input, user_query=""):
        return self.invoke(tool_input, self.select)
    
    def select(self, query):
        results = self.subquery(query), query
        return self.answer(self.summarize(results, query), query)
            
    # def answer(self, results, query):
    #     return [result for result in results]

    # def summarize(self, results, query):
    #     return [result for result in results]

    def subquery(self, query):
        results = self.search_engine.select(query)
        results = self.search_engine.organic(results)
        return [result['snippet'] for result in results]
    

class SearchToolFactory():

    def __init__(self, completion_llm, is_verbose=False):
        self.completion_llm = completion_llm
        self.is_verbose = is_verbose

    def get_tools(self):
        api = SearchSerpResult(self.completion_llm, self.is_verbose)
        return [
            Tool(
              name="Search",
              func=api.run,
              description="useful to answer questions about current events or the current state of the world"
        )]

