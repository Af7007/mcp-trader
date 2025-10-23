import torch
import logging
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import LoraConfig
from trl import SFTTrainer, SFTConfig

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("=" * 60)
    logger.info("Fine-Tuning Moderno com SFTTrainer e LoRA")
    logger.info("=" * 60)
    
    model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    logger.info(f"Modelo: {model_name}")
    
    logger.info("[1/4] Carregando modelo...")
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
    
    logger.info("[2/4] Carregando tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer.pad_token = tokenizer.eos_token
    logger.info("✓ Tokenizer carregado")
    
    logger.info("[3/4] Preparando dataset...")
    dataset = load_dataset("json", data_files="finetune_dataset.jsonl", split="train")
    logger.info(f"✓ Dataset: {len(dataset)} exemplos")
    
    def format_data(examples):
        texts = []
        for inst, out in zip(examples["instruction"], examples["output"]):
            text = f"### Instruction:\n{inst}\n\n### Response:\n{out}"
            texts.append(text)
        return {"text": texts}
    
    dataset = dataset.map(format_data, batched=True, remove_columns=["instruction", "output"])
    logger.info("✓ Dataset preparado")
    
    logger.info("[4/4] Iniciando treinamento...")
    
    lora_config = LoraConfig(
        r=8,
        lora_alpha=16,
        target_modules=["q_proj", "v_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )
    
    training_args = SFTConfig(
        output_dir="outputs",
        num_train_epochs=1,
        per_device_train_batch_size=1,
        logging_steps=1,
        save_strategy="no",
        report_to="none",
        dataset_text_field="text",
        max_seq_length=512,
        peft_config=lora_config,
    )
    
    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        args=training_args,
        train_dataset=dataset,
    )
    
    trainer.train()
    logger.info("✓ Treinamento concluído!")
    
    logger.info("Salvando modelo...")
    trainer.save_model("fine_tuned_model")
    logger.info("✓ Modelo salvo!")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()
