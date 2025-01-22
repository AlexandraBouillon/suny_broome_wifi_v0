from lib.graphql_client import GraphQLClient
from config.settings import ENDPOINT, API_KEY
from handlers.request_handler import RequestHandler
from utils.memory_profiler import MemoryProfiler

def main():
    client = GraphQLClient(ENDPOINT, API_KEY)
    handler = RequestHandler(client)
    profiler = MemoryProfiler()
    
    # Start web server and handle requests
    start_server(handler)

if __name__ == "__main__":
    main()