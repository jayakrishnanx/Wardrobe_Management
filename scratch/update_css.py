import sys

file_path = r'c:\Users\jayak\OneDrive\Desktop\Wardrobe_Management\static\css\main.css'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_css = """/* Accessory Recommendations in Outfits - Compact & Premium */
.accessory-recommendations {
    background: #fafafa;
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: var(--space-ms) var(--space-md);
    margin-top: -0.5rem;
    box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);
}

.accessory-grid {
    display: flex;
    flex-wrap: wrap;
    gap: var(--space-ms);
    justify-content: flex-start;
}

.accessory-item-card {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-sm);
    padding: var(--space-xs) var(--space-sm);
    display: flex;
    align-items: center;
    gap: var(--space-ms);
    min-width: 140px;
    max-width: fit-content;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.accessory-item-card:hover {
    transform: translateY(-2px);
    border-color: var(--primary-color);
    box-shadow: var(--shadow-sm);
}

.accessory-img {
    width: 38px;
    height: 38px;
    object-fit: cover;
    border-radius: var(--radius-sm);
    border: 1px solid var(--border-color);
    flex-shrink: 0;
}

.accessory-img-placeholder {
    width: 38px;
    height: 38px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
    background: var(--bg-body);
    border-radius: var(--radius-sm);
    flex-shrink: 0;
}

.accessory-info {
    display: flex;
    flex-direction: column;
    text-align: left;
    gap: 0;
    line-height: 1.2;
}

.acc-name {
    font-size: 0.78rem;
    font-weight: 600;
    color: var(--text-main);
}

.acc-supplier {
    font-size: 0.65rem;
    color: var(--text-muted);
}

.acc-price {
    font-size: 0.72rem;
    font-weight: 700;
    color: var(--primary-color);
}
"""

# The accessory block starts after the chat-message block.
# We'll search for the comment line.
start_idx = -1
for i, line in enumerate(lines):
    if "/* Accessory Recommendations in Outfits */" in line:
        start_idx = i
        break

if start_idx != -1:
    filename = file_path
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines[:start_idx])
        f.write(new_css)
    print(f"Successfully updated CSS in {file_path}")
else:
    print("Could not find the accessory CSS block to replace.")
