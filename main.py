import time
import requests
import json
import random

serverURL = "http://localhost:8080/completion"
task_list = "tasks.jsonl"

def readEnergy(): # reads total energy consumption from arbitrary starting point in microjoules
    with open("/sys/class/powercap/intel-rapl:0/energy_uj", "r") as file:
        energy_uj = file.read()
        return(energy_uj)

def counterMax(): # maximum counter before wrap around in microjoules
    with open("/sys/class/powercap/intel-rapl:0/max_energy_range_uj", "r") as file:
        max_energy = file.read()
        return(max_energy)

def energyUsed(start, end, max_energy): # calculates delta energy, accounting for wrap around
    if (start>end): # if t1>t2, it means the energy counter has wrapped around
        return (max_energy - int(start) + int(end))
    return (int(end) - int(start))

def prompt():
    with open(task_list, "r") as file:
        lines = [json.loads(line) for line in file]
        random_task = random.choice(lines)
        if random_task["context"] != "":
            return "Passage: " + random_task["context"] + "\nQuestion: " + random_task["question"] + "\nAnswer:"
        else:
            return "Question: " + random_task["question"] + "\nAnswer:"

start = int(readEnergy())
time.sleep(10)
end = int(readEnergy())
delta_e = energyUsed(start, end, counterMax())
watts = delta_e / 10000000
print(f"Power consumption: {watts} watts")
print(f"Energy consumption: {delta_e} microjoules")

prompt = prompt()
maxTokens = 512
response = requests.post(serverURL, json={
    "prompt": "Question: " + prompt,
    "n_predict": maxTokens,
    "temperature": 0,
    "cache_prompt": False,
    "stream": False

})
data = response.json()
print(f"prompt: {data.get('prompt')}") # prompt sent to the model
print(f"tokens: {data.get('tokens_predicted')}") # amount of tokens generated for the response
print(f"content: {data.get('content')}") # solution and reasoning for the prompt
print(f"prompt_ms: {data.get('timings').get('prompt_ms')}") # time taken to process the prompt (prefill)
print(f"predicted_ms: {data.get('timings').get('predicted_ms')}") # time taken to generate the response (decode)