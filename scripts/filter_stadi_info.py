from pathlib import Path

file_name = "datasets/selected/satdi_info_complete.csv"
file_in_path = Path(__file__).parent / file_name

with open(file_in_path, "r") as in_file:
    for line in in_file.readlines():
        data = line.replace("\n", "").split(";")

        if(data[0] == "repository"):
            continue

        state = data[4]

        out_file_name = "datasets/selected/satdi_info_summarized_" + state + ".csv"
        file_out_path = Path(__file__).parent / out_file_name
        #duration, size, participants, comments
        with open(file_out_path, "a") as out_file:
            out_file.write(data[0] + ";" + str(data[-1]) + ";" + str(data[-2]) + ";" + str(data[-3]) + ";" + str(data[-5]) + "\n")