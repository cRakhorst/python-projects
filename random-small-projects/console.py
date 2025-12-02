import os

BASE_DIR = os.path.dirname(__file__)
file_path = os.path.join(BASE_DIR, "txt", "example.txt")

def run(file_path):
    companies = []
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if "->" in line:
                company = line.split("->", 1)[1].strip()
                company = company.split("'", 1)[0].strip()
                companies.append(company)
            
        counts = {item: companies.count(item) for item in set(companies)}
        sorted_counts = sorted(counts.items(), key = lambda x: x[1], reverse=True)
    return sorted_counts, len(companies)
        
if __name__ == "__main__":
    result, total = run(file_path)

    max_len = max(len(company) for company, _ in result)
    for company, count in result:
        percentage = round((count / total) * 100, 2)
        print(f"{company.ljust(max_len)} : {count}      {percentage}%")

    print("-" * (max_len +6))
    print(f"{'total'.ljust(max_len)} : {total}")