"""
================================================================================
MODULE 1: Embeddings & Similarity Search Demo
================================================================================

WHY EMBEDDINGS MATTER:
━━━━━━━━━━━━━━━━━━━━━
Traditional search: "password reset" only finds docs with those exact words
Semantic search:    "password reset" also finds "forgot credentials", 
                    "can't log in after changing password", "auth issues"

This is the FOUNDATION of RAG - without good embeddings, retrieval fails!

WHAT YOU'LL LEARN:
━━━━━━━━━━━━━━━━━
1. How to generate embeddings from text using OpenAI
2. What embeddings actually look like (1536 numbers!)
3. Computing similarity scores (cosine similarity)
4. Finding most similar documents (semantic search)
5. Visualizing the relationships embeddings capture

THE BIG PICTURE:
━━━━━━━━━━━━━━━
    Text → [Embedding Model] → Vector (1536 floats) → [Compare] → Similarity Score
    
    "login fails"     →  [0.023, -0.041, ...]  ─┐
                                                 ├─→ 0.89 (similar!)
    "auth not working" → [0.019, -0.038, ...]  ─┘

LEARNING RESOURCES:
- OpenAI Embeddings Guide: https://platform.openai.com/docs/guides/embeddings
- Understanding Vector Embeddings: https://www.pinecone.io/learn/vector-embeddings/
- Cosine Similarity Explained: https://en.wikipedia.org/wiki/Cosine_similarity
"""

# =============================================================================
# IMPORTS
# =============================================================================

import json
import numpy as np
import os
from openai import OpenAI
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from logger import Logger

