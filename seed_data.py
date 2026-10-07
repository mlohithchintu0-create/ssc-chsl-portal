"""
Master Seeding Script for SSC CHSL Portal
Executes seed_base.py and generate_questions.py.
"""
from seed_base import seed_all
from generate_questions import build_questions_and_mocks
from insert_model_papers import create_model_papers

def main():
    print("Step 1: Seeding subjects, topics, and initial users...")
    seed_all()
    print("Step 2: Building full Tier-I (100 Qs), Tier-II (135 Qs), typing passages, and study capsules...")
    build_questions_and_mocks()
    print("Step 3: Generating and inserting SSC CHSL Model Papers (Tier-I & Tier-II)...")
    create_model_papers()
    print("Master database build completed successfully.")

if __name__ == '__main__':
    main()
