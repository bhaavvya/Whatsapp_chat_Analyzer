import streamlit as st 
import preprocessor, add_on
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import re  # For regular expressions to search for bad words

# --------------- NAVBAR ---------------
st.sidebar.header("CScan🔍")
st.sidebar.title("Navigation")
nav_option = st.sidebar.radio("Go to", ['About', 'Narcotics & CBI','Chat Analysis'])

# --------------- FILE UPLOADER ---------------
st.sidebar.title("Upload Chat File")
uploadfile = st.sidebar.file_uploader("Choose a WhatsApp Chat File")

if uploadfile is not None:
    bytes_data = uploadfile.getvalue()
    data = bytes_data.decode('utf-8')
    df = preprocessor.preprocess(data)
    st.write("✅ **Chat file successfully uploaded!**")
else:
    df = pd.DataFrame()  # If no file is uploaded, create an empty DataFrame

# --------------- ABOUT SECTION ---------------
if nav_option == 'About':
    st.title("About CScan🔍")
    st.write("""
    Welcome to the **CScan**. This tool allows you to analyze WhatsApp chats 
    for various metrics like total messages, most active users,word cloud, activity maps and many more.
    
    In addition, we have a **Narcotics & CBI Section** where the tool can search for 
    suspicious words related to **narcotics, drugs, cybercrime, and threats**. The system 
    also identifies the potential **culprit** who uses these sensitive words the most.
    
    **Features of this tool:**
    - View WhatsApp chat statistics
    - Detect messages related to narcotics, drugs, cybercrime, and threats
    - View flagged messages after clicking on the sensitive information button to prevent flashing harsh words to the users.
    - Identify the potential **culprit** in the chat
    """)

# --------------- CHAT ANALYSIS SECTION ---------------
elif nav_option == 'Chat Analysis':
    st.title("Chat Analysis")

    if not df.empty:
        st.dataframe(df)

         # --- SEARCH BOX (TOP CENTER) ---
        st.markdown("<h3 style='text-align: center;'>Search Messages</h3>", unsafe_allow_html=True)
        search_query = st.text_input("Enter a word to search", "", key="search_query")

        if search_query:
            search_query = search_query.lower()
            # Filter messages where the search query is found (case-insensitive)
            search_results = df[df['message'].str.contains(search_query, case=False, na=False)]

            if not search_results.empty:
                st.success(f"🔍 **Found {len(search_results)} messages containing '{search_query}'**")
                st.dataframe(search_results[['user', 'message']])
            else:
                st.warning(f"No messages found containing '{search_query}'")


        # --------------- LOAD BAD WORDS FROM FILE ---------------
        def load_bad_words(file_path='bad_words.txt'):
            """Load bad words from a file and return a list of words."""
            try:
                with open(file_path, 'r') as file:
                    bad_words = [line.strip().lower() for line in file if line.strip()]
                    st.write(f"🔍 **Loaded {len(bad_words)} bad words from `{file_path}` for analysis.**")
                return bad_words
            except FileNotFoundError:
                st.error(f"❌ `{file_path}` not found! Please make sure the file is in the same directory as this script.")
                return []

        # Load bad words from the bad_words.txt file
        bad_words_list = load_bad_words()
        def detect_bad_words(messages, bad_words):
            """Detect and return a DataFrame with flagged messages and the bad words found."""
            if not bad_words:  # If no bad words are loaded, return an empty DataFrame
                return pd.DataFrame(columns=['user', 'message', 'bad_word'])

            pattern = r'\b(' + '|'.join(re.escape(word) for word in bad_words) + r')\b'
            flagged_messages = []

            for i, row in messages.iterrows():
                match = re.search(pattern, row['message'], re.IGNORECASE)
                if match:  # If a bad word is found
                    flagged_messages.append({
                        'user': row['user'],
                        'message': row['message'],
                        'bad_word': match.group()  # The specific bad word that matched
                    })

            return pd.DataFrame(flagged_messages)

        flagged_df = detect_bad_words(df, bad_words_list)

        if not flagged_df.empty:
            st.write(f"🚩 **Total flagged messages: {len(flagged_df)}**")
            st.warning("The following table contains sensitive information. Click to view it.")
            with st.expander("View Sensitive Information"):
                st.dataframe(flagged_df[['user', 'message', 'bad_word']])
        else:
            st.write("✅ **No sensitive information detected in the chat.**")

        user_lst = df['user'].unique().tolist()
        user_lst.remove('group notification')
        user_lst.sort()
        user_lst.insert(0, "Overall")
        user_selects = st.sidebar.selectbox("Show Analysis with respect to ", user_lst)

        if st.sidebar.button("Show Analysis"):
            num_msg, words, num_media, number_links = add_on.fetch_stats(user_selects, df)
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.header("Total Messages")
                st.title(num_msg)
            with col2:
                st.header("Total Words")
                st.title(words)
            with col3:
                st.header("Media Shared")
                st.title(num_media)
            with col4:
                st.header("Links Shared")
                st.title(number_links)

            # Monthly timeline
            st.title("Monthly Timeline")
            timeline = add_on.monthly_timeline(user_selects, df)
            fig, ax = plt.subplots()
            ax.plot(timeline['time'], timeline['message'], color='green')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

            # Daily timeline
            st.title("Daily Timeline")
            daily_timeline = add_on.daily_timeline(user_selects, df)
            fig, ax = plt.subplots()
            ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='black')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

            # Activity map
            st.title('Activity Map')
            col1, col2 = st.columns(2)
            
            with col1:
                st.header("Most busy day")
                busy_day = add_on.week_activity_map(user_selects, df)
                fig, ax = plt.subplots()
                ax.bar(busy_day.index, busy_day.values, color='purple')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)

            with col2:
                st.header("Most busy month")
                busy_month = add_on.month_activity_map(user_selects, df)
                fig, ax = plt.subplots()
                ax.bar(busy_month.index, busy_month.values, color='orange')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)

            # Weekly activity map (heatmap)
            st.title("Weekly Activity Map")
            user_heatmap = add_on.activity_heatmap(user_selects, df)
            fig, ax = plt.subplots()
            ax = sns.heatmap(user_heatmap)
            st.pyplot(fig)

            # WordCloud
            st.title("Wordcloud")
            df_wc = add_on.create_wordcloud(user_selects, df)
            fig, ax = plt.subplots()
            ax.imshow(df_wc)
            st.pyplot(fig)

            # Most common words
            most_common_df = add_on.most_common_words(user_selects, df)
            fig, ax = plt.subplots()
            ax.barh(most_common_df[0], most_common_df[1])
            plt.xticks(rotation='vertical')
            st.title('Most Common Words')
            st.pyplot(fig)

            # Emoji analysis
            emoji_df = add_on.emoji_add_on(user_selects, df)
            st.title("Emoji Analysis")
            col1, col2 = st.columns(2)

            with col1:
                st.dataframe(emoji_df)
            with col2:
                fig, ax = plt.subplots()
                ax.pie(emoji_df[1].head(), labels=emoji_df[0].head(), autopct="%0.2f")
                st.pyplot(fig)
    else:
        st.write("📂 **Please upload a WhatsApp chat file to begin analysis.**")

