import multiprocessing

# Set the number of gunicorn workers to the number of CPU
workers = multiprocessing.cpu_count()
