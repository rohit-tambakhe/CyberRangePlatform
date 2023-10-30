# Use an official Python runtime as a parent image
FROM python:3.8

# Set the working directory to /app
WORKDIR /LDAP

# Copy the LDAP integration code and dependencies
COPY ldap_integration.py .
COPY ldap_util.py .
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Expose the port if your application listens on a specific port (modify if needed)
EXPOSE 80

# Define environment variables if needed
# ENV VARIABLE_NAME=value

# Run the LDAP integration application
CMD ["python", "ldap_integration.py"]
