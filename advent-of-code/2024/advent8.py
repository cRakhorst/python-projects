def parse_input(file_path):
    with open(file_path) as file:
        return {
            x + y * 1j: character
            for x, line in enumerate(file)
            for y, character in enumerate(line.strip())
        }

def find_unique_paths(grid_data, step_ranges):
    path_counts = []

    for step_range in step_ranges:
        unique_positions = set()

        for start in grid_data:
            for end in grid_data:
                # Overslaan als de start- en eindposities gelijk zijn of tekens niet overeenkomen
                if start == end or grid_data[start] != grid_data[end] or grid_data[start] == ".":
                    continue
                
                # Genereer alle tussenliggende posities voor een gegeven stapgrootte
                for step in step_range:
                    position = start + step * (end - start)
                    if position in grid_data:
                        unique_positions.add(position)

        # Voeg het aantal unieke posities toe aan de resultaten
        path_counts.append(len(unique_positions))

    return path_counts

def main():

    input_file = "day8.txt"
    grid_data = parse_input(input_file)
    
    # Definieer de stapreeksen: één met alleen stap 2, en een andere tot stap 50
    step_ranges = [[2], range(51)]
    
    # Bereken het aantal unieke paden
    results = find_unique_paths(grid_data, step_ranges)
    
    # Print de resultaten
    print(*results)

if __name__ == "__main__":
    main()
