
input_file = r'c:\Users\jason.m.chgv\Documents\CavalierOne\resources\extracted_excel.txt'
output_file = r'c:\Users\jason.m.chgv\Documents\CavalierOne\resources\fast_keys_final.md'

excluded_keywords = ["Travel", "Estimator", "Working"]

with open(input_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

output_lines = []
current_sheet = None
include_sheet = True

for line in lines:
    if line.strip().startswith("[Sheet:"):
        current_sheet = line.strip()
        # Check exclusion
        if any(keyword in current_sheet for keyword in excluded_keywords):
            include_sheet = False
        else:
            include_sheet = True
            output_lines.append(f"\n## {current_sheet}\n")
    
    if include_sheet and not line.strip().startswith("[Sheet:"):
        # Basic cleanup - maybe remove empty pipe rows if too many
        if line.strip() and not line.strip() == "|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |":
             output_lines.append(line)

with open(output_file, 'w', encoding='utf-8') as f:
    f.writelines(output_lines)

print(f"Filtered content written to {output_file} with {len(output_lines)} lines.")
