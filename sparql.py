"""
Claims of Tamriel — SPARQL Queries (v5.0)
==========================================
Requirement : pip install rdflib
Usage       : python sparql_queries.py
Note        : TTL file must be in the same folder as this script.
"""

from rdflib import Graph

TTL_FILE = "skyrim_ontology_v5_0.ttl"

g = Graph()
g.parse(TTL_FILE, format="turtle")
print(f"Ontology loaded: {len(g)} triples\n")


def run(title, query):
    print("=" * 65)
    print(f"  {title}")
    print("=" * 65)
    results = list(g.query(query))
    if not results:
        print("  (no results)")
    for row in results:
        print("  " + "  |  ".join(str(v) if v else "-" for v in row))
    print(f"\n  Rows returned : {len(results)}")
    print()


# ─────────────────────────────────────────────────────────────
# CQ1 — All contradicting pairs with holders and types
# ─────────────────────────────────────────────────────────────
run(
    "CQ1 — Contradicting Pairs",
    """
    PREFIX : <http://www.semanticweb.org/skyrim/ontology#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?labelA ?holderA ?typeA ?labelB ?holderB ?typeB
    WHERE {
      ?claimA a :Claim ;
        :contradicts ?claimB ;
        rdfs:label ?labelA ;
        :hasClaimType ?typeA ;
        :hasClaimHolder ?charA .
      ?claimB a :Claim ;
        rdfs:label ?labelB ;
        :hasClaimType ?typeB ;
        :hasClaimHolder ?charB .
      ?charA rdfs:label ?holderA .
      ?charB rdfs:label ?holderB .
      FILTER (STR(?claimA) < STR(?claimB))
    }
    ORDER BY ?typeA
    """
)

# ─────────────────────────────────────────────────────────────
# CQ2 — Faction conflict matrix (inferred, not directly asserted)
# ─────────────────────────────────────────────────────────────
run(
    "CQ2 — Faction Conflict Matrix",
    """
    PREFIX : <http://www.semanticweb.org/skyrim/ontology#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?factionA ?factionB (COUNT(DISTINCT ?claimA) AS ?conflicts)
    WHERE {
      ?claimA :hasSource ?facA ;
              :contradicts ?claimB .
      ?claimB :hasSource ?facB .
      ?facA rdfs:label ?factionA .
      ?facB rdfs:label ?factionB .
      FILTER (?facA != ?facB && STR(?facA) < STR(?facB))
    }
    GROUP BY ?factionA ?factionB
    ORDER BY DESC(?conflicts)
    """
)

# ─────────────────────────────────────────────────────────────
# CQ3 — Evidence cited by directly opposing claims
# ─────────────────────────────────────────────────────────────
run(
    "CQ3 — Contested Evidence",
    """
    PREFIX : <http://www.semanticweb.org/skyrim/ontology#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?evLabel (COUNT(DISTINCT ?claim) AS ?citedBy)
           (GROUP_CONCAT(DISTINCT ?claimLabel; separator=" | ") AS ?claims)
    WHERE {
      ?claim a :Claim ;
        :hasEvidence ?ev ;
        :contradicts ?opposing ;
        rdfs:label ?claimLabel .
      ?opposing :hasEvidence ?ev .
      ?ev rdfs:label ?evLabel .
    }
    GROUP BY ?evLabel
    ORDER BY DESC(?citedBy)
    """
)

# ─────────────────────────────────────────────────────────────
# CQ4 — Neutrality detection (absence of framesAs)
# ─────────────────────────────────────────────────────────────
run(
    "CQ4 — Neutrality Detection",
    """
    PREFIX : <http://www.semanticweb.org/skyrim/ontology#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?charLabel ?role
    WHERE {
      ?char a :Character ;
        rdfs:label ?charLabel ;
        :hasRole ?role .
      FILTER NOT EXISTS {
        ?char :framesAs ?anyClaim
      }
    }
    """
)

# ─────────────────────────────────────────────────────────────
# CQ5 — Denial chains (directional, active repudiation)
# ─────────────────────────────────────────────────────────────
run(
    "CQ5 — Denial Chains",
    """
    PREFIX : <http://www.semanticweb.org/skyrim/ontology#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?denierLabel ?deniedLabel ?deniedHolderLabel
    WHERE {
      ?denier :framesAs ?claim .
      ?claim :denies ?denied .
      ?denied :hasClaimHolder ?dh .
      ?denier rdfs:label ?denierLabel .
      ?denied rdfs:label ?deniedLabel .
      ?dh rdfs:label ?deniedHolderLabel .
    }
    """
)

print("All queries complete.")