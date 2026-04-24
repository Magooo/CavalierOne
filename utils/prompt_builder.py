from .data_loader import get_style_guide, get_company_info, load_master_prompt

def build_marketing_prompt(data):
    """
    Constructs the final prompt by combining:
    1. Master Prompt (Rules)
    2. Style Guide (Tone & Branding)
    3. Company Info (Static Details)
    4. User Inputs (Specific Session Data)
    """
    
    # Load Static Context
    master_prompt = load_master_prompt() # Note: We need to expose this in data_loader
    style_guide = get_style_guide()
    company_info = get_company_info()
    
    # Extract User Inputs
    media_type = data.get('media_type', 'Social Media Content')
    home_name = data.get('home_name', 'N/A')
    inclusions = data.get('inclusions', 'Standard Inclusions')
    land_details = data.get('land_details', 'N/A')
    target_audience = data.get('target_audience', 'Home Buyers')
    
    # Construct the Context Injection Block
    context_block = f"""
---
## CONTEXT INJECTION
**STYLE GUIDE:**
{style_guide}

**COMPANY INFORMATION:**
{company_info}
"""

    # Construct the User Input Block
    input_block = f"""
---
## USER SESSION INPUTS
**Marketing Media Type:** {media_type}
**Home Name:** {home_name}
**Target Audience:** {target_audience}

**Land / Estate Details:**
{land_details}

**Inclusions List:**
{inclusions}

**INSTRUCTION:**
Generate the {media_type} for the above property.
1. Apply the **System Rules** from the Master Prompt.
2. Apply the **Tone & Branding** from the Style Guide.
3. Use the **Company Details** provided.

**CRITICAL ANTI-HALLUCINATION RULES:**
- Do NOT invent facts. Use only the data provided above.
- Use exact names from Company Info (e.g. Jason McHugh).
- If a detail (e.g. price, address) is missing, omit it or use "contact us for details".
"""
    
    return master_prompt + context_block + input_block

def build_image_prompt(data):
    """
    Constructs a highly detailed DALL-E 3 prompt for architectural renderings.
    Enforces Brand Style Guide rules:
    - Fresh, modern, bright, well-lit
    - Front-on angle (strict)
    - Blue skies
    """
    
    # Extract specifics
    home_name = data.get('home_name', 'Custom Home')
    facade_desc = data.get('facade_description', 'Architectural Elevation')
    environment = data.get('environment', 'Manicured suburban garden')
    roof_geometry = data.get('roof_geometry', '') # Legacy
    structural_details = data.get('structural_details', '') # Primary forensic data
    
    # Sanitize Negatives & Enforce Terminolgy
    if structural_details and "no eaves" in structural_details.lower():
         structural_details += "\n(GARAGE DETAIL: FLUSH EAVE. ROOF ENDS AT EXTERNAL BRICK LINE WITH FASCIA/GUTTER)"
    
    # "Punchy" Protocol - Iteration 9 (Strict Materials)
    prompt = (
        f"ARCHITECTURAL BLUEPRINT MODE. STRICT MATERIAL ADHERENCE.\n"
        f"1. STRUCTURE: {structural_details}\n"
        f"2. ROOF OVERRIDE: {roof_geometry if roof_geometry else 'Follow Structure'}.\n"
        f"3. SUBJECT: Facade of '{home_name}'.\n"
        f"4. MATERIALS: {facade_desc}. DO NOT ADD RENDER unless listed.\n"
        f"5. ENVIRONMENT: {environment}.\n"
        f"6. STYLE: Photorealistic, 8k, Bright Day, Front-On Elevation. "
        f"NO CROPPING. SHOW FULL ROOF."
    )
    
    return prompt

def build_job_ad_prompt(data):
    """
    Constructs a structured prompt for generating Job Advertisements
    using the formal, 'Punchy' protocol inspired by the image generator.
    """
    # Extract specifics
    role_title = data.get('role_title', 'Job Opening')
    department = data.get('department', 'General')
    location = data.get('location', 'Shepparton, VIC')
    if not location:
        location = 'Shepparton, VIC'
        
    job_type = data.get('job_type', 'Full-Time')
    
    responsibilities = "\n- ".join(data.get('key_responsibilities', []))
    if responsibilities: responsibilities = "- " + responsibilities
    
    requirements = "\n- ".join(data.get('requirements', []))
    if requirements: requirements = "- " + requirements
        
    benefits = "\n- ".join(data.get('benefits', []))
    if benefits: benefits = "- " + benefits

    # User inputs
    salary = data.get('salary', '')
    perks = data.get('perks', '')
    extra = data.get('extra', '')
    
    platform = data.get('platform', 'LinkedIn, Facebook, and Instagram')

    prompt = (
        f"FORMAL AD COPY MODE. STRICT BRAND ADHERENCE.\\n"
        f"1. ROLE: {role_title} ({job_type})\\n"
        f"2. DEPARTMENT: {department} | LOCATION: {location}\\n"
        f"3. RESPONSIBILITIES:\\n{responsibilities}\\n"
        f"4. REQUIREMENTS:\\n{requirements}\\n"
        f"5. BENEFITS/PERKS:\\n{benefits}\\n"
    )
    if salary:
        prompt += f"-> REMUNERATION: {salary}\\n"
    if perks:
        prompt += f"-> EXTRA PERKS: {perks}\\n"
    if extra:
        prompt += f"-> EXTRA CONTEXT/REQUIREMENTS: {extra}\\n"
        
    prompt += (
        f"6. STYLE: Fresh, modern, professional. Clear, scannable structure. No overly hyped superlatives.\\n"
        f"7. PLATFORMS: {platform}. Generate suitable lengths for each.\\n"
        f"8. INSTRUCTION: Write the job advertisement using the strict structural style above. Keep it formal, highly legible, and aligned with Cavalier Homes Goulburn Valley branding. DO NOT include any internal debug messages, just write the final ad."
    )
    
    return prompt
