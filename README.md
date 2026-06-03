# Claims of Tamriel — OWL Ontology of Contested Narratives

> *An OWL ontology modelling conflicting claims, rival factions, and epistemic conflict in* The Elder Scrolls V: Skyrim  
> **Course:** Knowledge Representation & Knowledge Extraction (KRKE) — University of Bologna  
> **Version:** 5.0

---

## Overview

*Claims of Tamriel* is an OWL ontology that encodes **competing and irreconcilable narratives** within the world of Skyrim. Rather than representing facts about the game world, it models the *structure of disagreement* itself who claims what, against whom, on what grounds, and through what kind of logical opposition.

The ontology operationalises **epistemic pluralism** as a structural commitment: no claim is marked as correct and no faction as authoritative. Every assertion is relativised to its holder. The architecture is domain-neutral — the same pattern (Claim, Holder, ClaimType, three conflict relations, contested evidence) applies equally to news media bias, historical revisionism, or legal testimony.

**Project stats:**

| Dimension | Count |
|---|---|
| OWL Classes | 7 |
| Claim individuals | 16 (8 pairs) |
| Characters | 12 |
| Factions | 8 |
| Conflict types | 3 |
| OWL axioms | 4 |
| External alignments | 4 |
| SKOS ClaimType concepts | 11 |
| Property chain axioms | 1 |

---

## Repository Structure

```
.
├── skyrim_ontology_v5_0.ttl   # OWL ontology serialised in Turtle (RDF/OWL)
├── index.html                 # Interactive project website (standalone, no build step)
└── README.md
```

---

## Core Design

### The Three Laws of Disagreement

All conflict in the ontology is expressed through exactly three typed object properties:

| Property | Characteristic | Semantics | Used for |
|---|---|---|---|
| `contradicts` | `owl:SymmetricProperty` | Strict logical opposition — if A is true, B must be false | 6 of 8 dispute pairs (sovereignty, theology, territorial, political, vampiric) |
| `disputes` | `owl:SymmetricProperty` | Conflicting interpretations where both positions are coherent within their own framework | 2 pairs (cosmological, theological-moral) |
| `denies` | `owl:IrreflexiveProperty` | Directional, active repudiation — propaganda, not just disagreement | Only the Talos pair; uniquely bidirectional |

### Ontology Class Hierarchy

```
owl:Thing
├── Character       (subClassOf foaf:Person)      — 12 individuals
├── Faction         (subClassOf foaf:Group)        — 8 individuals
├── Claim           (subClassOf prov:Entity)       — 16 individuals
├── ClaimType       (SKOS concept scheme)          — 11 concepts
├── City            (subClassOf schema:Place)      — 6 individuals
├── Item                                           — 3 individuals
└── Race                                           — 10 individuals
```

All seven classes are declared mutually disjoint via `owl:AllDisjointClasses`.

### Key Object Properties

| Property | Characteristic | Notes |
|---|---|---|
| `hasClaimHolder` | subPropertyOf `prov:wasAttributedTo` | Links a Claim to its Character holder |
| `hasClaimTypeIRI` | `owl:FunctionalProperty` | Each Claim has exactly one ClaimType |
| `framesAs` / `isFramedBy` | Inverse pair | Links Characters to the Claims they advance |
| `hasOpposingHolder` | Property chain inferred | Derived via `contradicts ∘ hasClaimHolder`; no direct assertion needed |
| `memberOf` | Domain: Character → Range: Faction | Faction membership |

### OWL Restrictions on `Claim`

Every `Claim` individual must satisfy:
- **`hasClaimHolder` some `Character`** — at least one holder
- **`hasClaimTypeIRI` exactly 1 `ClaimType`** — functional classification
- **`hasDescription` some `xsd:string`** — a natural-language description

### Linked Data Alignments

| Ontology Class / Property | External Vocabulary |
|---|---|
| `Character` | `foaf:Person` |
| `Faction` | `foaf:Group` |
| `City` | `schema:Place` |
| `Claim` | `prov:Entity` |
| `hasClaimHolder` | `prov:wasAttributedTo` |

---

## The Eight Disputed Pairs

| ID | Type | Claim A | Claim B | Relation |
|---|---|---|---|---|
| I | Territorial | *Skyrim belongs to the Nords* (Ulfric) | *Skyrim is an Imperial province* (Tullius) | `contradicts` |
| II | Theological | *Talos is the 9th Divine* (Ulfric) | *Talos worship is heresy* (Elenwen) | `contradicts` + `denies` |
| III | Political | *Ulfric is a freedom fighter* (Ulfric) | *Ulfric is a Thalmor asset* (Elenwen) | `contradicts` |
| IV | Moral | *Paarthurnax must face justice* (Delphine) | *Paarthurnax has earned redemption* (Paarthurnax) | `contradicts` |
| V | Theological-Moral | *Lycanthropy is Hircine's gift* (Hircine) | *The werewolf form is a curse* (Dragonborn) | `disputes` |
| VI | Cosmological | *Alduin is the prophesied World-Eater* (Alduin) | *Alduin is powerful, not inevitable* (Dragonborn) | `disputes` |
| VII | Territorial | *The Reach is Reachmen land* (Madanach) | *The Forsworn are criminals* (Tullius) | `contradicts` |
| VIII | Supremacist | *Eternal night is vampire liberation* (Harkon) | *Vampirism is a curse; stop eternal night* (Dragonborn) | `contradicts` |

