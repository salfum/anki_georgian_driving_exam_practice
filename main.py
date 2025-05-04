import os
import random
import json
import html
import genanki
from dotenv import load_dotenv

load_dotenv()

anki_model_id = int(os.getenv('MODEL_ID', random.randrange(1 << 30, 1 << 31)))
anki_deck_id = int(os.getenv('DECK_ID', random.randrange(1 << 30, 1 << 31)))

print("Model ID: ", anki_model_id)
print("Deck ID: ", anki_deck_id)

questions_file_path = './assets/static_data_ru.json'
images_dir_path = './assets/images'
images_ext = '.jpg'

anki_deck_name = 'Georgian driving exam practice RU'
anki_model_name = anki_deck_name + " Model"
anki_template_name = anki_deck_name + " Template"

apkg_file_name = 'geo_exam.apkg'

fields=[
    {'name': 'ID'},
    {'name': 'Question'},
    {'name': 'All Answers'},
    {'name': 'Answer'},
    {'name': 'Image'},
    {'name': 'Hint'},
]

front_template = """
{{#Image}}
<div style="text-align:center; margin-bottom:10px;">
  <img src="{{Image}}" style="max-width:300px;">
</div>
{{/Image}}
<div style="text-align:center;">
  <strong>{{Question}}</strong>
</div>
<div style="text-align:center;">
  <ul style="display:inline-block; margin-top:20px; text-align:center; padding-left:0; list-style-position:inside;">
    {{All Answers}}
  </ul>
</div>
"""

back_template = """
{{FrontSide}}<hr id=answer>
<div style="margin-top:30px; text-align:center;">
  <strong style="font-size:1.2em;">{{Answer}}</strong>
</div>
{{#Hint}}
<div style="opacity:0.8; font-size:13pt; margin-top:20px;">
  <em>Примечание:</em><br>
  <ul>
    {{Hint}}
  </ul>
</div>
{{/Hint}}
"""

templates=[{
    'name': anki_template_name,
    'qfmt': front_template,
    'afmt': back_template,
}]

print("Creating a model...")
anki_model = genanki.Model(
    anki_model_id,
    anki_model_name,
    fields = fields,
    templates = templates,
)
print("Model created!")

with open(questions_file_path, 'r') as file:
    print("Loading questions...")
    json_questions = json.load(file)
    print(json_questions.__len__(), " questions loaded!")

    anki_questions = []
    media_files = []

    print("Collecting cards and images...")
    for json_question in json_questions:
        id_field = json_question['id']
        image_field = json_question['img'] if 'img' in json_question else ""

        question = json_question['question']
        answers = json_question['answers']
        correct_answer = ""

        if image_field != "":
            image = image_field + '.png'
            media_files.append(images_dir_path + '/' + image_field + images_ext)
        else:
            image = ""

        for answer in answers:
            if 'correct' in answer and answer['correct'] is True:
                correct_answer = answer['text']

        all_answers_html = ''.join(f"<li>{a['text']}</li>" for a in answers)

        # hint is an empty field for user
        # to fill something helpfull
        hint = ""
        
        anki_question = genanki.Note(
            model=anki_model,
            fields=[
                str(id_field),
                html.escape(question),
                all_answers_html,
                html.escape(correct_answer),
                html.escape(image),
                hint
            ],
        )

        anki_questions.append(anki_question)

    print(json_questions.__len__(), " cards collected!")
    print(media_files.__len__(), " images collected!")
        
    my_deck = genanki.Deck(anki_deck_id, anki_deck_name)

    package = genanki.Package(my_deck)
    package.media_files = media_files

    for anki_question in anki_questions:
        my_deck.add_note(anki_question)
    
    print("Creating anki package...")
    package.write_to_file(apkg_file_name)
    print("Anki package created!")
