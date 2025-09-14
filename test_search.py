from main import search

query = "Как получить направление на анализы"
print(f"Query: {query}")
answer, results = search(query)
print(f"Answer: {answer}")
print(f"Results: {len(results)}")
for hit in results:
    print(f"Question: {hit.entity.question}")
    print(f"Answer: {hit.entity.answer}")
