from transformers import pipeline
import pandas as pd
import json
from docx import Document

def read_docx(file_path):
    doc = Document(file_path)
    text = []
    for paragraph in doc.paragraphs:
        text.append(paragraph.text)
    return "n".join(text)


def get_context():
    # Загрузка данных из Excel файла
    file_path = 'model_files/01_База_знаний.xlsx'  # Укажите путь к вашему Excel файлу
    df = pd.read_excel(file_path)

    # Создание списка словарей
    data = []
    for _, row in df.iterrows():
        data.append({
            "question": row['Вопрос из БЗ'],
            "answer": row['Ответ из БЗ']
        })

    # Преобразование в JSON формат
    context = json.dumps(data, ensure_ascii=False, indent=4)
    return context

def answer_question(question):
    context = get_context()
    print("Файл контекста получен")
    qa_pipeline = pipeline("question-answering", model="DeepPavlov/rubert-base-cased")
    print("Начало генерации...")
    result = qa_pipeline(question, context)
    print("Генерация завершена!")
    return result['answer']

#Обучение(функция содержит ошибку)
def train():
    from transformers import Trainer, TrainingArguments, BertForQuestionAnswering, BertTokenizer
    from datasets import Dataset

    # Загрузка предобученной модели и токенизатора
    model_name = "DeepPavlov/rubert-base-cased"
    model = BertForQuestionAnswering.from_pretrained(model_name)
    tokenizer = BertTokenizer.from_pretrained(model_name)

    placement_conditions_text = read_docx('model_files/04_УСЛОВИЯ РАЗМЕЩЕНИЯ КОНТЕНТА.docx')
    data_description_text = read_docx('model_files/00_Описание данных.docx')
    agreement_text = read_docx('model_files/03_ГЕНЕРАЛЬНОЕ ПОЛЬЗОВАТЕЛЬСКОЕ СОГЛАШЕНИЕ RUTUBE.docx')

    texts = [agreement_text, data_description_text, placement_conditions_text]
    labels = ["user_agreement", "data_description", "placement_conditions"]

    # Токенизация входных данных
    encodings = tokenizer(texts, truncation=True, padding=True, return_tensors="pt")

    # Проверка, что токенизация прошла успешно
    print("Input IDs shape:", encodings['input_ids'].shape)
    print("Attention mask shape:", encodings['attention_mask'].shape)

    # Подготовка dataset в нужном формате
    dataset = []
    for i, label in enumerate(labels):
        dataset.append({
            "input_ids": encodings['input_ids'][i].tolist(),
            "attention_mask": encodings['attention_mask'][i].tolist(),
            "label": label
        })

    # Создаем Dataset
    train_dataset = Dataset.from_list(dataset)

    # Обучение модели
    training_args = TrainingArguments(
        output_dir='./results',          # выходная директория
        evaluation_strategy="epoch",     # периодичность оценки во время обучения
        learning_rate=2e-5,
        per_device_train_batch_size=8,
        num_train_epochs=3,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
    )

    trainer.train()

    model.save_pretrained('model_files/saved_model')
    tokenizer.save_pretrained('model_files/saved_model')
    print('Обучение завершено')