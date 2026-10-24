"""The paper's vocabulary parses, is complete, and holds its own source records.

Run: python -m unittest tests.test_ontology   (needs requirements.txt)

What this checks, in order:
  1. every .ttl and .jsonld under ontology/ parses;
  2. the vocabulary is rooted in the 561 Group root ontology and conforms to
     the root's own ontology-metadata shape;
  3. every skos:Concept has a prefLabel and a definition, sits in the scheme,
     and (for glossary concepts) agrees with the generated SKOS projection;
  4. each closed set (histories, juridical operations, evidence statuses,
     reading grades, legislative states) is exactly its owl:oneOf list;
  5. every record under data/records/ converts to RDF through
     ontology/records.context.jsonld and conforms to ontology/shapes.ttl;
  6. the shapes bite: deliberately broken copies of the records fail.

It judges the structure of records, not their numbers; test_reproduction.py
recomputes those.
"""

import copy
import json
import re
import unittest
from pathlib import Path

import pyshacl
from pyld import jsonld
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.collection import Collection
from rdflib.namespace import OWL, RDF, RDFS, SKOS, XSD

ROOT = Path(__file__).resolve().parent.parent
ONTOLOGY = ROOT / "ontology"
RECORDS = ROOT / "data" / "records"

WR = Namespace("https://561.group/knowledge/white-repopulation#")
NS = Namespace("https://561.group/ns/")
FIELD = "https://561.group/knowledge/white-repopulation/field#"
SOC = "https://561.group/knowledge/science-services-section/social-science-services-section/sociology-science-services-section/"
PAPER = URIRef("https://561.group/knowledge/white-repopulation")
RECORD_BASE = "https://561.group/knowledge/white-repopulation/record/"

# Where the root ontology lives for import resolution. The root is published
# by the Science knowledge-organization section; a pinned copy ships with the
# paper so the paper validates offline (see ontology/vendor/README).
ROOT_ONTOLOGY = ONTOLOGY / "vendor" / "561-ns-root.ttl"
ROOT_SHAPES = ONTOLOGY / "vendor" / "561-ns-root.shapes.ttl"

EXPECTED_KIND = {
    "2026-10-17-captive-birth-shares-source-series.json": WR.BirthReconstruction,
    "2026-10-17-antebellum-property-law-case-register.json": WR.CaseRegister,
    "2026-10-17-everett-directed-reproduction-case-extract.json": WR.TestimonyExtraction,
    "2026-10-17-virginia-racial-integrity-legislative-sequence.json": WR.LegislativeEventSequence,
    "us-net-migration-share-of-growth-1790-1860.json": WR.GrowthComponents,
    "white-increase-eugenic-selection-measurements-2026-10-17.json": WR.QuantitativeDocumentaryEvidence,
}


def load(path: Path, fmt: str = "turtle") -> Graph:
    graph = Graph()
    graph.parse(path, format=fmt)
    return graph


def record_graph(name: str, record: dict) -> Graph:
    """A record as RDF, through the JSON-LD context. Spec-compliant expansion (PyLD) because
    the context uses JSON-LD 1.1 scoped, type-scoped and nest features."""
    context = json.loads((ONTOLOGY / "records.context.jsonld").read_text(encoding="utf-8"))["@context"]
    stem = Path(name).stem
    document = {
        "@context": [context, {"@base": f"{RECORD_BASE}{stem}/"}],
        "@id": f"{RECORD_BASE}{stem}",
        **record,
    }
    nquads = jsonld.to_rdf(document, {"format": "application/n-quads"})
    graph = Graph()
    graph.parse(data=nquads, format="nquads")
    return graph


def merged(*graphs: Graph) -> Graph:
    out = Graph()
    for graph in graphs:
        for triple in graph:
            out.add(triple)
    return out