# --------------- NARCOTICS & CBI SECTION ---------------
elif nav_option == 'Narcotics & CBI':
    st.title("Narcotics & CBI Analysis")

    if not df.empty:
        st.dataframe(df)

        # Predefined list of sensitive words
        sensitive_words = [
            'cocaine', 'heroin', 'marijuana', 'weed', 'ganja', 'mdma', 'ecstasy', 'meth', 
            'brown sugar', 'molly', 'acid', 'lsd', 'shrooms', 'pot', 'grass', 'blunt', 'kush', 
            'joint', 'stash', 'hash', 'dope', 'bhang', '420', 'charras', 'party stuff', 'stuff',
            'payment', 'deposit', 'upi', 'transfer', 'amount', 'cash', 'money', 'bank', 
            'bitcoin', 'btc', 'crypto', 'ethereum', 'tether', 'monero', 'wallet',
            'meet at', 'pickup', 'drop', 'location', 'delivery', 'send location', 'parcel',
            'come alone', 'don’t tell anyone', 'delivery time', 'gift', 'drop point', 'pickup point',
            'kill', 'murder', 'attack', 'revenge', 'gun', 'weapon', 'target', 'bomb', 'blast', 
            'pistol', 'ak47', 'mafia', 'terror', 'jihad', 'extort', 'threat', 'ransom', 
            'otp', 'pin', 'password', 'phishing', 'scam', 'fraud', 'hacked', 'dark web', 
            'spyware', 'ransomware', 'breach', 'credit card', 'debit card', 'bank account'
        ]

        # Clean the sensitive words
        sensitive_words = list(set([word.strip().lower() for word in sensitive_words if word.strip()]))
        st.write(f"🔍 **Loaded {len(sensitive_words)} sensitive words for analysis.**")
        
        def detect_sensitive_words(messages, sensitive_words):
            flagged_messages = []
            pattern = r'\b(' + '|'.join(re.escape(word) for word in sensitive_words) + r')\b'
            
            for i, row in messages.iterrows():
                match = re.search(pattern, row['message'], re.IGNORECASE)
                if match:
                    flagged_messages.append({
                        'user': row['user'],
                        'message': row['message'],
                        'bad_word': match.group()
                    })
            
            return pd.DataFrame(flagged_messages)

        flagged_df = detect_sensitive_words(df, sensitive_words)
        
        if not flagged_df.empty:
            st.write(f"**🚩 Total flagged messages: {len(flagged_df)}**")
            
            # Identify the culprit
            culprit = flagged_df['user'].value_counts().idxmax()
            st.warning(f"🚨 **Potential Culprit Detected: {culprit}** 🚨")
            
            st.warning("The following table contains sensitive information. Click to view it.")
            
            with st.expander("View Sensitive Information"):
                st.dataframe(flagged_df[['user', 'message', 'bad_word']])
        else:
            st.write("✅ **No sensitive information detected in the chat.**")
    else:
        st.write("📂 **Please upload a WhatsApp chat file to begin analysis.**")