class EmbeddingDemo:
    def __init__(self):
        # Load the .env file
        load_dotenv()
        # Initialize OpenAI client
        print("Initializing OpenAI client...")
        self.client = OpenAI(api_key=os.getenv("OPENAI_APIKEY"))

        # Embedding Model Selection (using text-embedding-3-small model)
        self.embed_model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
        self.embedding_dim = 1536
        print(f"Embedding model: {self.embed_model}")
        print(f"Embedding dimension: {self.embedding_dim}")

        # Load support tickets
        print("\nLoading support tickets...")
        with open("../../data/synthetic_tickets.json", "r") as f:
            self.tickets = json.load(f)
        print(f"\nLoaded {len(self.tickets)} support tickets.")
               

    def print_ticket(self, idx = 0):
        if idx < 0 or idx >= len(self.tickets):
            print("Invalid ticket index.")
            return

        print("\n" + "="*80)
        print("TICKET:")
        print("="*80)
        sample = self.tickets[idx]
        print(f"ID: {sample['ticket_id']}")
        print(f"Title: {sample['title']}")
        print(f"Description: {sample['description'][:200]}...")
        print(f"Category: {sample['category']}")
        print(f"Priority: {sample['priority']}")        
        

    def generate_embeddings(self):
        print("\n" + "="*80)
        print("Generating embeddings ....")
        print("="*80)

        ticket_texts = [
            f"{ticket['title']}. {ticket['description']}"
            for ticket in self.tickets
        ]
        print("\n" + "="*80)
        print("Generated ticket texts.")
        print("="*80)
        print(ticket_texts)

        print("\n Generating embeddings for all tickets ....")
        response = self.client.embeddings.create(
            model = self.embed_model,
            input = ticket_texts
        )

        self.embeddings = np.array([data.embedding for data in response.data])
        print(f"✓ Generated embeddings with shape: {self.embeddings.shape}")
        print(f" ({len(self.tickets)} tickets X {self.embedding_dim} dimensions)")
    
    def print_embedding(self, ticket_idx):
        print(f"Priniting first 10 values of embeddings for ticket  {ticket_idx + 1}")
        print(self.embeddings[ticket_idx][:10])
        
    def get_similarity(self, query_text):
        """
        Compute cosine similarity between two texts
        """
        query_response = self.client.embeddings.create(
            model = self.embed_model,
            input = query_text
        )
        query_embedding = np.array([query_response.data[0].embedding])

        similarity_score = cosine_similarity(query_embedding, self.embeddings)
        print(f"\nComputed similarity scores for {len(similarity_score)} tickets")
        print(f"Similarity range: [{similarity_score.min():.4f}, {similarity_score.max():.4f}]")
        return similarity_score

    def get_relevant_tickets(self, query_text, top_k=5, threshold=0.0, category=None, show_chart = False):
        similarity_scores = self.get_similarity(query_text)

        # relevant_indices = np.argsort(similarity_scores)[::-1][:top_k]
        relevant_indices = [
            idx for idx in np.argsort(similarity_scores[0])[::-1] 
            if similarity_scores[0, idx] >= threshold 
            and (category is None or not category.strip() or self.tickets[idx]['category'].lower() == category.strip().lower())
        ][:top_k]

        category_str = f" [Category: {category}]" if category else ""
        print(f"\nTop {top_k} most similar tickets to query: '{query_text}'{category_str}")
        print("-" * 80)

        logger = Logger()

        for rank, idx in enumerate(relevant_indices, 1):
            ticket = self.tickets[idx]
            score = similarity_scores[0, idx]
            print(f"\n#{rank} - Similarity: {score:.4f}")
            print(f"Ticket ID: {ticket['ticket_id']}")
            print(f"Title: {ticket['title']}")
            print(f"Category: {ticket['category']} | Priority: {ticket['priority']}")
            print(f"Description: {ticket['description'][:200]}...")
            logger.log(f"#{rank} - Similarity: {score:.4f}")
            logger.log(f"Ticket ID: {ticket['ticket_id']}")
            logger.log(f"Title: {ticket['title']}")
            logger.log(f"Category: {ticket['category']} | Priority: {ticket['priority']}")
            logger.log(f"Description: {ticket['description']}...")
            
        if show_chart:
            self.show_visual(query_text, relevant_indices, similarity_scores)
        
        

    def show_visual(self, query_text, relevant_indices, similarities):
        selected_indices = list(relevant_indices[:5]) + list(np.random.choice(
            [i for i in range(len(self.tickets)) if i not in relevant_indices[:5]], 
            size=min(5, len(self.tickets) - 5), 
            replace=False
        ))

        selected_embeddings = self.embeddings[selected_indices]
        similarity_matrix = cosine_similarity(selected_embeddings)

        # -----------------------------------------------------------------------------
        # Create the visualization
        # -----------------------------------------------------------------------------
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

        # LEFT PLOT: Similarity heatmap
        # Shows pairwise similarity between all selected tickets
        # Green = high similarity, Red = low similarity
        im = ax1.imshow(similarity_matrix, cmap='RdYlGn', vmin=0, vmax=1)
        ax1.set_xticks(range(len(selected_indices)))
        ax1.set_yticks(range(len(selected_indices)))

        # Label with ticket IDs and categories
        labels = [f"{self.tickets[i]['ticket_id']}\n({self.tickets[i]['category']})" 
                for i in selected_indices]
        ax1.set_xticklabels(labels, rotation=45, ha='right', fontsize=8)
        ax1.set_yticklabels(labels, fontsize=8)

        # Add similarity values to cells (so students can read exact numbers)
        for i in range(len(selected_indices)):
            for j in range(len(selected_indices)):
                text = ax1.text(j, i, f'{similarity_matrix[i, j]:.2f}',
                            ha="center", va="center", color="black", fontsize=9)

        ax1.set_title('Similarity Heatmap: What Embeddings Actually Measure\n' + 
                    '(Top 5 matches + random others)', fontweight='bold', fontsize=11)
        plt.colorbar(im, ax=ax1, label='Cosine Similarity')

        # RIGHT PLOT: Query similarities bar chart
        # Shows how similar each ticket is to the original query
        query_similarities = [similarities[0, i] for i in selected_indices]
        colors_bar = ['green' if i < 5 else 'gray' for i in range(len(selected_indices))]

        ax2.barh(range(len(selected_indices)), query_similarities, color=colors_bar, alpha=0.7)
        ax2.set_yticks(range(len(selected_indices)))
        ax2.set_yticklabels([f"{self.tickets[i]['ticket_id']}" for i in selected_indices], fontsize=9)
        ax2.set_xlabel('Similarity to Query', fontweight='bold')
        ax2.set_title(f'Similarity Scores for Query:\n"{query_text}"\n(Green = Top N matches)',  
                    fontweight='bold', fontsize=11)
        ax2.set_xlim(0, 1)
        ax2.grid(axis='x', alpha=0.3)

        # Add score labels on bars
        for i, score in enumerate(query_similarities):
            ax2.text(score + 0.02, i, f'{score:.3f}', va='center', fontsize=9)

        plt.tight_layout()
        plt.savefig('embeddings_similarity_analysis.png', dpi=150, bbox_inches='tight')
        print("✓ Visualization saved as 'embeddings_similarity_analysis.png'")
        print("\nKEY INSIGHTS FROM THIS VISUALIZATION:")
        print("  • Left heatmap: Shows TRUE pairwise similarities in 1536D space")
        print("  • Right chart: Query similarity scores (what drives retrieval)")
        print("  • High similarity (green) = semantically similar content")
        print("  • Low similarity (red) = different topics/meanings")
        print("  • These scores are EXACT - they show true relationships in 1536D space!")
        plt.show(block=False)

        
        


