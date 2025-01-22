from config.settings import MAX_QUERY_SIZE
from utils.memory_profiler import MemoryProfiler
from lib.error_handler import ErrorHandler

class GraphQLClient:
    def __init__(self, endpoint, api_key):
        self.endpoint = endpoint
        self.api_key = api_key
        self.profiler = MemoryProfiler()
        self.error_handler = ErrorHandler()