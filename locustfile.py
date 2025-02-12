# locustfile.py
from locust import HttpUser, task, between
import random
import string

def generate_random_string(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

class WebsiteUser(HttpUser):
    wait_time = between(1, 3)  # Random wait between tasks
    
    def on_start(self):
        # Initialize any session data if needed
        pass
    
    @task(3)  # Weight of 3 - more frequent
    def add_item(self):
        # Add a new item
        name = f"Load Test Item {generate_random_string(8)}"
        description = f"Load test description {generate_random_string(20)}"
        
        self.client.post("/add", data={
            "name": name,
            "description": description
        })
    
    @task(5)  # Weight of 5 - most frequent
    def view_items(self):
        # View the main page
        self.client.get("/")
    
    @task(1)  # Weight of 1 - less frequent
    def delete_item(self):
        # First get the page to parse for items
        response = self.client.get("/")
        
        # This is a simple way to extract an ID from the delete URL
        # In a real scenario, you might want to use BeautifulSoup for better parsing
        if "delete" in response.text:
            try:
                # Find a delete URL in the response
                start = response.text.find('/delete/')
                if start != -1:
                    end = response.text.find('"', start)
                    delete_url = response.text[start:end]
                    self.client.get(delete_url)
            except Exception:
                pass
    
    @task(1)  # Weight of 1 - less frequent
    def add_invalid_item(self):
        # Try to add an item with invalid data
        name = generate_random_string(300)  # Too long for VARCHAR(255)
        description = "Test description"
        
        self.client.post("/add", data={
            "name": name,
            "description": description
        })