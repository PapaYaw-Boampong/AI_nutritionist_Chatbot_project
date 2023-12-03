import streamlit as st
import os
import openai
from openai import OpenAI

# Now you can access your variables
openai_api_key = os.getenv("OPENAI_API_KEY")




client = OpenAI(
    # This is the default and can be omitted
    # api_key=os.environ.get("OPENAI_API_KEY"),
    api_key = st.secrets["openai"]["api_key"]
)



# Function to get completion from OpenAI Chat API
def get_completion_from_messages(messages,
                                 model="gpt-3.5-turbo",
                                 temperature=0,
                                 max_tokens=500):
    response = client.chat.completions.create(
        messages=messages,
        model=model,
        max_tokens=max_tokens,
        temperature=0,  # this is the degree of randomness of the model's output
    )
    return response.choices[0].message.content


# Function to categorize user input and extract relevant information
def get_input_category(user_input):
    delimiter = "####"
    system_message = f"""
        You will receive user inquiries related to the AI nutritionist service. \
        Each user query will be delimited with {delimiter} characters.

        Classify each query into a primary category and a secondary category.
        If the query is off-topic, provide the classification as Off-Topic.
        Further Extract keywords like,food titles, recipes, and\
        ingredients if provided and none in no keyword found.store as keyword.
        Also return keyword like,food titles, recipes, and\ 

        Provide your output in JSON format with the keys: primary,secondary and keyword\

        Primary categories: Personalized Meal Planning, Nutritional Information, \
        Dietary Advice, Health Goals, General Inquiry, or Off-Topic.

        Meal Planning secondary categories:
        Generate meal plan
        Modify existing plan
        Preferences update
        Meal substitution

        Nutritional Information secondary categories:
        Specific food nutrition
        General nutrition facts
        Caloric content
        Ingredient analysis

        Dietary Advice secondary categories:
        Healthy eating tips
        Dietary restrictions
        Balanced diet suggestions
        Nutritional guidance

        Health Goals secondary categories:
        Weight management
        Fitness advice
        Wellness goals
        Health improvement strategies

        General Inquiry secondary categories:
        Application features
        User feedback
        Technical support
        Speak to a human

        Off-Topic categories:
        Not related to nutritionist service
        Unintelligible input
        Irrelevant content
        Non-queries
    """

    messages = [
        {'role': 'system', 'content': system_message},
        {'role': 'user', 'content': f"{delimiter}{user_input}{delimiter}"},
    ]

    response = get_completion_from_messages(messages)
    return response


# Function to process user input and generate responses



def process_user_message(user_input, all_messages, debug=True):
    delimiter = "```"

    # Get categorized information
    product_information = get_input_category(user_input).replace("\n", "")

    system_message = f"""
        You are an AI-powered nutritionist assistant. \
        Interact with users in a friendly and informative manner, providing personalized nutritional advice. \
        Ask questions to understand users' dietary preferences, health goals, and any specific restrictions. \
        Offer tailored meal plans and share educational insights about nutrition. \
        Ensure the conversation is engaging and encourage users to ask follow-up questions.
    """

    messages = [
        {'role': 'system', 'content': system_message},
        {'role': 'user', 'content': f"{delimiter}{user_input}{delimiter}"},
        {'role': 'assistant', 'content': f"Relevant product information:\n{product_information}"}
    ]

    final_response = get_completion_from_messages(all_messages + messages)

    # Update AI memory
    all_messages = all_messages + messages[1:]

    # Model self-evaluation
    user_message = f"""
        Customer message: {delimiter}{user_input}{delimiter} ?
        Agent response: {delimiter}{final_response}{delimiter}

        Does the response sufficiently answer the question?
    """

    messages = [
        {'role': 'system', 'content': system_message},
        {'role': 'user', 'content': user_message}
    ]

    evaluation_response = get_completion_from_messages(messages)

    if "Y" in evaluation_response:
        return final_response, all_messages
    else:
        neg_str = "I'm unable to provide the information you're looking for.\n My function only extends to nutrition"
        return neg_str, all_messages


# Streamlit App
def main():
    st.title("AI Nutritionist Chatbot")

    # Initialize variables
    all_messages = []
    user_input = ""

    # Input box for user
    user_input = st.text_input("You:", user_input)

    # Button to submit user input
    if st.button("Ask"):
        # Process user input
        response, all_messages = process_user_message(user_input, all_messages)

        # Display chat history
        st.text_area("Chat History", value="\n".join([f"{msg['role']}: {msg['content']}" for msg in all_messages]))

        # Display chatbot response
        st.text_area("AI Nutritionist:", value=response, height=len(response.split("\n")) * 20)  # Adjust height dynamically

# Run the Streamlit app
if __name__ == "__main__":
    main()
