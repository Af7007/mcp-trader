import torch
import logging
from datetime import datetime
from datasets import load_dataset
from transformers import (
    TrainingArguments, 
    AutoModelForCausalLM, 
    AutoTokenizer, 
    BitsAndBytesConfig,
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    logger.info("=" * 60)
    logger.info("Iniciando Fine-Tuning do Agente de IA")
    logger.info("=" * 60)
    
    model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    logger.info(f"Modelo: {model_name}")
    
    logger.info("\n[1/5] Configurando quantização 4-bit...")
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16
    )
    
    logger.info("[2/5] Carregando modelo com quantização...")
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
    )
    logger.info("      ✓ Modelo carregado com sucesso!")
    
    logger.info("[2.5/5] Configurando LoRA adapters...")
    lora_config = LoraConfig(
        r=8,
        lora_alpha=16,
        target_modules=["q_proj", "v_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )
    model = get_peft_model(model, lora_config)
    logger.info("      ✓ LoRA adapters configurados!")
    
    logger.info("[3/5] Carregando tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token
    logger.info("      ✓ Tokenizer carregado!")
    
    logger.info("[4/5] Carregando e formatando dataset...")
    
    def formatting_prompts_func(examples):
        instructions = examples["instruction"]
        outputs = examples["output"]
        texts = []
        for instruction, output in zip(instructions, outputs):
            # Garantir que instruction e output são strings
            inst_str = str(instruction) if instruction else ""
            out_str = str(output) if output else ""
            text = f"### Instruction:\n{inst_str}\n\n### Response:\n{out_str}"
            texts.append(text)
        return {"text": texts}
    
    dataset = load_dataset("json", data_files="finetune_dataset.jsonl", split="train")
    logger.info(f"      Dataset carregado: {len(dataset)} exemplos")
    
    dataset = dataset.map(formatting_prompts_func, batched=True)
    logger.info("      ✓ Dataset formatado!")
    
    logger.info("      Tokenizando dataset...")
    def tokenize_function(examples):
        return tokenizer(
            examples["text"],
            padding="max_length",
            truncation=True,
            max_length=512,
        )
    
    dataset = dataset.map(
        tokenize_function,
        batched=True,
        remove_columns=["text", "instruction", "output"],
        cache_file_name=".cache/tokenized_dataset"
    )
    
    def add_labels(examples):
        examples["labels"] = examples["input_ids"].copy()
        return examples
    
    dataset = dataset.map(
        add_labels,
        batched=True,
        cache_file_name=".cache/labeled_dataset"
    )
    logger.info("      ✓ Dataset tokenizado!")
    
    logger.info("[5/5] Iniciando treinamento...")
    logger.info("-" * 60)
    
    training_args = TrainingArguments(
        output_dir="outputs",
        per_device_train_batch_size=1,
        gradient_accumulation_steps=1,
        warmup_steps=0,
        max_steps=3,
        learning_rate=2e-4,
        fp16=False,
        bf16=torch.cuda.is_bf16_supported(),
        logging_steps=1,
        weight_decay=0.01,
        lr_scheduler_type="linear",
        seed=3407,
        save_strategy="no",
        dataloader_pin_memory=False,
        dataloader_num_workers=0,
        report_to="none",
        remove_unused_columns=False,
        disable_tqdm=False,
    )
    
    logger.info("Preparando data collator...")
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False,
        return_tensors="pt"
    )
    
    logger.info("Inicializando trainer...")
    trainer = Trainer(
        model=model,
        train_dataset=dataset,
        args=training_args,
        data_collator=data_collator,
    )
    
    logger.info("Iniciando treinamento...")
    trainer.train()
    logger.info("-" * 60)
    logger.info("✓ Treinamento concluído!")
    
    logger.info("\nSalvando modelo fine-tuned...")
    model.save_pretrained("fine_tuned_model")
    tokenizer.save_pretrained("fine_tuned_model")
    logger.info("✓ Modelo salvo em 'fine_tuned_model'!")
    
    logger.info("=" * 60)
    logger.info("Fine-Tuning concluído com sucesso!")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()