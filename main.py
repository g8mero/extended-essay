import time
import requests
import json
import random
import csv

serverURL = "http://localhost:8080/completion"
task_list = "tasks.jsonl"
maxTokens = 512
model = "OLMo" # switch to OLMoe for mixture-of-experts model

stopSequences = {   # Stop sequences written by Claude, used to determine when the model has finished generating text. These stop sequences were also prompted to follow the ones used in OLMES, the original OLMoe paper. Gu et al. (2024)
    "math": ["Question:", "</s>", "<|im_end|>", "<|endoftext|>"],
    "knowledge": ["\n\n", "Question:", "</s>", "<|im_end|>", "<|endoftext|>"],
    "comprehension": ["Passage:", "Question:", "</s>", "<|im_end|>", "<|endoftext|>"],
}


def readEnergy(): # reads total energy consumption from arbitrary starting point in microjoules
    with open("/sys/class/powercap/intel-rapl:0/energy_uj", "r") as file:
        energy_uj = file.read()
        return(energy_uj)

def counterMax(): # maximum counter before wrap around in microjoules
    with open("/sys/class/powercap/intel-rapl:0/max_energy_range_uj", "r") as file:
        max_energy = file.read()
        return(int(max_energy))


def energyUsed(start, end, max_energy): # calculates delta energy, accounting for wrap around
    if (start>end): # if t1>t2, it means the energy counter has wrapped around
        return (max_energy - int(start) + int(end))
    return (int(end) - int(start))


# formatts prompt for the model based on required context.
def prompt(task):
    if task["context"] != "":
        return "Passage: " + task["context"] + "\nQuestion: " + task["question"] + "\nAnswer:"
    else:
        return "Question: " + task["question"] + "\nAnswer:"


# runs a single task and returns run specific details in an array.
def runTask(task, maxEnergy):        
    request = {
        "prompt": prompt(task),
        "n_predict": maxTokens,
        "temperature": 0,
        "cache_prompt": False,
        "stream": False,
        "stop": stopSequences[task["domain"]]
    }

    start = int(readEnergy())
    t1 =time.perf_counter() # starts timer with high precision
    response = requests.post(serverURL, json=request)
    data = response.json()
    t2 = time.perf_counter() # ends timer with high precision
    end = int(readEnergy())

    task_id = task["id"]
    domain = task["domain"]
    benchmark = task["benchmark"]
    energy_package_uj = energyUsed(start, end, maxEnergy)
    wall_time_s = t2 - t1
    prompt_ms = data.get("timings").get("prompt_ms")
    predicted_ms = data.get("timings").get("predicted_ms")
    tokens_prompt = data.get("tokens_evaluated")
    tokens_predicted = data.get("tokens_predicted")
    stop_type = data.get("stop_type")
    truncated = tokens_predicted >= maxTokens
    content = data.get("content")

    measurements = [task_id, domain, benchmark, energy_package_uj, wall_time_s, prompt_ms, predicted_ms, tokens_prompt, tokens_predicted, stop_type, truncated, content]
    return measurements

def main():
    maxEnergy = int(counterMax())
    tasks = []
    # loads tasks into array from tasks.jsonl line by line
    with open("tasks.jsonl", "r") as file:
        for line in file:
            tasks.append(json.loads(line))
    print(f"Loaded {len(tasks)} tasks from task.jsonl")

    totalRuns = 5 * len(tasks)
    i = 0 #counts the number of tasks completed


    # writes results to CSV file
    with open(f"results-{model}.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["model", "repeat", "run_index", "task_id", "domain", "benchmark","energy_package_uj", "wall_time_s", "prompt_ms", "predicted_ms","tokens_prompt", "tokens_predicted", "stop_type", "truncated", "content"])
        for repeat in range(5):
            order = tasks.copy()
            random.shuffle(order)
            for task in order:
                time.sleep(2)
                measurements = runTask(task, counterMax())
                i += 1
                writer.writerow([model, repeat, i] + measurements) # appends run specific information to the CSV file
                file.flush()
                print(f"[{i}/{totalRuns}] {measurements[0]} {measurements[3]/1000000} J")
main()