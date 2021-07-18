color_data = {}

with open("info/colors.csv", "r") as file:
    for line in file:
        color_data[line.split(",")[0]] = line.split(",")[1].strip()

frame_background = color_data["frame_background"]
background = color_data["background"]
