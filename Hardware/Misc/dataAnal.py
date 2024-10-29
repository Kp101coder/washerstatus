import ast

def parse_data(data_str):
    try:
        # First, attempt to use ast.literal_eval
        return ast.literal_eval(data_str)
    except (SyntaxError, ValueError) as e:
        # If that fails, try manually parsing the list as a fallback
        try:
            # Remove unwanted characters and split into float values
            cleaned_data = data_str.strip().strip('[]').split(',')
            return [float(item) for item in cleaned_data]
        except Exception as parse_error:
            print(f"Failed to parse line: {data_str}, Error: {parse_error}")
            return None

def analize(filepath: str):
    with open(filepath, "r") as f:
        data = f.read().splitlines()

    averageLin = [0.0, 0.0, 0.0]
    highestRot = [0.0, 0.0, 0.0]
    linCount = 0
    rotCount = 0

    for line in data:
        data_str = line[line.find(": ") + 2:]
        if "Linear" in line:
            linData = parse_data(data_str)
            if linData:
                for i in range(len(linData)):
                    averageLin[i] += abs(linData[i])
                linCount += 1
        elif "Rotational" in line:
            rotData = parse_data(data_str)
            if rotData:
                for i in range(len(rotData)):
                    highestRot[i] = max(rotData[i], highestRot[i])
                rotCount += 1

    # Avoid division by zero and calculate averages
    if linCount > 0:
        averageLin = [x / linCount for x in averageLin]
    if rotCount > 0:
        highestRot = [x / rotCount for x in highestRot]

    print(filepath)
    print(f"Linear Averages: {averageLin}")
    print(f"Rotational Highest: {highestRot}")
    print(f"Data points: {linCount}")

# Analyze the files
analize("washerOpen.txt")
print()
analize("washerClose.txt")
print()
analize("washerON.txt")
print()
analize("washerOFF.txt")