if __name__ == "__main__":
    demo = EmbeddingDemo()
    logger = Logger()
    demo.print_ticket(0)

    test_queries = [
        "Users can't login after changing password",
        "Database is running very slowly",
        "Payment failed for international customers",
        "Mobile app keeps crashing",
        "Emails are not being delivered",
        "How to make pizza?",
        "Login authentication failed",
        "Slow database performance",
        "login problem"
    ]

    demo.generate_embeddings()

    while True:
        print("Select Option for query text")
        print(f"1. {test_queries[0]}")
        print(f"2. {test_queries[1]}")
        print(f"3. {test_queries[2]}")
        print(f"4. {test_queries[3]}")
        print(f"5. {test_queries[4]}")
        print(f"6. {test_queries[5]}")
        print(f"7. {test_queries[6]}")
        print(f"8. {test_queries[7]}")
        print(f"9. {test_queries[8]}")
        print("10. Exit")

        option = int(input("Enter your option: "))
        if(option <= len(test_queries)):
            show_chart_val = input("Do you want to see the chart? (yes/no) (default no): ")
            try:
                show_chart = True if show_chart_val.lower() == 'yes' else False
            except ValueError:
                print("Invalid input. Using default no.")
                show_chart = False
        else:
            print("Exiting...")
            break
        
        k_val = input("Enter top K (default 5): ")
        try:
            k = int(k_val) if k_val.strip() else 5
        except ValueError:
            print("Invalid input. Using default 5.")
            k = 5

        threshold_val = input("Enter threshold (0 - 1) (default 0.0): ")
        try:
            threshold = float(threshold_val) if threshold_val.strip() else 0.0
        except ValueError:
            print("Invalid input. Using default 0.0.")
            threshold = 0.0

        category_val = input("Enter category filter (optional, e.g. Authentication, Database) (default none): ")
        category = category_val.strip() if category_val.strip() else None

        query = test_queries[option - 1]

        logger.log("="*80)
        logger.log("\n")
        logger.log(f"\nQuery : {query} \n")
        logger.log(f"Threshold : {threshold} \n")
        if category:
            logger.log(f"Category : {category} \n")
        logger.log(f"Top K : {k} \n")

        logger.log('='*80)
        logger.log('\n')

        
        print(f"\nQuery: {query}")
        demo.get_relevant_tickets(query, top_k=k, threshold=threshold, category=category, show_chart = show_chart)
        
    logger.save_logs("embeddings_demo_results.txt")
        

        