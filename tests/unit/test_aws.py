import copy
import hashlib
import json
import unittest
from unittest.mock import patch

from tests.support import pair_text, synthetic_pair
from secret_history.baselines.aws_rules import AWS_EXAMPLE, classify_aws
from secret_history.candidates.aws import extract_aws
from secret_history.reporting.report import candidate_record, fingerprint


class AwsRulesTests(unittest.TestCase):
    def decision(self, text: str):
        candidates, warnings = extract_aws(text)
        self.assertFalse(warnings)
        self.assertEqual(len(candidates), 1)
        return classify_aws(candidates[0])

    def test_literal_pair_quotes_export_and_comments(self):
        identifier, secret = synthetic_pair()
        text = f' export AWS_ACCESS_KEY_ID = "{identifier}" # account\nAWS_SECRET_ACCESS_KEY=\'{secret}\'\n'
        self.assertEqual(self.decision(text).status, "SUSPECTED_SECRET")

    def test_placeholders_empty_and_environment_references(self):
        for identifier, secret in (("", ""), ("your_access_key_here", "your_secret_key_here"),
                                   ("${ACCESS_ID}", "$SECRET_VALUE")):
            with self.subTest(identifier=identifier):
                self.assertEqual(self.decision(f"AWS_ACCESS_KEY_ID={identifier}\nAWS_SECRET_ACCESS_KEY={secret}").status, "NON_SECRET")

    def test_exact_public_example(self):
        identifier, secret = AWS_EXAMPLE
        self.assertEqual(self.decision(f"AWS_ACCESS_KEY_ID={identifier}\nAWS_SECRET_ACCESS_KEY={secret}").reason,
                         "exact_aws_documentation_example")

    def test_example_word_is_not_an_allowlist(self):
        _, secret = synthetic_pair()
        self.assertEqual(self.decision(f"AWS_ACCESS_KEY_ID={AWS_EXAMPLE[0]}\nAWS_SECRET_ACCESS_KEY={secret}").status,
                         "SUSPECTED_SECRET")

    def test_single_id_is_incomplete(self):
        identifier, _ = synthetic_pair()
        self.assertEqual(self.decision(f"AWS_ACCESS_KEY_ID={identifier}").status, "INCOMPLETE")

    def test_single_secret_is_retained(self):
        _, secret = synthetic_pair()
        self.assertEqual(self.decision(f"AWS_SECRET_ACCESS_KEY={secret}").status, "SUSPECTED_SECRET")

    def test_realistic_secret_with_empty_id_is_retained(self):
        _, secret = synthetic_pair()
        self.assertEqual(self.decision(f"AWS_ACCESS_KEY_ID=\nAWS_SECRET_ACCESS_KEY={secret}").status, "SUSPECTED_SECRET")

    def test_empty_secret_with_literal_id_is_incomplete(self):
        identifier, _ = synthetic_pair()
        self.assertEqual(self.decision(f"AWS_ACCESS_KEY_ID={identifier}\nAWS_SECRET_ACCESS_KEY=").status, "INCOMPLETE")

    def test_duplicate_fields_are_not_arbitrarily_paired(self):
        candidates, warnings = extract_aws(pair_text() + pair_text("second"))
        self.assertFalse(warnings)
        self.assertEqual(len(candidates), 4)
        self.assertTrue(all(c.kind == "aws_component" and classify_aws(c).status == "UNCERTAIN" for c in candidates))

    def test_comments_do_not_hide_a_pair(self):
        commented = "\n".join("# " + line for line in pair_text().splitlines())
        self.assertEqual(self.decision(commented).status, "SUSPECTED_SECRET")

    def test_mixed_comment_and_active_assignment_is_uncertain(self):
        self.assertEqual(self.decision("# " + pair_text()).status, "UNCERTAIN")

    def test_malformed_assignment_reports_coverage_warning(self):
        candidates, warnings = extract_aws(pair_text() + 'AWS_SECRET_ACCESS_KEY="unclosed')
        self.assertEqual(warnings[0].line, 3)
        self.assertTrue(all(classify_aws(c).status == "UNCERTAIN" for c in candidates))

    def test_unexpected_format_is_not_silently_dropped(self):
        self.assertEqual(self.decision("AWS_SECRET_ACCESS_KEY=short").status, "UNCERTAIN")

    def test_temporary_credentials_are_not_treated_as_full_pair(self):
        self.assertEqual(self.decision(pair_text().replace("AKIA", "ASIA")).reason, "temporary_credentials_out_of_scope")

    def test_raw_values_and_context_are_not_serialized(self):
        identifier, secret = synthetic_pair("test-pair")
        candidates, _ = extract_aws(pair_text() + "# another secret must never be exported")
        candidate = candidates[0]
        record = candidate_record(candidate, classify_aws(candidate), ".env", "a" * 40)
        rendered = repr(record)
        self.assertNotIn(identifier, rendered)
        self.assertNotIn(secret, rendered)
        self.assertNotIn("another secret", rendered)
        self.assertNotIn(secret, repr(candidate))
        self.assertNotIn("ground_truth", record)
        self.assertEqual(record["activity_status"], "UNKNOWN")