class Parsing(unittest.TestCase):
    def test_every_turtle_file_parses(self):
        files = sorted(ONTOLOGY.rglob("*.ttl"))
        self.assertGreaterEqual(len(files), 4, files)
        for path in files:
            with self.subTest(path=path.name):
                self.assertGreater(len(load(path)), 0)

    def test_every_jsonld_file_is_json_and_the_context_expands(self):
        files = sorted(ONTOLOGY.glob("*.jsonld"))
        self.assertEqual({p.name for p in files}, {"records.context.jsonld", "white-repopulation.skos.jsonld"})
        for path in files:
            with self.subTest(path=path.name):
                self.assertIsInstance(json.loads(path.read_text(encoding="utf-8")), dict)


class Rooting(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.vocab = load(ONTOLOGY / "white-repopulation.ttl")
        cls.root = load(ROOT_ONTOLOGY)

    def test_vocabulary_is_an_ontology_with_the_expected_metadata(self):
        g = self.vocab
        self.assertIn((PAPER, RDF.type, OWL.Ontology), g)
        self.assertIn((PAPER, OWL.versionIRI, URIRef(f"{PAPER}/0.2.0")), g)
        self.assertIn((PAPER, OWL.imports, URIRef(str(NS))), g)
        self.assertIn((PAPER, URIRef("http://purl.org/dc/terms/license"), URIRef("https://creativecommons.org/licenses/by/4.0/")), g)
        version = re.search(r"^version:\s*(\S+)", (ROOT / "paper.yaml").read_text(encoding="utf-8"), re.M).group(1)
        self.assertEqual(str(g.value(PAPER, OWL.versionInfo)), version)

    def test_root_declares_the_namespace_the_vocabulary_imports(self):
        self.assertIn((URIRef(str(NS)), RDF.type, OWL.Ontology), self.root)
        self.assertIn((NS.Record, RDF.type, OWL.Class), self.root)

    def test_vocabulary_and_root_conform_to_the_root_ontology_shapes(self):
        shapes = load(ROOT_SHAPES)
        for name, graph in (("vocabulary", self.vocab), ("root", self.root), ("record shapes", load(ONTOLOGY / "shapes.ttl"))):
            with self.subTest(graph=name):
                conforms, _, text = pyshacl.validate(merged(graph, self.root), shacl_graph=shapes, inference="none")
                self.assertTrue(conforms, text)

    def test_every_record_kind_is_a_subclass_of_the_root_record(self):
        g = merged(self.vocab, self.root)
        for kind in EXPECTED_KIND.values():
            with self.subTest(kind=kind):
                self.assertIn(NS.Record, set(g.transitive_objects(kind, RDFS.subClassOf)))

    def test_every_wr_class_and_property_is_documented(self):
        g = self.vocab
        declared = {
            s for t in (OWL.Class, OWL.ObjectProperty, OWL.DatatypeProperty)
            for s in g.subjects(RDF.type, t) if str(s).startswith(str(WR))
        }
        self.assertGreater(len(declared), 60)
        undocumented = [s for s in declared if not (g.value(s, RDFS.comment) or g.value(s, RDFS.label))]
        self.assertEqual(undocumented, [])


class Concepts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.vocab = load(ONTOLOGY / "white-repopulation.ttl")
        cls.skos = json.loads((ONTOLOGY / "white-repopulation.skos.jsonld").read_text(encoding="utf-8"))
        cls.scheme = WR.terms

    def concepts(self):
        return sorted(self.vocab.subjects(RDF.type, SKOS.Concept))

    def test_scheme_exists_and_has_top_concepts(self):
        self.assertIn((self.scheme, RDF.type, SKOS.ConceptScheme), self.vocab)
        self.assertGreaterEqual(len(list(self.vocab.objects(self.scheme, SKOS.hasTopConcept))), 5)

    def test_every_concept_has_a_label_and_a_definition_and_is_in_the_scheme(self):
        concepts = self.concepts()
        self.assertEqual(len(concepts), 38)  # 21 glossary terms, 4 histories, 4 operations, 3 statuses, 4 grades, 2 design concepts
        for concept in concepts:
            with self.subTest(concept=str(concept)):
                self.assertTrue(list(self.vocab.objects(concept, SKOS.prefLabel)), "no skos:prefLabel")
                definition = list(self.vocab.objects(concept, SKOS.definition))
                self.assertTrue(definition and all(str(d).strip() for d in definition), "no skos:definition")
                self.assertIn((concept, SKOS.inScheme, self.scheme), self.vocab)

    def test_collections_have_labels_and_definitions_and_members_in_scheme(self):
        for collection in self.vocab.subjects(RDF.type, SKOS.Collection):
            with self.subTest(collection=str(collection)):
                self.assertTrue(list(self.vocab.objects(collection, SKOS.prefLabel)))
                self.assertTrue(list(self.vocab.objects(collection, SKOS.definition)))
                members = list(self.vocab.objects(collection, SKOS.member))
                self.assertGreaterEqual(len(members), 3)
                for member in members:
                    self.assertIn((member, SKOS.inScheme, self.scheme), self.vocab)

    def test_no_concept_is_also_a_collection(self):  # SKOS: Concept and Collection are disjoint
        both = set(self.vocab.subjects(RDF.type, SKOS.Concept)) & set(self.vocab.subjects(RDF.type, SKOS.Collection))
        self.assertEqual(both, set())

    def test_glossary_concepts_keep_their_house_iris_and_trace_to_a_pinned_source(self):
        glossary = [c for c in self.concepts() if str(c).startswith(SOC)]
        self.assertEqual(len(glossary), 21)
        for concept in glossary:
            with self.subTest(concept=str(concept)):
                sources = [str(o) for o in self.vocab.objects(concept, URIRef("http://purl.org/dc/terms/source"))]
                self.assertEqual(len(sources), 1)
                self.assertRegex(sources[0], r"^https://github\.com/lenticule-science/science-services-section/blob/[0-9a-f]{40}/.+/glossary/terms/[a-z0-9-]+\.md$")
                derived = [str(o) for o in self.vocab.objects(concept, URIRef("http://www.w3.org/ns/prov#wasDerivedFrom"))]
                self.assertEqual(len(derived), 1)
                self.assertRegex(derived[0], r"^swh:1:cnt:[0-9a-f]{40}$")

    def test_all_glossary_sources_are_at_one_pinned_commit(self):
        commits = {
            re.search(r"/blob/([0-9a-f]{40})/", str(o)).group(1)
            for c in self.concepts() if str(c).startswith(SOC)
            for o in self.vocab.objects(c, URIRef("http://purl.org/dc/terms/source"))
        }
        self.assertEqual(len(commits), 1, commits)

    def test_skos_projection_agrees_with_the_vocabulary(self):
        by_id = {node["@id"]: node for node in self.skos["@graph"]}
        glossary = [c for c in self.concepts() if str(c).startswith(SOC)]
        for concept in glossary:
            with self.subTest(concept=str(concept)):
                node = by_id.get(str(concept))
                self.assertIsNotNone(node, "concept missing from the SKOS projection")
                self.assertEqual(node["skos:prefLabel"], str(self.vocab.value(concept, SKOS.prefLabel)))
                self.assertEqual(node["skos:notation"], str(self.vocab.value(concept, SKOS.notation)))
                # the vocabulary's definition is the opening of the projection's full-body definition
                opening = str(self.vocab.value(concept, SKOS.definition))
                self.assertTrue(node["skos:definition"].startswith(opening[:80]), "definition drifted from the projection")
                related = {r["@id"] for r in node.get("skos:related", [])}
                # every glossary-derived edge is in the vocabulary; the vocabulary adds the paper's own edges to its coined concepts
                self.assertLessEqual(related, {str(o) for o in self.vocab.objects(concept, SKOS.related)})
        self.assertEqual(self.skos["accounting"]["concepts"], len(glossary))

    def test_related_edges_are_symmetric_and_land_in_the_scheme(self):
        for a, b in self.vocab.subject_objects(SKOS.related):
            self.assertIn((b, SKOS.related, a), self.vocab, f"{a} related {b} is not symmetric")
            self.assertIn((b, SKOS.inScheme, self.scheme), self.vocab)


class ClosedSets(unittest.TestCase):
    """Each closed set is exactly the owl:oneOf list of its class, and no other individual claims membership."""

    SETS = {
        WR.History: 4,
        WR.JuridicalOperation: 4,
        WR.EvidenceStatus: 3,
        WR.ReadingGrade: 4,
        WR.LegislativeState: 3,
    }

    def test_enumerations_match_instances(self):
        g = load(ONTOLOGY / "white-repopulation.ttl")
        for cls, size in self.SETS.items():
            with self.subTest(cls=str(cls)):
                enumerated = set()
                for equivalent in g.objects(cls, OWL.equivalentClass):
                    for one_of in g.objects(equivalent, OWL.oneOf):
                        enumerated |= set(Collection(g, one_of))
                self.assertEqual(len(enumerated), size)
                self.assertEqual(set(g.subjects(RDF.type, cls)), enumerated)

    def test_the_three_evidence_statuses_are_the_papers(self):
        g = load(ONTOLOGY / "white-repopulation.ttl")
        labels = {str(g.value(s, SKOS.prefLabel)) for s in g.subjects(RDF.type, WR.EvidenceStatus)}
        self.assertEqual(labels, {"observed", "mechanistically plausible", "not established"})


class Records(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ontology = merged(load(ONTOLOGY / "white-repopulation.ttl"), load(ROOT_ONTOLOGY))
        cls.shapes = load(ONTOLOGY / "shapes.ttl")
        cls.files = sorted(RECORDS.glob("*.json"))

    def validate(self, graph: Graph):
        return pyshacl.validate(graph, shacl_graph=self.shapes, ont_graph=self.ontology, inference="none")

    def test_every_record_file_has_a_kind(self):
        self.assertEqual({p.name for p in self.files}, set(EXPECTED_KIND))

    def test_every_record_converts_with_no_unmapped_key(self):
        for path in self.files:
            with self.subTest(record=path.name):
                graph = record_graph(path.name, json.loads(path.read_text(encoding="utf-8")))
                unmapped = sorted({str(p) for p in graph.predicates() if str(p).startswith(FIELD)})
                self.assertEqual(unmapped, [], "JSON keys the context does not map")
                top = URIRef(f"{RECORD_BASE}{path.stem}")
                self.assertIn((top, RDF.type, EXPECTED_KIND[path.name]), graph)
                types = set(graph.objects(top, RDF.type))
                self.assertTrue(all(str(t).startswith(str(WR)) for t in types), types)

    def test_every_record_conforms_to_its_shape(self):
        for path in self.files:
            with self.subTest(record=path.name):
                graph = record_graph(path.name, json.loads(path.read_text(encoding="utf-8")))
                conforms, _, text = self.validate(graph)
                self.assertTrue(conforms, text)

    def test_case_kinds_are_subclasses_of_case_record(self):
        graph = record_graph("2026-10-17-antebellum-property-law-case-register.json",
                             json.loads((RECORDS / "2026-10-17-antebellum-property-law-case-register.json").read_text(encoding="utf-8")))
        cases = list(graph.objects(None, WR.hasCase))
        self.assertEqual(len(cases), 7)
        kinds = {t for c in cases for t in graph.objects(c, RDF.type)}
        self.assertEqual(kinds, {WR.JudicialOpinion, WR.FreedomPetitionOpinion, WR.SecondaryExtractedOpinion, WR.EnslaverCorrespondence})


class ShapesBite(unittest.TestCase):
    """Broken copies of the real records must fail, so a green run means something."""

    @classmethod
    def setUpClass(cls):
        cls.ontology = merged(load(ONTOLOGY / "white-repopulation.ttl"), load(ROOT_ONTOLOGY))
        cls.shapes = load(ONTOLOGY / "shapes.ttl")

    def record(self, name):
        return json.loads((RECORDS / name).read_text(encoding="utf-8"))

    def conforms(self, name, record):
        graph = record_graph(name, record)
        return pyshacl.validate(graph, shacl_graph=self.shapes, ont_graph=self.ontology, inference="none")[0]

    def assertBreaks(self, name, mutate):
        broken = copy.deepcopy(self.record(name))
        mutate(broken)
        self.assertFalse(self.conforms(name, broken))

    def test_unmodified_records_pass_the_same_path(self):
        for name in EXPECTED_KIND:
            with self.subTest(record=name):
                self.assertTrue(self.conforms(name, self.record(name)))

    def test_birth_reconstruction_without_limitations_fails(self):
        self.assertBreaks("2026-10-17-captive-birth-shares-source-series.json", lambda r: r.pop("limitations"))

    def test_birth_reconstruction_without_a_sensitivity_fails(self):
        self.assertBreaks("2026-10-17-captive-birth-shares-source-series.json", lambda r: r.update(sensitivities=[]))

    def test_birth_share_over_one_hundred_fails(self):
        self.assertBreaks("2026-10-17-captive-birth-shares-source-series.json",
                          lambda r: r["sensitivities"][0].update(share_1790_1849_pct=117.37))

    def test_case_register_claiming_a_known_universe_fails(self):
        self.assertBreaks("2026-10-17-antebellum-property-law-case-register.json",
                          lambda r: r.update(universe_not_ascertained=False))

    def test_case_without_read_status_fails(self):
        self.assertBreaks("2026-10-17-antebellum-property-law-case-register.json",
                          lambda r: r["records"][0].pop("read_status"))

    def test_case_with_an_unknown_kind_is_caught_by_the_context_check(self):
        broken = copy.deepcopy(self.record("2026-10-17-antebellum-property-law-case-register.json"))
        broken["records"][0]["kind"] = "judicial-memo"
        graph = record_graph("x.json", broken)
        self.assertTrue(any(str(o).startswith(FIELD) for o in graph.objects(None, RDF.type)))

    def test_testimony_observation_without_a_validity_bound_fails(self):
        self.assertBreaks("2026-10-17-everett-directed-reproduction-case-extract.json",
                          lambda r: r["observations"][0].pop("not_valid_for"))

    def test_testimony_without_unmeasured_fails(self):
        self.assertBreaks("2026-10-17-everett-directed-reproduction-case-extract.json", lambda r: r.pop("unmeasured"))

    def test_postponed_bill_without_a_later_disposition_fails(self):
        def mutate(r):
            r["events"][2].pop("later_disposition")
        self.assertBreaks("2026-10-17-virginia-racial-integrity-legislative-sequence.json", mutate)

    def test_unknown_legislative_state_fails(self):
        def mutate(r):
            r["events"][0]["state"] = "repealed"
        self.assertBreaks("2026-10-17-virginia-racial-integrity-legislative-sequence.json", mutate)

    def test_growth_interval_running_backwards_fails(self):
        def mutate(r):
            r["intervals"][0].update(start_year=1810, end_year=1800)
        self.assertBreaks("us-net-migration-share-of-growth-1790-1860.json", mutate)

    def test_growth_without_forbidden_inferences_fails(self):
        self.assertBreaks("us-net-migration-share-of-growth-1790-1860.json", lambda r: r.pop("forbidden_inferences"))

    def test_measurement_with_an_impossible_percentage_fails(self):
        def mutate(r):
            r["computed_statistics"]["nc_share_classified_white_cumulative_pct"] = 161.568
        self.assertBreaks("white-increase-eugenic-selection-measurements-2026-10-17.json", mutate)

    def test_measurement_whose_parts_do_not_sum_to_the_total_fails(self):
        def mutate(r):
            r["raw_counts"]["nc_cumulative"]["white"] = 4000
        self.assertBreaks("white-increase-eugenic-selection-measurements-2026-10-17.json", mutate)

    def test_measurement_without_its_not_pooled_list_fails(self):
        self.assertBreaks("white-increase-eugenic-selection-measurements-2026-10-17.json", lambda r: r.pop("not_pooled"))


if __name__ == "__main__":
    unittest.main()
