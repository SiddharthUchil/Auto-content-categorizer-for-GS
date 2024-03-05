import os
import openai
import gspread
from oauth2client.service_account import ServiceAccountCredentials

from dotenv import load_dotenv

load_dotenv()
# Setup OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')
client = openai.OpenAI(
    api_key=openai.api_key,
    base_url="http://localhost:11434/v1"
)

# Setup Google Sheets
spread_sheets_id = os.getenv('SPREAD_SHEETS_ID')
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name('key.json', scope)
gc = gspread.authorize(credentials)
sheet = gc.open_by_key(spread_sheets_id).sheet1


def classify_comment(comment):
    try:
        response = client.chat.completions.create(
            model="llama2",
            messages=[
                {"role": "system", "content": """
                    You are a helpful assistant designed to classify comments into: 
                    computer-vison, mlops, natural-language-processing or other. 
                    Must respond with one word.
                    """
                },
                {"role": "user", "content": "Comparison between YOLO and RCNN on real world videos"},
                {"role": "assistant", "content": "computer-vision"},
                {"role": "user", "content": "Show, Infer & Tell: Contextual Inference for Creative Captioning"},
                {"role": "assistant", "content": "computer-vision"},
                {"role": "user", "content": "ELECTRA: Pre-training Text Encoders as Discriminators"},
                {"role": "assistant", "content": "natural-language-processing"},
                {"role": "user", "content": "Tuned ALBERT (ensemble model)"},
                {"role": "assistant", "content": "natural-language-processing"},
                {"role": "user", "content": "Debugging Neural Networks with PyTorch and W&B"},
                {"role": "assistant", "content": "mlops"},
                {"role": "user", "content": "Machine learning deserves its own flavor of Continuous Delivery"},
                {"role": "assistant", "content": "mlops"},
                {"role": "user", "content": "Curriculum for Reinforcement Learning"},
                {"role": "assistant", "content": "other"},
                {"role": "user", "content": "Almost Everything You Need to Know About Time Series"},
                {"role": "assistant", "content": "other"},
                {"role": "user", "content": comment}  # This is the comment you want to classify
            ]
        )
        category = response.choices[0].message.content.strip()
        print(f"Comment: '{comment}' -> Category: '{category}'")
        return category.title()
    except Exception as e:
        print(f"Error in classifying comment: {e}")
        return "Process Failed"


# Read data from the sheet
data = sheet.get_all_values()
header = data[0]  # Assuming the first row is the header
comments_rows = data[1:]  # Exclude header

# Iterate over each row that contains comments
for i, row in enumerate(comments_rows, start=2):  # Google Sheets is 1-indexed; header is row 1, so data starts at row 2
    comment = row[1]  # Assuming the comment is in the second column
    category = classify_comment(comment)
    # Update the 3th column (index 2) with the classification
    sheet.update_cell(i, 3, category)

print("The Google Sheet has been updated with categories for each comment.")