class FingerprintTests(unittest.TestCase):
    def record(self, text=None):
        candidates, _ = extract_aws(pair_text() if text is None else text)
        candidate = candidates[0]
        return candidate_record(candidate, classify_aws(candidate), "config/.env", "a" * 40)

    def test_hash_input_has_location_and_masked_values_only(self):
        text = pair_text()
        with patch("secret_history.reporting.report.hashlib.sha256", wraps=hashlib.sha256) as sha256:
            record = self.record(text)
        self.assertEqual(sha256.call_count, 1)
        payload = sha256.call_args.args[0]
        fields = json.loads(payload)
        self.assertEqual(set(fields), {"scheme", "path", "commit_oid", "line_start", "line_end", "components"})
        self.assertEqual(fields["path"], record["path"])
        self.assertEqual(fields["commit_oid"], record["commit_oid"])
        self.assertEqual([item["masked_value"] for item in fields["components"]], ["[REDACTED]", "[REDACTED]"])
        self.assertEqual((fields["line_start"], fields["line_end"]), (1, 2))
        for value in synthetic_pair("test-pair"):
            self.assertNotIn(value.encode(), payload)

    def test_coordinate_and_mask_changes_affect_fingerprint(self):
        original = self.record()
        variations = []
        for key, value in (("path", "other/.env"), ("commit_oid", "b" * 40), ("line_start", 3), ("line_end", 4)):
            updated = copy.deepcopy(original)
            updated[key] = value
            variations.append(updated)
        updated = copy.deepcopy(original)
        updated["components"][0]["masked_value"] = "[EMPTY]"
        variations.append(updated)
        updated = copy.deepcopy(original)
        updated["components"][0]["line"] = 3
        variations.append(updated)
        fingerprints = [fingerprint(record) for record in [original, *variations]]
        self.assertEqual(len(set(fingerprints)), len(fingerprints))

    def test_value_changes_and_component_order_do_not_affect_masked_identity(self):
        original = self.record()
        changed_value = self.record(pair_text("different-synthetic-value"))
        self.assertEqual(original["fingerprint"], changed_value["fingerprint"])
        reordered = copy.deepcopy(original)
        reordered["components"].reverse()
        reordered["status"] = "UNCERTAIN"
        reordered["features"] = {}
        self.assertEqual(original["fingerprint"], fingerprint(reordered))

    def test_unmasked_component_is_rejected(self):
        record = self.record()
        record["components"][0]["masked_value"] = "unmasked-synthetic-value"
        with self.assertRaisesRegex(ValueError, "fully masked"):
            fingerprint(record)


if __name__ == "__main__":
    unittest.main()
