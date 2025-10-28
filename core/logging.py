import logging

# Configure root logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

# Reduce SQLAlchemy engine logs
# sqlalchemy_logger = logging.getLogger('sqlalchemy.engine')
# sqlalchemy_logger.setLevel(logging.WARNING)
# sqlalchemy_logger.propagate = False
sqlalchemy_logger = logging.getLogger('sqlalchemy.engine')
sqlalchemy_logger.setLevel(logging.ERROR)  # Only show errors, not info or warnings
sqlalchemy_logger.propagate = False

def setup_request_logging(app):
    import time
    from fastapi import Request

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        duration = (time.time() - start_time) * 1000
        logging.info(f"{request.method} {request.url.path} - Status: {response.status_code} - {duration:.2f}ms")
        return response
