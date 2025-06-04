import streamlit as st

# Title of the app
st.title("codeChecker")



# Text input
code = st.text_input("Enter your code:", """
        def calculate_stats(data):
            total = sum(data)
            average = total / len(data)
            return {"total": total, "avg": average}

        def process_user(user):
            user["full_name"] = user["name"] + " " + user["surname"]
            user["age_next_year"] = user.age + 1
            return user

        def load_config():
            config = {"timeout": 30, "retries": 3}
            return config["retry_count"]

        def main():
            stats = calculate_stats([])
            print(stats)

            user = {"name": "Alice"}
            processed_user = process_user(user)
            print(processed_user)

            config_value = load_config()
            print(config_value)

            value = "123"
            result = value + 5
            print(result)

        if __name__ == "__main__":
            main()""")

# Description
st.code(code)

errorType = st.segmented_control("error type", ["runitme", "syntax", "logical"], default="syntax")

st.write("checking for " + errorType)

