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
    Constructs a prompt for generating Job Advertisements.
    Focus: Sell the ROLE, the TEAM, and the CAREER — NOT the houses.
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

    prompt = f"""You are a recruitment copywriter for Cavalier Homes Goulburn Valley — a respected residential home builder in regional Victoria.

CRITICAL TONE INSTRUCTION:
You are writing a JOB ADVERTISEMENT, NOT a property listing. Your job is to SELL THE ROLE AND THE TEAM to potential candidates.
- Write like a great recruiter, NOT like a real estate agent.
- Focus on: the people, the team culture, career growth, day-to-day impact, and why someone would love coming to work here.
- DO NOT talk about "quality craftsmanship", "trusted builder", "supplier relationships", or "integrity in every project" — that's house-selling language.
- Instead talk about: supportive team, career development, meaningful work, great leadership, flexible culture, regional lifestyle benefits.
- Be warm, energetic, and genuine. Make the reader think "I want to work there!"
- Use punchy, scannable formatting with clear headings. Keep paragraphs short.

ROLE DETAILS:
- Title: {role_title}
- Type: {job_type}
- Department: {department}
- Location: {location}

KEY RESPONSIBILITIES:
{responsibilities if responsibilities else '(Use common responsibilities for this type of role)'}

REQUIREMENTS:
{requirements if requirements else '(Use reasonable requirements for this type of role)'}

BENEFITS & PERKS:
{benefits if benefits else '(Emphasise team culture, regional lifestyle, career growth)'}
"""
    if salary:
        prompt += f"\nSALARY/REMUNERATION: {salary}"
    if perks:
        prompt += f"\nADDITIONAL PERKS: {perks}"
    if extra:
        prompt += f"\nEXTRA CONTEXT: {extra}"
        
    prompt += f"""

OUTPUT FORMAT:
Write in Markdown. Use a professional, polished structure.

IMPORTANT — MULTIPLE ROLES:
If the role details or extra context mention more than one position (e.g. "Accounts Payable Administrator" AND "Accounts & Bookkeeping Administrator"), you MUST treat each as a SEPARATE, CLEARLY DEFINED role within the ad. For each role, provide:
- A clear role title as a heading (## or ###)
- A brief description of what the role involves (1-2 sentences)
- **Key Responsibilities** — bullet points specific to THAT role
- **What You'll Bring** — requirements specific to THAT role (or shared if genuinely the same)

Do NOT merge the roles into vague combined sections. The reader must be able to clearly see exactly what each position entails.

OVERALL STRUCTURE:
1. A compelling headline (sell the opportunity, not just the job title)
2. Brief intro (2-3 sentences — why these roles are exciting, who the team is)
3. Individual role sections (as described above)
4. **Why You'll Love It Here** — perks, culture, lifestyle (shared across roles)
5. **How to Apply** — clear call to action, email admin@cavalierhomesgv.com.au

STYLE RULES:
- Be specific and concrete, not vague
- Use professional but warm language
- Keep it scannable — short paragraphs, clear headings, bullet points
- Do NOT use generic filler phrases like "dynamic environment" or "passionate team player"

TARGET PLATFORMS: {platform}
Keep it concise enough for social media but detailed enough for LinkedIn. One version that works across all platforms.
Do NOT include any meta-commentary. Just write the final ad copy in Markdown."""
    
    return prompt

