from datetime import datetime

# Get the current date
current_date = datetime.now()

# Get the current time
current_time = datetime.now().time()

print("Current Date:", type(str(current_date)))
print("Current Time:", type(current_time))