---

## SKOS ClaimType Hierarchy

The `ClaimType` controlled vocabulary is organised as a SKOS concept scheme (`ClaimTypeScheme`), with `skos:narrower` / `skos:broader` relations between primary claim types and their counter-claim variants.

```
TerritorialClaim
  └── SovereigntyClaim (narrower)
TheologicalClaim
  ├── TheologicalCounterClaim (narrower)
  └── TheologicalMoralClaim (narrower, skos:related MoralClaim)
PoliticalClaim
  └── PoliticalCounterClaim (narrower)
MoralClaim
  └── MoralCounterClaim (narrower)
CosmologicalClaim
  └── CosmologicalCounterClaim (narrower)
SupremacistClaim (standalone)
```

---

## SPARQL Competency Questions

Five competency questions drove the property architecture and validate design decisions:

| CQ | Question | Key technique |
|---|---|---|
| CQ1 | All contradicting claim pairs with holders and types | `contradicts` + `FILTER(STR(?A) < STR(?B))` to deduplicate |
| CQ2 | Faction conflict matrix | `memberOf → framesAs → contradicts` chain; entirely emergent |
| CQ3 | Evidence cited by directly opposing claims | `hasEvidence` on both sides of `contradicts` |
| CQ4 | Neutral characters (no `framesAs` assertions) | `FILTER NOT EXISTS { ?char :framesAs ?anyClaim }` |
| CQ5 | Directional denial chains | Traversal of asymmetric `denies` relation |

### Example Query — Neutrality Detection (CQ4)

```sparql
PREFIX : <http://www.semanticweb.org/skyrimontology/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?charLabel ?role
WHERE {
  ?char a :Character ;
        rdfs:label ?charLabel ;
        :hasRole ?role .
  FILTER NOT EXISTS { ?char :framesAs ?anyClaim }
}
```

**Expected result:** Jarl Balgruuf the Greater — his political neutrality is encoded as structured absence, not as a stated assertion.

---

## Non-Obvious Findings

The ontology reveals emergent knowledge not stated anywhere directly:

- **The Dragonborn as Cosmic Arbiter** — frames claims only in existential domains (moral, cosmological, vampiric), never territorial or political. Queryable via `ClaimType` filter.
- **Contested Evidence** — Auriel's Bow and the Elder Scroll are each cited by directly opposing claims simultaneously. The same artifact grounds both a liberation and a prevention argument.
- **Machine-Readable Neutrality** — Balgruuf's neutrality is a single `FILTER NOT EXISTS` query away. Structured absence is a valid knowledge representation technique.
- **Denial is Rare and Propagandistic** — Only the Talos pair uses `denies`, and both sides use it bidirectionally. This marks it as uniquely adversarial — active propaganda, not mere logical contradiction.

---

## Tools & Serialisation

- **Format:** RDF/OWL serialised in Turtle (`.ttl`)
- **Base IRI:** `http://www.semanticweb.org/skyrimontology/`
- **Reasoner compatible:** Any OWL 2 DL reasoner (e.g. HermiT, Pellet) will infer `hasOpposingHolder` automatically via the property chain axiom
- **SPARQL endpoint:** Load the `.ttl` into any triplestore (Apache Jena Fuseki, GraphDB, Stardog) to run the competency queries
- **Validation:** Open in [Protégé](https://protege.stanford.edu/) for class hierarchy browsing and reasoner activation

---

## Project Website

`index.html` is a fully self-contained interactive documentation site. Open it in any browser — no build step, no server required. It includes:

- Animated class diagram (SVG)
- All 8 dispute pairs with clickable claim metadata
- All 5 SPARQL competency questions with expected results
- SKOS hierarchy visualisation
- OWL axiom and property chain diagrams

---

## Data Sources

Ontology data drawn from the **[UESP Wiki](https://en.uesp.net/wiki/Skyrim)** under [CC BY-SA](https://creativecommons.org/licenses/by-sa/4.0/).  
*The Elder Scrolls V: Skyrim* © Bethesda Game Studios.

---

## Team

| Name | Role | GitHub |
|---|---|---|
| Atakan Kayı | Ontology Design & Knowledge Modelling | [@GrandTuvalet](https://github.com/GrandTuvalet) |
| Ceyda Uyar | SPARQL & Knowledge Extraction | [@yunglingwist](https://github.com/yunglingwist) |
| Yiğit Ak | Ontology Engineering & Web | [@yigittakk](https://github.com/yigittakk) |

---

*Knowledge Representation & Knowledge Extraction — University of Bologna*
