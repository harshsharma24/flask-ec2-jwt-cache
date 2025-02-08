#step 1 Use and official python image as the base
FROM python:3.9-slim

#step-2 Set working directory inside the container
WORKDIR /app

#step-3 Copy the current directory contents into the container
COPY . /app

# Step 4: Install the python deficiencies
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Expose the flask port
EXPOSE 5000

#Step 6 Define the the command to run the app
CMD ["python", "app.py"]