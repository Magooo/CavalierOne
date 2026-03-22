with open(r'c:\Users\jason.m.chgv\Documents\CavalierOne\resources\extracted_excel.txt', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f, 1):
        if "NSW.xlsx" in line:
            print(f"Found NSW at line {i}: {line.strip()}")
