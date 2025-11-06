import logging
import time
from fastapi import Request

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    filename='app.log', 
    filemode='a'         
)

sqlalchemy_logger = logging.getLogger('sqlalchemy.engine')
sqlalchemy_logger.setLevel(logging.ERROR)
sqlalchemy_logger.propagate = False

def setup_request_logging(app):
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        duration = (time.time() - start_time) * 1000
        logging.info(f"{request.method} {request.url.path} - Status: {response.status_code} - {duration:.2f}ms")
        return response
