import csv
from itertools import combinations

def load_data(file_path):
    """
    Load transaction data from a CSV file.
    Each row in the CSV file represents a transaction.
    """
    transactions = []
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            transactions.append(set(row))  # Convert each row to a set of items
    return transactions

def generate_candidates(itemsets, length):
    """
    Generate candidate itemsets of a given length.
    """
    return set([frozenset(comb) for itemset in itemsets for comb in combinations(itemset, length)])

def filter_candidates(transactions, candidates, min_support):
    """
    Filter candidates based on minimum support.
    """
    itemset_counts = {candidate: 0 for candidate in candidates}
    for transaction in transactions:
        for candidate in candidates:
            if candidate.issubset(transaction):
                itemset_counts[candidate] += 1

    # Keep only itemsets that meet the minimum support
    num_transactions = len(transactions)
    frequent_itemsets = {itemset: count for itemset, count in itemset_counts.items() if count / num_transactions >= min_support}
    return frequent_itemsets

def apriori(transactions, min_support):
    """
    Apriori algorithm to find frequent itemsets.
    """
    # Step 1: Generate frequent 1-itemsets
    items = set(item for transaction in transactions for item in transaction)
    candidates = [frozenset([item]) for item in items]
    frequent_itemsets = filter_candidates(transactions, candidates, min_support)

    all_frequent_itemsets = frequent_itemsets.copy()
    k = 2

    # Step 2: Generate frequent k-itemsets
    while frequent_itemsets:
        candidates = generate_candidates(frequent_itemsets.keys(), k)
        frequent_itemsets = filter_candidates(transactions, candidates, min_support)
        all_frequent_itemsets.update(frequent_itemsets)
        k += 1

    return all_frequent_itemsets

def main():
    # File path to the CSV file
    file_path = 'data/processed_data.csv'

    # Minimum support threshold
    min_support = 0.5  # Example: 50%

    # Load transactions from the CSV file
    transactions = load_data(file_path)

    # Run the Apriori algorithm
    frequent_itemsets = apriori(transactions, min_support)

    # Print the results
    print("Frequent Itemsets:")
    for itemset, count in frequent_itemsets.items():
        print(f"{set(itemset)}: {count}")

if __name__ == "__main__":
    main()