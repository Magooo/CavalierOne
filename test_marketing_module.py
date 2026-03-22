from marketing import SocialMediaPost

def test_social_media_post():
    print("Testing SocialMediaPost...")
    
    # 1. Create a dummy post
    post = SocialMediaPost(
        platform="Instagram",
        home_name="The Hampton 256",
        target_audience="Young Families",
        land_details="Lot 45, Kialla Lakes - Lake Views",
        inclusions="Ducted Heating, Evaporative Cooling, Stone Benchtops"
    )
    
    print(f"Created Post Object: {post}")
    
    # 2. Generate the draft (prompt)
    prompt = post.generate_draft()
    
    # 3. Validation
    if "The Hampton 256" in prompt and "Instagram" in prompt:
        print("\n✅ SUCCESS: Prompt generated correctly containing key details.")
        print("-" * 50)
        print("Preview of generated prompt (first 500 chars):")
        print(prompt[:500] + "...")
        print("-" * 50)
    else:
        print("\n❌ FAILURE: Prompt missing key details.")
        print(prompt)

if __name__ == "__main__":
    test_social_media_post()
