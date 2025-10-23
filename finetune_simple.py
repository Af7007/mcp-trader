import torch
import logging
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
    Trainer,
)
from peft import LoraConfig, get_peft_model

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("=" * 60)
    logger.info("Fine-Tuning Simples com LoRA")
    logger.info("=" * 60)
    
    model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    logger.info(f"Modelo: {model_name}")
    
    logger.info("[1/5] Carregando modelo...")
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16
    )
    
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=bnb_config,
        device_map="auto",
    )
    logger.info("✓ Modelo carregado")
    
    logger.info("[2/5] Configurando LoRA...")
    lora_config = LoraConfig(
        r=8,
        lora_alpha=16,
        target_modules=["q_proj", "v_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )
    model = get_peft_model(model, lora_config)
    logger.info("✓ LoRA configurado")
    
    logger.info("[3/5] Carregando tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer.pad_token = tokenizer.eos_token
    logger.info("✓ Tokenizer carregado")
    
    logger.info("[4/5] Preparando dataset...")
    dataset = load_dataset("json", data_files="finetune_dataset.jsonl", split="train")
    logger.info(f"✓ Dataset: {len(dataset)} exemplos")
    
    def format_data(examples):
        texts = []
        for inst, out in zip(examples["instruction"], examples["output"]):
            text = f"### Instruction:\n{inst}\n\n### Response:\n{out}"
            texts.append(text)
        return {"text": texts}
    
    dataset = dataset.map(format_data, batched=True, remove_columns=["instruction", "output"])
    
    def tokenize(examples):
        return tokenizer(examples["text"], truncation=True, max_length=512)
    
    dataset = dataset.map(tokenize, batched=True, remove_columns=["text"])
    dataset = dataset.map(lambda x: {"labels": x["input_ids"]}, batched=True)
    
    logger.info("✓ Dataset preparado")
    
    logger.info("[5/5] Iniciando treinamento...")
    training_args = TrainingArguments(
        output_dir="outputs",
        num_train_epochs=1,
        per_device_train_batch_size=1,
        logging_steps=1,
        save_strategy="no",
        report_to="none",
    )
    
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
    )
    
    trainer.train()
    logger.info("✓ Treinamento concluído!")
    
    logger.info("Salvando modelo...")
    model.save_pretrained("fine_tuned_model")
    tokenizer.save_pretrained("fine_tuned_model")
    logger.info("✓ Modelo salvo!")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()
