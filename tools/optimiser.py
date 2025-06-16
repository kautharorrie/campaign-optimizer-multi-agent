def suggest_improvements(user_input, llm):
    prompt = f"""
    You are a campaign optimizer. Based on this input, suggest advanced tactics to increase ROI and engagement:
    {user_input}
    Make sure suggestions are actionable.
    """
    return llm.invoke(prompt).content