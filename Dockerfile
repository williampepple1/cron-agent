FROM python:3.10

WORKDIR /code

# Set up a new user to avoid running as root (Hugging Face Spaces requirement)
RUN useradd -m -u 1000 user

# Copy requirements and install
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy application files
COPY . /code

# Change ownership to the new user
RUN chown -R user:user /code
USER user

# Set environment variables for hugging face
ENV HOME=/home/user \
	PATH=/home/user/.local/bin:$PATH

WORKDIR /code

# Expose port
EXPOSE 7860

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
