def analyse_campaign(user_input, llm):
    prompt = f"""
    You are a campaign analyst. Analyze this campaign input and extract the key issues:
    {user_input}
    Provide suggestions for improving performance.
    """
    return llm.invoke(prompt).content