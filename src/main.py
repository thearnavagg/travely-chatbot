import os
from groq import Groq
import streamlit as st
import json
import re

# Streamlit page config
st.set_page_config(
    page_title="Travely",
    page_icon="✈️",
    layout="centered"
)

GROQ_API_KEY = st.secrets["groq"]["GROQ_API_KEY"]

# Save API key to env variable
os.environ["GROQ_API_KEY"] = GROQ_API_KEY

client = Groq()

# Enabling chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Streamlit page title
st.title("✈️ Travely")

# Display chat history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input field for user's message:
user_prompt = st.chat_input("Ask Travely...")

if user_prompt:
    st.chat_message("user").markdown(user_prompt)
    st.session_state.chat_history.append({"role": "user", "content": user_prompt})

    # Check if the user provided a place or number of days
    place = None
    days = None

    # Simple parsing logic to identify place and days from user input (this can be improved)
    if "days" in user_prompt.lower():
        days = user_prompt.split("days")[0].strip()  # Extract number of days
        place = user_prompt.split("days")[-1].strip()  # Extract place after 'days'

    # Handle greetings like "Hi", "Hey", "Hello"
    if user_prompt.lower() in ["hi", "hey", "hello"]:
        messages = [
            {"role": "system", "content": "👋 Hey there, travel adventurer! 🌍 Ready to embark on an unforgettable journey? 😎\n\nI can't wait to help you plan your dream trip, but I need a couple of details from you first:\n\n- 🏖️ **Where** are you thinking of heading for your next adventure?\n- 🕒 **How many days** are you planning to explore this amazing place?\n\nOnce you tell me that, I'll whip up the perfect itinerary just for you! 🎒✨ Let’s make your travel dreams come true! 🌟✈️"},
            *st.session_state.chat_history
        ]
    # Check if both place and days are not provided
    elif not place and not days:
        messages = [
            {"role": "system", "content": "❗ Please provide both the place you'd like to visit and the number of days for your stay."},
            *st.session_state.chat_history
        ]
    elif not place:
        messages = [
            {"role": "system", "content": "👋 Welcome to your personalized travel planner! Please tell me the place you would like to visit."},
            *st.session_state.chat_history
        ]
    elif not days:
        messages = [
            {"role": "system", "content": f"🌍 Great choice! How many days do you plan to stay in {place}?"},
            *st.session_state.chat_history
        ]
    else:
        messages = [
            {"role": "system", "content": f"📅 Here is your itinerary for {place} for {days} days:"},
            *st.session_state.chat_history
        ]

        # Example itinerary with emoji
        itinerary_example = f"""
        **Your Travel Itinerary for {place}** ✈️🏙️

        ---

        ### 🌍 Destination: {place}
        ### 🕒 Duration: {days} Days

        ---

        #### Day {days}: Arrival and Exploration 🎒
        - **Check-in** at your hotel and settle in.
        - **Morning**: Take a stroll around the city center to get familiar with the surroundings.
        - **Lunch**: Enjoy a meal at a local restaurant, famous for its traditional dishes.
        - **Afternoon**: Visit the **{place} Museum** and explore local landmarks.
        - **Dinner**: Try the signature local dish at **[Popular Restaurant]**.
        - **Evening**: Enjoy a relaxing walk along the waterfront and experience the night vibe.

        ---

        #### Additional Suggestions:
        - **Shopping**: Don’t forget to explore the local markets for souvenirs.
        - **Cultural Experience**: Attend a live performance of traditional music or theater.
        - **Explore**: Rent a bike and take a scenic ride around the outskirts of the city.

        ---

        We hope you have an amazing time exploring {place}! 🌟 Let us know if you need any more recommendations or adjustments to your itinerary.
        """

        # Provide instructions and the example to the LLM
        messages.append({"role": "system", "content": "Please generate a response with engaging that match the theme of travel."})
        messages.append({"role": "system", "content": itinerary_example})

    # Send user message to LLM
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages
    )

    assistant_response = response.choices[0].message.content

    def add_emojis(text, max_emojis_per_sentence=2, max_total_emojis=25):
            emoji_map = {
                # General travel and places
                "city": "🏙️",
                "capital": "🏛️",
                "beach": "🏖️",
                "mountain": "🏔️",
                "hills": "⛰️",
                "park": "🌳",
                "garden": "🌸",
                "museum": "🏛️",
                "palace": "🏰",
                "monument": "🗿",
                "landmark": "📍",
                "market": "🛍️",
                "restaurant": "🍽️",
                "cafe": "☕",
                "hotel": "🏨",
                "resort": "🏝️",
                "spa": "💆‍♀️",
                "airport": "✈️",
                "train station": "🚉",
                "bus stop": "🚌",

                # Travel actions and activities
                "travel": "✈️",
                "explore": "🌍",
                "visit": "🗺️",
                "tour": "🚌",
                "hike": "🥾",
                "bike": "🚴‍♀️",
                "walk": "🚶‍♂️",
                "drive": "🚗",
                "boat ride": "⛵",
                "relax": "🌸",
                "shopping": "🛍️",
                "sightseeing": "👀",
                "adventure": "🧗‍♂️",
                "wildlife": "🦁",
                "cultural": "🎭",
                "performance": "🎶",
                "food": "🍲",
                "drink": "🍹",
                "nightlife": "🌙",
                "festival": "🎉",
                "view": "🌅",
                "sunset": "🌇",
                "sunrise": "🌄",

                # Accommodation
                "luxury hotel": "🏨✨",
                "hostel": "🏨",
                "villa": "🏡",
                "apartment": "🏢",

                # Transportation
                "flight": "🛫",
                "bus": "🚌",
                "train": "🚂",
                "car": "🚗",
                "bicycle": "🚴",
                "ferry": "⛴️",
                "taxi": "🚕",
                "subway": "🚇",
                "tram": "🚋",

                # Nature and outdoors
                "forest": "🌲",
                "river": "🌊",
                "waterfall": "💧",
                "lake": "🏞️",
                "desert": "🏜️",
                "volcano": "🌋",
                "island": "🏝️",
                "wildlife sanctuary": "🐅",
                "national park": "🏞️",

                # Miscellaneous
                "itinerary": "📅",
                "adventure": "🧗",
                "history": "📜",
                "culture": "🕌",
            }

            def replace_emoji_in_sentence(sentence, max_emojis):
                replaced_emoji_count = 0
                for word, emoji in emoji_map.items():
                    if replaced_emoji_count >= max_emojis:
                        break
                    if re.search(rf'\b{word}\b', sentence, re.IGNORECASE):
                        sentence = re.sub(rf'\b{word}\b', f'{word} {emoji}', sentence, flags=re.IGNORECASE, count=1)
                        replaced_emoji_count += 1
                return sentence, replaced_emoji_count

            sentences = re.split(r'(?<=[.!?]) +', text)  # Split text into sentences
            total_emojis = 0

            for i, sentence in enumerate(sentences):
                if total_emojis >= max_total_emojis:
                    break
                updated_sentence, emoji_count = replace_emoji_in_sentence(sentence, max_emojis_per_sentence)
                sentences[i] = updated_sentence
                total_emojis += emoji_count

            return ' '.join(sentences)

    assistant_response = add_emojis(assistant_response)

    st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})

        # Display assistant response
    with st.chat_message("assistant"):
        st.markdown(assistant_response)
