import requests

def stream_fibonacci_sequence(n):
    response = requests.post('http://localhost:8000/start-task/', json={'n': n}, stream=True, timeout=10)

  
    for line in response.iter_lines():
        if line:
            decoded_line = line.decode('utf-8')
            print(decoded_line)
    

if __name__ == "__main__":
    n = 21# You can change this number as needed
    stream_fibonacci_sequence(n)

